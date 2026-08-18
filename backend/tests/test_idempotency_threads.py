import json
import uuid
import pytest
from fastapi.testclient import TestClient
from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_runs_simulation_idempotency_and_thread_reconciliation():
    candidate_id = f"evaluator.grader.{uuid.uuid4().hex[:6]}@test.com"

    # RUN 1: Fresh Batch of Emails
    batch_1 = [
        {
            "email_id": "em_run1_001",
            "thread_id": "th_run1_001",
            "message_index": 0,
            "from_name": "Suresh Kulkarni",
            "from_email": "s.kulkarni@meridiansteel.co.in",
            "subject": "RFP - Enterprise DMS",
            "body": "Meridian Steel invites proposals for an enterprise DMS. Indicative budget is Rs. 25 lakhs. Proposals must reach us by 12th August 2026.",
            "received_at": "2026-08-01T09:14:22+05:30",
            "is_reply": False
        },
        {
            "email_id": "em_run1_002",
            "thread_id": "th_run1_002",
            "message_index": 0,
            "from_name": "Ankit Bose",
            "from_email": "ankit@railyardlogistics.in",
            "subject": "Quick demo request",
            "body": "Hi, we're a 30-person startup, can we get a demo next week? Nothing urgent.",
            "received_at": "2026-08-01T11:02:10+05:30",
            "is_reply": False
        },
        {
            "email_id": "em_run1_003",
            "thread_id": "th_run1_003",
            "message_index": 0,
            "from_name": "Raghav Sharma",
            "from_email": "raghav@northbridge.in",
            "subject": "Automatic reply: Out of Office",
            "body": "I am out of office until 14th August. — Sent from Outlook",
            "received_at": "2026-08-03T08:00:00+05:30",
            "is_reply": False
        }
    ]

    ingest_resp_1 = client.post("/ingest", json={"candidate_id": candidate_id, "emails": batch_1})
    assert ingest_resp_1.status_code == 200
    res_data_1 = ingest_resp_1.json()
    assert res_data_1["processed"] == 3
    assert res_data_1["tasks_created"] == 2  # 2 tasks created, 1 skipped (OOO)
    assert res_data_1["skipped"] == 1

    # Check Task count after Run 1
    tasks_resp_1 = client.get(f"/tasks?candidate_id={candidate_id}")
    assert tasks_resp_1.status_code == 200
    tasks_run1 = tasks_resp_1.json()
    assert len(tasks_run1) == 2

    # RUN 2: Post the IDENTICAL batch again (Idempotency Test)
    ingest_resp_2 = client.post("/ingest", json={"candidate_id": candidate_id, "emails": batch_1})
    assert ingest_resp_2.status_code == 200
    res_data_2 = ingest_resp_2.json()
    assert res_data_2["tasks_created"] == 0  # No new tasks created!

    # Verify task count unchanged
    tasks_resp_2 = client.get(f"/tasks?candidate_id={candidate_id}")
    assert tasks_resp_2.status_code == 200
    tasks_run2 = tasks_resp_2.json()
    assert len(tasks_run2) == 2

    # RUN 3: Post a second batch containing a thread reply on Run 1's thread
    batch_3 = [
        {
            "email_id": "em_run3_001",
            "thread_id": "th_run1_001",  # Same thread as Run 1
            "message_index": 1,
            "from_name": "Suresh Kulkarni",
            "from_email": "s.kulkarni@meridiansteel.co.in",
            "subject": "Re: RFP - Enterprise DMS",
            "body": "Correction: budget increased to Rs. 32 lakhs, deadline advanced to 11th August.",
            "received_at": "2026-08-09T10:00:00+05:30",
            "is_reply": True
        },
        {
            "email_id": "em_run3_002",
            "thread_id": "th_run3_new",  # Brand new thread
            "message_index": 0,
            "from_name": "Tariq Mansoor",
            "from_email": "tariq@zenithcloudpartners.com",
            "subject": "Partnership integration",
            "body": "We'd like to explore a tech integration partnership.",
            "received_at": "2026-08-04T12:00:00+05:30",
            "is_reply": False
        }
    ]

    ingest_resp_3 = client.post("/ingest", json={"candidate_id": candidate_id, "emails": batch_3})
    assert ingest_resp_3.status_code == 200
    res_data_3 = ingest_resp_3.json()
    assert res_data_3["tasks_updated"] == 1  # th_run1_001 updated
    assert res_data_3["tasks_created"] == 1  # th_run3_new created

    # Verify total task count is now 3 (2 from run 1 + 1 new from run 3)
    tasks_resp_3 = client.get(f"/tasks?candidate_id={candidate_id}")
    assert tasks_resp_3.status_code == 200
    tasks_run3 = tasks_resp_3.json()
    assert len(tasks_run3) == 3

    # Verify that the updated task on th_run1_001 has budget 3200000 and priority high
    th1_task = next(t for t in tasks_run3 if t["thread_id"] == "th_run1_001")
    assert th1_task["deal_value_inr"] == 3200000
    assert th1_task["due_date"] == "2026-08-11"
    assert th1_task["priority"] == "high"
