import pytest
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
