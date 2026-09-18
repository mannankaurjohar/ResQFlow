import os

TESTS_DIR = os.path.join(os.path.dirname(__file__), "backend", "tests")

# test_ai_engines.py
ai_test_code = """import pytest
from app.ai.nlp_parser import parse_natural_language_request
from app.ai.priority_engine import calculate_priority_score
from app.ai.duplicate_detector import detect_duplicates, haversine_distance_km
from app.ai.resource_matcher import match_resources_for_request
from app.models import CommunityRequest, RequestItem, AffectedZone, Warehouse, Inventory, SeverityLevel

def test_nlp_parser_extraction():
    prompt = "Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children."
    result = parse_natural_language_request(prompt)
    
    assert result.extracted_location == "Village A"
    assert result.affected_people == 350
    assert result.vulnerable_elderly == 40
    assert result.vulnerable_children == 25
    assert result.urgency == "CRITICAL"
    
    categories = [it.category for it in result.items]
    assert "Drinking Water" in categories
    assert "Food" in categories
    assert "Medicines" in categories
    assert result.confidence_score >= 0.85

def test_priority_engine_calculation():
    zone = AffectedZone(
        name="Zone B",
        code="ZONE-B",
        severity_level=SeverityLevel.SEVERE,
        water_level_meters=2.8,
        population=5000,
        households=1200,
        center_lat=14.52,
        center_lon=75.31
    )
    req = CommunityRequest(
        tracking_code="FR-1048",
        location_name="Village A",
        latitude=14.5230,
        longitude=75.3120,
        affected_people=350,
        affected_households=85,
        vulnerable_elderly=40,
        vulnerable_children=25,
        urgency=SeverityLevel.CRITICAL
    )
    req.items = [
        RequestItem(category="Drinking Water", item_name="Water", requested_quantity=2000, unit="L"),
        RequestItem(category="Medicines", item_name="Medicine", requested_quantity=35, unit="Kits")
    ]
    
    score, classification, factors = calculate_priority_score(req, zone=zone, waiting_hours=5.0)
    
    assert score >= 80.0
    assert classification == SeverityLevel.CRITICAL
    assert len(factors) == 5

def test_haversine_and_duplicate_detector():
    # Village A and nearby hamlet (within 200 meters)
    lat1, lon1 = 14.5230, 75.3120
    lat2, lon2 = 14.5240, 75.3130
    dist = haversine_distance_km(lat1, lon1, lat2, lon2)
    assert dist < 0.5 # less than 500m

    req1 = CommunityRequest(
        id=1,
        tracking_code="FR-1048",
        location_name="Village A",
        latitude=lat1,
        longitude=lon1,
        raw_description="Around 350 people are stranded in Village A. We urgently need drinking water and food."
    )
    req1.items = [RequestItem(category="Drinking Water", item_name="Water", requested_quantity=2000, unit="L")]

    req2 = CommunityRequest(
        id=2,
        tracking_code="FR-1052",
        location_name="Village A",
        latitude=lat2,
        longitude=lon2,
        raw_description="Around 320 people stranded in Village A. Urgently need drinking water."
    )
    req2.items = [RequestItem(category="Drinking Water", item_name="Water", requested_quantity=1800, unit="L")]

    is_dup, candidate, sim_score, reason = detect_duplicates(req2, [req1])
    assert is_dup is True
    assert candidate.id == 1
    assert sim_score >= 0.70

def test_resource_matcher_closest_warehouse():
    req = CommunityRequest(
        id=1,
        tracking_code="FR-1048",
        location_name="Village A",
        latitude=14.5230,
        longitude=75.3120,
        priority_classification=SeverityLevel.CRITICAL,
        priority_score=88.0
    )
    req.items = [RequestItem(category="Drinking Water", item_name="Drinking Water", requested_quantity=2000, unit="L", fulfilled_quantity=0)]

    wh_a = Warehouse(id=1, name="Warehouse A", code="WH-A", latitude=14.465, longitude=75.285, is_active=True)
    wh_a.inventory = [Inventory(category="Drinking Water", item_name="Drinking Water", available_quantity=3000, unit="L", batches=[])]

    wh_b = Warehouse(id=2, name="Warehouse B", code="WH-B", latitude=14.780, longitude=75.450, is_active=True)
    wh_b.inventory = [Inventory(category="Drinking Water", item_name="Drinking Water", available_quantity=5000, unit="L", batches=[])]

    recommendation = match_resources_for_request(req, [wh_a, wh_b])
    
    assert len(recommendation.recommendations) > 0
    # Warehouse A should be chosen because it is ~7km away vs Warehouse B ~30km away
    assert recommendation.recommendations[0].warehouse_name == "Warehouse A"
    assert recommendation.recommendations[0].recommended_qty == 2000
    assert recommendation.is_partial is False
"""

with open(os.path.join(TESTS_DIR, "test_ai_engines.py"), "w", encoding="utf-8") as f:
    f.write(ai_test_code)

print("test_ai_engines.py written")

# test_workflow_lifecycle.py
workflow_test_code = """import pytest
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
"""

with open(os.path.join(TESTS_DIR, "test_workflow_lifecycle.py"), "w", encoding="utf-8") as f:
    f.write(workflow_test_code)

print("test_workflow_lifecycle.py written")
