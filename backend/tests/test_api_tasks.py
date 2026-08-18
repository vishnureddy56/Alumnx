import pytest
from fastapi.testclient import TestClient
from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_users_endpoint():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "team" in data
    assert len(data["team"]) == 6
    user_ids = [u["user_id"] for u in data["team"]]
    assert "u_aarti" in user_ids
    assert "u_rohit" in user_ids
    assert "u_meera" in user_ids
    assert "u_karan" in user_ids
    assert "u_divya" in user_ids
    assert "u_triage" in user_ids


def test_create_task_success():
    payload = {
        "candidate_id": "vishnureddynandyala1234@gmail.com",
        "source_email_id": "em_test_001",
        "thread_id": "th_test_001",
        "title": "RFP — Enterprise DMS for Meridian Steel",
        "description": "Meridian Steel has issued an RFP for a document management system. Submission due 12 Aug 2026.",
        "assignee_id": "u_aarti",
        "category": "enterprise_rfp",
        "priority": "high",
        "due_date": "2026-08-12",
        "deal_value_inr": 2500000,
        "company_name": "Meridian Steel Pvt Ltd",
        "confidence": 0.91
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["candidate_id"] == "vishnureddynandyala1234@gmail.com"
    assert data["source_email_id"] == "em_test_001"
    assert "created_at" in data


def test_create_task_invalid_assignee_enum():
    payload = {
        "candidate_id": "vishnureddynandyala1234@gmail.com",
        "source_email_id": "em_test_002",
        "thread_id": "th_test_002",
        "title": "Invalid Assignee Test",
        "assignee_id": "Aarti",  # Bad enum value
        "category": "enterprise_rfp",
        "priority": "high",
        "due_date": "2026-08-12",
        "deal_value_inr": 2500000,
        "company_name": "Meridian Steel Pvt Ltd",
        "confidence": 0.91
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_enum_value"
    assert data["field"] == "assignee_id"
    assert data["received"] == "Aarti"
    assert "u_aarti" in data["allowed"]


def test_create_task_invalid_category_enum():
    payload = {
        "candidate_id": "vishnureddynandyala1234@gmail.com",
        "source_email_id": "em_test_003",
        "thread_id": "th_test_003",
        "title": "Invalid Category Test",
        "assignee_id": "u_rohit",
        "category": "sales_smb",  # Invalid category enum
        "priority": "low",
        "confidence": 0.8
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_enum_value"
    assert data["field"] == "category"
    assert "enterprise_rfp" in data["allowed"]


def test_list_tasks_mandatory_candidate_id():
    # Without candidate_id parameter
    response = client.get("/tasks")
    assert response.status_code in [400, 422]


def test_list_tasks_with_candidate_id():
    response = client.get("/tasks?candidate_id=vishnureddynandyala1234@gmail.com")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_patch_task():
    # Create a task first
    payload = {
        "candidate_id": "vishnureddynandyala1234@gmail.com",
        "source_email_id": "em_test_patch",
        "thread_id": "th_test_patch",
        "title": "Initial Title",
        "assignee_id": "u_rohit",
        "category": "smb_enquiry",
        "priority": "low",
        "confidence": 0.8
    }
    create_resp = client.post("/tasks", json=payload)
    task_id = create_resp.json()["task_id"]

    patch_payload = {
        "priority": "high",
        "deal_value_inr": 3200000,
        "due_date": "2026-08-11"
    }
    patch_resp = client.patch(f"/tasks/{task_id}", json=patch_payload)
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()
    assert updated_data["priority"] == "high"
    assert updated_data["deal_value_inr"] == 3200000
    assert updated_data["due_date"] == "2026-08-11"
