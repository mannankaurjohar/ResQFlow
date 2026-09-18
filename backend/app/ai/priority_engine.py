import json
import datetime
from typing import Dict, Any, List, Tuple
from app.models import CommunityRequest, AffectedZone, SeverityLevel
from app.schemas import PriorityFactor, ExplainPriorityResponse

def calculate_priority_score(
    request: CommunityRequest,
    zone: AffectedZone = None,
    waiting_hours: float = 2.0
) -> Tuple[float, SeverityLevel, List[Dict[str, Any]]]:
    factors: List[Dict[str, Any]] = []
    total_score = 0.0

    # 1. Affected Population Factor (Max 25 pts)
    # Logarithmic/tiered scaling
    people = request.affected_people or 1
    if people >= 300:
        pop_pts = 25.0
        pop_reason = f"{people} people stranded/affected (Extremely high density)"
    elif people >= 150:
        pop_pts = 20.0
        pop_reason = f"{people} people stranded/affected (High density)"
    elif people >= 50:
        pop_pts = 15.0
        pop_reason = f"{people} people stranded/affected (Medium density)"
    else:
        pop_pts = min(12.0, max(5.0, people * 0.25))
        pop_reason = f"{people} people affected"
    
    total_score += pop_pts
    factors.append({"factor": "Affected Population", "points": pop_pts, "reason": pop_reason})

    # 2. Vulnerable Population Factor (Max 25 pts)
    vulnerable_count = (
        (request.vulnerable_elderly or 0) +
        (request.vulnerable_children or 0) +
        (request.vulnerable_infants or 0) * 1.5 +
        (request.vulnerable_pregnant or 0) * 1.5
    )
    if vulnerable_count >= 50:
        vuln_pts = 20.0 if vulnerable_count < 70 else 24.0
        vuln_reason = f"{int(vulnerable_count)} vulnerable individuals (Elderly, Children, Infants) requiring urgent medical/thermal care"
    elif vulnerable_count >= 20:
        vuln_pts = 16.0
        vuln_reason = f"{int(vulnerable_count)} vulnerable individuals present"
    elif vulnerable_count > 0:
        vuln_pts = min(12.0, vulnerable_count * 0.8)
        vuln_reason = f"{int(vulnerable_count)} vulnerable individuals identified"
    else:
        vuln_pts = 2.0
        vuln_reason = "Standard adult population"

    total_score += vuln_pts
    factors.append({"factor": "Vulnerable Demographics", "points": vuln_pts, "reason": vuln_reason})

    # 3. Resource Essentiality Factor (Max 25 pts)
    # Check items categories
    item_categories = [item.category.lower() for item in request.items] if request.items else []
    has_water = any("water" in c for c in item_categories)
    has_meds = any("medicine" in c or "medical" in c for c in item_categories)
    has_food = any("food" in c for c in item_categories)

    if has_water and has_meds:
        ess_pts = 20.0
        ess_reason = "Life-critical combination: Drinking Water and Emergency Medicines required"
    elif has_water:
        ess_pts = 16.0
        ess_reason = "Primary survival resource: Clean Drinking Water required"
    elif has_meds:
        ess_pts = 16.0
        ess_reason = "Urgent health risk: Medical Supplies required"
    elif has_food:
        ess_pts = 12.0
        ess_reason = "Essential nutrition: Food supplies required"
    else:
        ess_pts = 8.0
        ess_reason = "Secondary shelter and sanitation relief supplies"

    total_score += ess_pts
    factors.append({"factor": "Resource Essentiality", "points": ess_pts, "reason": ess_reason})

    # 4. Flood Severity & Zone Inundation Factor (Max 15 pts)
    zone_severity = zone.severity_level if zone else SeverityLevel.HIGH
    if zone_severity in [SeverityLevel.SEVERE, SeverityLevel.CRITICAL]:
        zone_pts = 15.0
        zone_reason = f"Located in {zone.name if zone else 'Zone B'} (Severe Inundation, water level > 2.0m)"
    elif zone_severity == SeverityLevel.HIGH:
        zone_pts = 12.0
        zone_reason = f"Located in {zone.name if zone else 'High Risk Zone'} (High flood impact)"
    elif zone_severity == SeverityLevel.MODERATE:
        zone_pts = 8.0
        zone_reason = "Moderate inundation zone"
    else:
        zone_pts = 4.0
        zone_reason = "Low flood risk sector"

    total_score += zone_pts
    factors.append({"factor": "Flood Severity Zone", "points": zone_pts, "reason": zone_reason})

    # 5. Waiting Time & Isolation Factor (Max 10 pts)
    wait_pts = min(10.0, max(2.0, waiting_hours * 1.6))
    wait_reason = f"Request pending for approximately {waiting_hours:.1f} hours without full relief delivery"
    total_score += wait_pts
    factors.append({"factor": "Response Latency", "points": round(wait_pts, 1), "reason": wait_reason})

    final_score = min(100.0, max(5.0, round(total_score, 1)))

    # Classification
    if final_score >= 80.0:
        classification = SeverityLevel.CRITICAL
    elif final_score >= 60.0:
        classification = SeverityLevel.HIGH
    elif final_score >= 40.0:
        classification = SeverityLevel.MEDIUM
    else:
        classification = SeverityLevel.LOW

    return final_score, classification, factors

def explain_priority(request: CommunityRequest) -> ExplainPriorityResponse:
    factors_list = []
    if request.priority_factors_json:
        try:
            factors_list = json.loads(request.priority_factors_json)
        except Exception:
            factors_list = []
            
    active_score = request.authority_override_score if request.authority_override_score is not None else request.priority_score
    active_class = request.priority_classification
    if request.authority_override_score is not None:
        if active_score >= 80:
            active_class = SeverityLevel.CRITICAL
        elif active_score >= 60:
            active_class = SeverityLevel.HIGH
        elif active_score >= 40:
            active_class = SeverityLevel.MEDIUM
        else:
            active_class = SeverityLevel.LOW

    return ExplainPriorityResponse(
        request_id=request.id,
        tracking_code=request.tracking_code,
        priority_score=active_score,
        priority_classification=active_class.value if hasattr(active_class, 'value') else str(active_class),
        factors=[PriorityFactor(**f) for f in factors_list],
        authority_override_score=request.authority_override_score,
        override_reason=request.override_reason,
        override_by=request.override_by
    )
