import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_CANDIDATE_ID = f"chat_test_{uuid.uuid4().hex[:6]}@test.com"


@pytest.fixture(scope="module", autouse=True)
def setup_chat_test_data():
    candidate_id = TEST_CANDIDATE_ID
    batch = [
        # 1. Enterprise RFP with deal value
        {
            "email_id": "em_chat_01",
            "thread_id": "th_chat_01",
            "message_index": 0,
            "from_name": "Suresh Kulkarni",
            "from_email": "suresh@meridian.com",
            "subject": "RFP for DMS System",
            "body": "Meridian Steel invites proposals for enterprise DMS. Budget Rs. 25 lakhs. Due 12th August 2026.",
            "received_at": "2026-08-01T09:00:00+05:30",
            "is_reply": False
        },
        # 2. Marketing Sponsorship
        {
            "email_id": "em_chat_02",
            "thread_id": "th_chat_02",
            "message_index": 0,
            "from_name": "Nandita Reddy",
            "from_email": "nandita@summit.in",
            "subject": "Keynote Sponsorship",
            "body": "Gold sponsorship ₹4,00,000 for SaaS summit. Need confirmation tomorrow EOD.",
            "received_at": "2026-08-02T16:00:00+05:30",
            "is_reply": False
        },
        # 3. Unsolicited Vendor Spam (Lookalike marketing)
        {
            "email_id": "em_chat_03",
            "thread_id": "th_chat_03",
            "message_index": 0,
            "from_name": "Alex Growth",
            "from_email": "alex@rankboosters.io",
            "subject": "Boost organic traffic with PR outreach",
            "body": "We've helped 200+ SaaS companies 3x traffic with content marketing and webinar promotion. Free audit attached.",
            "received_at": "2026-08-04T15:00:00+05:30",
            "is_reply": False
        },
        # 4. Triage Ambiguous item
        {
            "email_id": "em_chat_04",
            "thread_id": "th_chat_04",
            "message_index": 0,
            "from_name": "Farhan Qureshi",
            "from_email": "farhan@halcyon.com",
            "subject": "Two asks - platform and webinar",
            "body": "Two things: (1) evaluate platform budget TBD, and (2) co-host webinar in Sept.",
            "received_at": "2026-08-05T14:00:00+05:30",
            "is_reply": False
        },
        # 5. Alliances
        {
            "email_id": "em_chat_05",
            "thread_id": "th_chat_05",
            "message_index": 0,
            "from_name": "Tariq Mansoor",
            "from_email": "tariq@zenith.com",
            "subject": "Partnership inquiry",
            "body": "We'd like to explore reselling your platform.",
            "received_at": "2026-08-04T12:00:00+05:30",
            "is_reply": False
        }
    ]
    client.post("/ingest", json={"candidate_id": candidate_id, "emails": batch})


def test_chat_query_1_rfp_count():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "How many emails this batch were proposal or RFP related?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "enterprise_rfp" in data["supporting_data"]
    assert data["supporting_data"]["enterprise_rfp"] >= 1
    assert "enterprise_rfp" in data["answer"] or "proposal" in data["answer"]


def test_chat_query_2_marketing_vs_spam():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "How many were marketing versus actual spam we correctly ignored?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "marketing" in data["supporting_data"]
    assert "skipped_marketing_lookalike_spam" in data["supporting_data"]
    assert data["supporting_data"]["marketing"] >= 1
    assert data["supporting_data"]["skipped_marketing_lookalike_spam"] >= 1


def test_chat_query_3_triage_and_why():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "Show me everything sitting in triage and why."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "triage_count" in data["supporting_data"]
    assert "triage_task_ids" in data["supporting_data"]
    assert data["supporting_data"]["triage_count"] >= 1


def test_chat_query_4_spurious_rate():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "What's our spurious rate so far?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "spurious_rate" in data["supporting_data"]
    assert "processed" in data["supporting_data"]
    assert data["supporting_data"]["processed"] >= 5


def test_chat_query_6_alliances_reseller_breakdown():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "How many alliances emails came from resellers versus tech integration partners?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "alliances" in data["supporting_data"]
    # Answer must caveat that sub-breakdown is not stored in schema
    assert "alliances" in data["answer"].lower()


def test_chat_query_7_zero_match_trap():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "How many emails were about GST refunds?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["supporting_data"]["gst_refund_count"] == 0
    assert "0" in data["answer"] or "zero" in data["answer"].lower()


def test_chat_query_8_out_of_scope_action_trap():
    resp = client.post("/api/chat", json={
        "candidate_id": TEST_CANDIDATE_ID,
        "query": "Send Aarti an email about the Meridian Steel RFP."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["supporting_data"] == {}
    assert "cannot" in data["answer"].lower() or "informational" in data["answer"].lower()
