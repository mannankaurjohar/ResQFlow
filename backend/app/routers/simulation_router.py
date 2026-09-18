import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AffectedZone,
    CommunityRequest,
    RequestItem,
    DisasterEvent,
    SeverityLevel,
    RequestStatus,
)
from app.auth import log_audit_event

router = APIRouter(
    prefix="/simulation",
    tags=["Flood Simulation Engine"]
)

SIMULATION_STATE = {
    "is_escalated": False,
    "flood_phase": "Phase 1 - Baseline Inundation",
    "rainfall_rate_mm_hr": 35.0,
    "water_level_zone_b": 2.8
}


@router.get("/status")
def get_simulation_status():
    return SIMULATION_STATE


@router.post("/escalate")
def escalate_flood(db: Session = Depends(get_db)):

    # ---------------------------------------------------------
    # Set simulation state
    # ---------------------------------------------------------

    SIMULATION_STATE["is_escalated"] = True
    SIMULATION_STATE["flood_phase"] = (
        "Phase 2 - River Basin Breach & Rapid Surge"
    )
    SIMULATION_STATE["rainfall_rate_mm_hr"] = 92.5
    SIMULATION_STATE["water_level_zone_b"] = 3.2

    # ---------------------------------------------------------
    # 1. Escalate Zone B
    # ---------------------------------------------------------

    zone_b = (
        db.query(AffectedZone)
        .filter(AffectedZone.code == "ZONE-B")
        .first()
    )

    if zone_b:
        zone_b.severity_level = SeverityLevel.SEVERE
        zone_b.water_level_meters = 3.20
        zone_b.is_isolated = True

    # ---------------------------------------------------------
    # 2. Escalate Disaster Event
    # ---------------------------------------------------------

    disaster = db.query(DisasterEvent).first()

    if disaster:
        disaster.status = "ESCALATED"
        disaster.severity = SeverityLevel.CRITICAL

    # ---------------------------------------------------------
    # 3. Escalate Village A
    # ---------------------------------------------------------

    village_a = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.location_name == "Village A"
        )
        .first()
    )

    if village_a:
        village_a.urgency = SeverityLevel.CRITICAL
        village_a.affected_people = 350
        village_a.vulnerable_elderly = 40
        village_a.vulnerable_children = 25
        village_a.vulnerable_infants = 5

        village_a.priority_score = 88.0
        village_a.priority_classification = (
            SeverityLevel.CRITICAL
        )

        village_a.raw_description = (
            "Around 350 people are stranded in Village A. "
            "They urgently need drinking water, food and medicines. "
            "There are 40 elderly people and 25 children."
        )

        village_a.priority_factors_json = json.dumps([
            {
                "factor": "Affected Population",
                "points": 25.0,
                "reason": "350 people stranded"
            },
            {
                "factor": "Vulnerable Demographics",
                "points": 20.0,
                "reason": "65 vulnerable people"
            },
            {
                "factor": "Resource Essentiality",
                "points": 20.0,
                "reason": "Water and medicine required"
            },
            {
                "factor": "Flood Severity",
                "points": 15.0,
                "reason": "3.2m water level and isolation"
            },
            {
                "factor": "Response Latency",
                "points": 8.0,
                "reason": "Request pending"
            }
        ])

    # ---------------------------------------------------------
    # 4. Create a NEW request caused by flood escalation
    # ---------------------------------------------------------
    # This is what makes the simulation visibly affect the
    # request statistics and GIS map.
    # ---------------------------------------------------------

    escalation_code = "FR-ESC-0001"

    escalation_request = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.tracking_code ==
            escalation_code
        )
        .first()
    )

    if not escalation_request:

        escalation_request = CommunityRequest(
            tracking_code=escalation_code,
            zone_id=zone_b.id if zone_b else 1,
            reporter_name="Flood Simulation Control Room",
            reporter_phone="N/A",
            reporter_role="SIMULATION",
            location_name="Riverside Cluster",
            latitude=14.5310,
            longitude=75.3260,
            affected_people=420,
            affected_households=105,
            vulnerable_elderly=35,
            vulnerable_children=48,
            vulnerable_infants=12,
            urgency=SeverityLevel.CRITICAL,
            raw_description=(
                "Flood escalation has isolated the Riverside Cluster. "
                "Approximately 420 people require urgent drinking water, "
                "food and medical supplies."
            ),
            priority_score=91.0,
            priority_classification=SeverityLevel.CRITICAL,
            priority_factors_json=json.dumps([
                {
                    "factor": "Affected Population",
                    "points": 27.0,
                    "reason": "420 people affected"
                },
                {
                    "factor": "Vulnerable Population",
                    "points": 19.0,
                    "reason": "95 vulnerable people"
                },
                {
                    "factor": "Flood Severity",
                    "points": 18.0,
                    "reason": "Severe surge conditions"
                },
                {
                    "factor": "Isolation",
                    "points": 15.0,
                    "reason": "Access restricted"
                },
                {
                    "factor": "Emergency Essentiality",
                    "points": 12.0,
                    "reason": "Water, food and medical needs"
                }
            ]),
            status=RequestStatus.PENDING,
        )

        db.add(escalation_request)
        db.flush()

        db.add_all([
            RequestItem(
                request_id=escalation_request.id,
                category="Drinking Water",
                item_name="Drinking Water",
                requested_quantity=2500.0,
                unit="L"
            ),
            RequestItem(
                request_id=escalation_request.id,
                category="Food",
                item_name="Emergency Food Rations",
                requested_quantity=500.0,
                unit="Packets"
            ),
            RequestItem(
                request_id=escalation_request.id,
                category="Medicines",
                item_name="Emergency Medical Kits",
                requested_quantity=45.0,
                unit="Kits"
            )
        ])

    # ---------------------------------------------------------
    # 5. Escalate another zone to make the GIS change visible
    # ---------------------------------------------------------

    zone_c = (
        db.query(AffectedZone)
        .filter(AffectedZone.code == "ZONE-C")
        .first()
    )

    if zone_c:
        zone_c.severity_level = SeverityLevel.HIGH
        zone_c.water_level_meters = 2.1

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    db.commit()

    # ---------------------------------------------------------
    # Audit
    # ---------------------------------------------------------

    log_audit_event(
        db=db,
        actor_id=1,
        actor_name="System Simulation Trigger",
        actor_role="SIMULATION_ENGINE",
        action="ESCALATE_FLOOD_SIMULATION",
        entity_type="DISASTER_EVENT",
        entity_id="FLOOD-2026",
        previous_state="BASELINE",
        new_state="SEVERE_SURGE_PHASE_2",
        reason=(
            "Hydrological crest breach simulation executed."
        )
    )

    return {
        "is_escalated": True,
        "flood_phase":
            SIMULATION_STATE["flood_phase"],
        "rainfall_rate_mm_hr":
            SIMULATION_STATE["rainfall_rate_mm_hr"],
        "water_level_zone_b":
            SIMULATION_STATE["water_level_zone_b"],
        "message": (
            "Flood escalation activated. "
            "Zone B water level increased to 3.2m, "
            "Riverside Cluster became a new critical request, "
            "and Zone C severity increased."
        )
    }


@router.post("/reset")
def reset_simulation(
    db: Session = Depends(get_db)
):

    from app.seed_data import seed_all_data

    SIMULATION_STATE["is_escalated"] = False
    SIMULATION_STATE["flood_phase"] = (
        "Phase 1 - Baseline Inundation"
    )
    SIMULATION_STATE["rainfall_rate_mm_hr"] = 35.0
    SIMULATION_STATE["water_level_zone_b"] = 2.8

    seed_all_data(
        db,
        force_reset=True
    )

    return {
        "is_escalated": False,
        "flood_phase":
            SIMULATION_STATE["flood_phase"],
        "rainfall_rate_mm_hr":
            SIMULATION_STATE["rainfall_rate_mm_hr"],
        "water_level_zone_b":
            SIMULATION_STATE["water_level_zone_b"],
        "message":
            "Flood simulation reset successfully."
    }