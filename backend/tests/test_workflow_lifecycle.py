import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed_data import seed_all_data

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["platform"] == "ResQFlow AI"

def test_nlp_extraction_endpoint():
    response = client.post("/api/requests/parse-nlp", json={
        "text": "Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["extracted_location"] == "Village A"
    assert data["affected_people"] == 350
    assert data["vulnerable_elderly"] == 40
    assert data["vulnerable_children"] == 25

def test_explain_priority_and_override():
    # Village A request ID
    response = client.get("/api/requests")
    assert response.status_code == 200
    requests = response.json()
    village_a = next((r for r in requests if r["location_name"] == "Village A"), None)
    assert village_a is not None

    p_resp = client.get(f"/api/requests/{village_a['id']}/priority")
    assert p_resp.status_code == 200
    assert p_resp.json()["priority_score"] >= 80.0

def test_resource_matching_and_approval():
    response = client.get("/api/requests")
    village_a = next(r for r in response.json() if r["location_name"] == "Village A")
    
    # Recommendation
    rec_resp = client.get(f"/api/allocations/recommend/{village_a['id']}")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert len(rec_data["recommendations"]) > 0

    # Approval
    alloc_resp = client.post("/api/allocations/approve", json={
        "request_id": village_a["id"],
        "warehouse_id": rec_data["recommendations"][0]["warehouse_id"],
        "items": [
            {
                "category": "Drinking Water",
                "item_name": "Drinking Water",
                "allocated_quantity": 2000.0,
                "unit": "L"
            }
        ],
        "override_notes": "Immediate priority authorization for stranded population"
    })
    assert alloc_resp.status_code == 200
    assert alloc_resp.json()["status"] in ["APPROVED", "DELIVERED"]

def test_trace_relief_package():
    # Trace the signature relief package
    resp = client.get("/api/donations/RELIEF-2026-00482/trace")
    assert resp.status_code == 200
    data = resp.json()
    assert data["relief_id"] == "RELIEF-2026-00482"
    assert len(data["timeline"]) == 8

def test_audit_integrity_verification():
    resp = client.get("/api/audit/verify-integrity")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_chain_valid"] is True
    assert data["total_records"] > 0
