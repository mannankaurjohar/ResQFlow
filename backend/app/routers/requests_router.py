import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import (
    CommunityRequest,
    RequestItem,
    RequestVerification,
    AffectedZone,
    User,
    RequestStatus,
    SeverityLevel,
)
from app.schemas import (
    CommunityRequestCreate,
    CitizenItemPayload,
    CommunityRequestResponse,
    AIUnderstandingResponse,
    ExplainPriorityResponse,
    OverridePriorityRequest,
    VerifyRequestInput,
    CitizenEmergencyRequestCreate,
    CitizenRequestSyncPayload,
    CitizenSyncResponse,
    CitizenSyncResponseItem,
)
from app.auth import get_current_user, log_audit_event
from app.ai.nlp_parser import parse_natural_language_request
from app.ai.priority_engine import (
    calculate_priority_score,
    explain_priority,
)
from app.ai.duplicate_detector import detect_duplicates

router = APIRouter(
    prefix="/requests",
    tags=["Community Requests"]
)


# ============================================================
# NLP PARSING
# ============================================================

@router.post(
    "/parse-nlp",
    response_model=AIUnderstandingResponse
)
def parse_natural_language(payload: dict):
    text = payload.get("text", "")

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    return parse_natural_language_request(text)


# ============================================================
# LIST REQUESTS
# ============================================================

@router.get(
    "",
    response_model=List[CommunityRequestResponse]
)
def list_requests(
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    zone_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CommunityRequest)

    if status:
        query = query.filter(
            CommunityRequest.status == status
        )

    if urgency:
        query = query.filter(
            CommunityRequest.urgency == urgency
        )

    if zone_id:
        query = query.filter(
            CommunityRequest.zone_id == zone_id
        )

    return (
        query
        .order_by(
            CommunityRequest.priority_score.desc()
        )
        .all()
    )


# ============================================================
# CREATE COMMUNITY REQUEST
# ============================================================

@router.post(
    "",
    response_model=CommunityRequestResponse
)
def create_request(
    request_in: CommunityRequestCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):

    # --------------------------------------------------------
    # 1. Generate a UNIQUE tracking code
    #
    # IMPORTANT:
    # Do NOT use count + 1048 because deleted/test/simulation
    # records can create gaps and collisions.
    # --------------------------------------------------------

    tracking_number = 1049

    while True:
        candidate_code = (
            f"FR-{tracking_number}"
        )

        exists = (
            db.query(CommunityRequest)
            .filter(
                CommunityRequest.tracking_code
                == candidate_code
            )
            .first()
        )

        if not exists:
            tracking_code = candidate_code
            break

        tracking_number += 1

    # --------------------------------------------------------
    # 2. Find flood zone
    # --------------------------------------------------------

    zone = None

    if request_in.zone_id:
        zone = (
            db.query(AffectedZone)
            .filter(
                AffectedZone.id
                == request_in.zone_id
            )
            .first()
        )

    # Fallback to first active flood zone
    if zone is None:
        zone = (
            db.query(AffectedZone)
            .order_by(
                AffectedZone.id.asc()
            )
            .first()
        )

    # --------------------------------------------------------
    # 3. Validate request data
    # --------------------------------------------------------

    if request_in.affected_people < 1:
        raise HTTPException(
            status_code=400,
            detail="Affected people must be at least 1."
        )

    if not request_in.items:
        raise HTTPException(
            status_code=400,
            detail="At least one relief item is required."
        )

    for item in request_in.items:

        if item.requested_quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Requested quantity for "
                    f"{item.item_name} must be greater than 0."
                )
            )

        if not item.item_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Relief item name cannot be empty."
            )

    # --------------------------------------------------------
    # 4. Create request
    # --------------------------------------------------------

    new_req = CommunityRequest(
        tracking_code=tracking_code,
        zone_id=zone.id if zone else None,

        reporter_name=(
            request_in.reporter_name
            or "Anonymous Citizen"
        ),

        reporter_phone=request_in.reporter_phone,

        reporter_role=(
            request_in.reporter_role
            or "Citizen"
        ),

        location_name=request_in.location_name.strip(),

        latitude=request_in.latitude,
        longitude=request_in.longitude,

        affected_people=request_in.affected_people,
        affected_households=request_in.affected_households,

        vulnerable_elderly=(
            request_in.vulnerable_elderly
        ),

        vulnerable_children=(
            request_in.vulnerable_children
        ),

        vulnerable_infants=(
            request_in.vulnerable_infants
        ),

        vulnerable_pregnant=(
            request_in.vulnerable_pregnant
        ),

        urgency=request_in.urgency,

        raw_description=(
            request_in.raw_description.strip()
        ),

        status=RequestStatus.PENDING
    )

    db.add(new_req)
    db.flush()

    # --------------------------------------------------------
    # 5. Add requested relief items
    # --------------------------------------------------------

    for item in request_in.items:

        db_item = RequestItem(
            request_id=new_req.id,
            category=item.category,
            item_name=item.item_name.strip(),
            requested_quantity=(
                item.requested_quantity
            ),
            unit=item.unit
        )

        db.add(db_item)

    db.flush()

    # --------------------------------------------------------
    # 6. AI Priority Scoring
    # --------------------------------------------------------

    score, classification, factors = (
        calculate_priority_score(
            new_req,
            zone=zone,
            waiting_hours=0.5
        )
    )

    new_req.priority_score = score
    new_req.priority_classification = (
        classification
    )

    new_req.priority_factors_json = (
        json.dumps(factors)
    )

    # --------------------------------------------------------
    # 7. Duplicate Detection
    # --------------------------------------------------------

    existing_requests = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id
            != new_req.id
        )
        .all()
    )

    (
        is_duplicate,
        candidate,
        similarity_score,
        reason
    ) = detect_duplicates(
        new_req,
        existing_requests
    )

    if is_duplicate and candidate:

        new_req.status = (
            RequestStatus.FLAGGED_DUPLICATE
        )

        verification = RequestVerification(
            request_id=new_req.id,
            is_duplicate=True,
            duplicate_of_id=candidate.id,
            similarity_score=similarity_score,
            notes=reason,
            action_taken="FLAGGED"
        )

        db.add(verification)

    # --------------------------------------------------------
    # 8. Save request
    # --------------------------------------------------------

    db.commit()
    db.refresh(new_req)

    # --------------------------------------------------------
    # 9. Audit log
    # --------------------------------------------------------

    actor_name = (
        current_user.full_name
        if current_user
        else "Public Citizen"
    )

    actor_role = (
        current_user.role.value
        if current_user
        and hasattr(
            current_user.role,
            "value"
        )
        else "COMMUNITY"
    )

    log_audit_event(
        db=db,
        actor_id=(
            current_user.id
            if current_user
            else None
        ),
        actor_name=actor_name,
        actor_role=actor_role,
        action="CREATE_REQUEST",
        entity_type="COMMUNITY_REQUEST",
        entity_id=new_req.tracking_code,
        previous_state=None,
        new_state=json.dumps({
            "status": (
                new_req.status.value
                if hasattr(
                    new_req.status,
                    "value"
                )
                else str(new_req.status)
            ),
            "score": score,
            "location": new_req.location_name,
        }),
        reason=(
            f"Community request filed "
            f"from {new_req.location_name}"
        )
    )

    return new_req


# ============================================================
# GET REQUEST
# ============================================================

@router.get(
    "/{id}",
    response_model=CommunityRequestResponse
)
def get_request(
    id: int,
    db: Session = Depends(get_db)
):

    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return req


# ============================================================
# PRIORITY EXPLANATION
# ============================================================

@router.get(
    "/{id}/priority",
    response_model=ExplainPriorityResponse
)
def get_priority_explanation(
    id: int,
    db: Session = Depends(get_db)
):

    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return explain_priority(req)


# ============================================================
# AUTHORITY PRIORITY OVERRIDE
# ============================================================

@router.post(
    "/{id}/override-priority",
    response_model=ExplainPriorityResponse
)
def override_priority(
    id: int,
    payload: OverridePriorityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    old_score = req.priority_score

    req.authority_override_score = (
        payload.override_score
    )

    req.override_reason = (
        payload.override_reason
    )

    req.override_by = (
        current_user.full_name
    )

    db.commit()
    db.refresh(req)

    log_audit_event(
        db=db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=(
            current_user.role.value
            if hasattr(
                current_user.role,
                "value"
            )
            else str(current_user.role)
        ),
        action="OVERRIDE_PRIORITY",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=(
            f"Score: {old_score}"
        ),
        new_state=(
            f"Override Score: "
            f"{payload.override_score}"
        ),
        reason=payload.override_reason
    )

    return explain_priority(req)


# ============================================================
# VERIFY REQUEST
# ============================================================

@router.post(
    "/{id}/verify",
    response_model=CommunityRequestResponse
)
def verify_request(
    id: int,
    payload: VerifyRequestInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    action = payload.action.upper()

    if action == "APPROVED":
        req.status = RequestStatus.VERIFIED

    elif action == "MERGED":
        req.status = RequestStatus.VERIFIED

    elif action == "REJECTED":
        req.status = RequestStatus.REJECTED

    else:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid verification action. "
                "Use APPROVED, MERGED or REJECTED."
            )
        )

    verification = RequestVerification(
        request_id=req.id,
        verified_by_id=(
            current_user.id
            if current_user
            else None
        ),
        is_duplicate=(
            action == "MERGED"
        ),
        duplicate_of_id=(
            payload.duplicate_of_id
        ),
        similarity_score=(
            1.0
            if action == "MERGED"
            else 0.0
        ),
        notes=payload.notes,
        action_taken=action
    )

    db.add(verification)

    db.commit()
    db.refresh(req)

    log_audit_event(
        db=db,
        actor_id=(
            current_user.id
            if current_user
            else None
        ),
        actor_name=(
            current_user.full_name
            if current_user
            else "Volunteer"
        ),
        actor_role=(
            current_user.role.value
            if current_user
            and hasattr(
                current_user.role,
                "value"
            )
            else "VOLUNTEER"
        ),
        action=f"VERIFY_{action}",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=None,
        new_state=(
            req.status.value
            if hasattr(
                req.status,
                "value"
            )
            else str(req.status)
        ),
        reason=payload.notes
    )

    return req


# ============================================================
# CITIZEN MOBILE APP INGESTION & IDEMPOTENT SYNC
# ============================================================

def _process_citizen_request(
    request_in: CitizenEmergencyRequestCreate,
    db: Session
) -> CommunityRequest:
    # 1. Idempotency Check: check tracking_code or idempotency_key
    tracking_code = request_in.tracking_code
    idempotency_key = request_in.idempotency_key or tracking_code

    if idempotency_key:
        existing = db.query(CommunityRequest).filter(
            (CommunityRequest.idempotency_key == idempotency_key) |
            (CommunityRequest.tracking_code == idempotency_key)
        ).first()
        if existing:
            # Update communication status if needed and return existing request (Idempotent)
            if request_in.communication_method:
                existing.communication_method = request_in.communication_method
            if request_in.communication_status:
                existing.communication_status = request_in.communication_status
            db.commit()
            db.refresh(existing)
            return existing

    if tracking_code:
        existing_by_code = db.query(CommunityRequest).filter(
            CommunityRequest.tracking_code == tracking_code
        ).first()
        if existing_by_code:
            return existing_by_code

    # If no tracking code provided, generate standard RQ-XXXX code
    if not tracking_code:
        tracking_number = 1800
        while True:
            candidate_code = f"RQ-{tracking_number}"
            exists = db.query(CommunityRequest).filter(
                CommunityRequest.tracking_code == candidate_code
            ).first()
            if not exists:
                tracking_code = candidate_code
                break
            tracking_number += 1

    # 2. Find Nearest Flood Zone or Fallback
    zone = (
        db.query(AffectedZone)
        .order_by(AffectedZone.id.asc())
        .first()
    )

    # 3. Location description
    loc_name = request_in.location_name

    if not loc_name or not loc_name.strip():
        if request_in.latitude is not None and request_in.longitude is not None:
            loc_name = (
                f"GPS ({request_in.latitude:.5f}, "
                f"{request_in.longitude:.5f})"
            )
        else:
            loc_name = "Location unavailable"

    # 4. Synthesize raw description for Command Center / AI models
    desc_parts = [
        f"Type: {request_in.request_type}",
        f"People: {request_in.affected_people}"
    ]
    if request_in.situation_flags:
        desc_parts.append(f"Situation: {', '.join(request_in.situation_flags)}")
    if request_in.medical_emergency:
        med_info = ', '.join(request_in.medical_conditions) if request_in.medical_conditions else 'Yes'
        desc_parts.append(f"Medical Emergency: {med_info}")
    if request_in.immediate_danger and request_in.immediate_danger != "NO":
        danger_info = ', '.join(request_in.danger_details) if request_in.danger_details else request_in.immediate_danger
        desc_parts.append(f"Immediate Danger: {danger_info}")
    if request_in.additional_information:
        desc_parts.append(f"Notes: {request_in.additional_information}")

    raw_description = " | ".join(desc_parts)

    urgency_level = SeverityLevel.CRITICAL if (request_in.medical_emergency or request_in.immediate_danger == "YES") else SeverityLevel.HIGH

    new_req = CommunityRequest(
        tracking_code=tracking_code,
        idempotency_key=idempotency_key or tracking_code,
        zone_id=zone.id if zone else None,
        reporter_name="Citizen Mobile User",
        reporter_phone=None,
        reporter_role="Citizen",
        location_name=loc_name.strip(),
        latitude=request_in.latitude,
        longitude=request_in.longitude,
        location_accuracy=request_in.location_accuracy,
        affected_people=max(1, request_in.affected_people),
        affected_households=1,
        vulnerable_elderly=request_in.elderly or 0,
        vulnerable_children=request_in.children or 0,
        vulnerable_infants=0,
        vulnerable_pregnant=0,
        urgency=urgency_level,
        raw_description=raw_description,
        request_type=request_in.request_type or "EVACUATION",
        communication_method=request_in.communication_method or "INTERNET",
        communication_status="RECEIVED",
        medical_emergency=request_in.medical_emergency,
        medical_conditions_json=json.dumps(request_in.medical_conditions) if request_in.medical_conditions else None,
        immediate_danger=request_in.immediate_danger,
        danger_details_json=json.dumps(request_in.danger_details) if request_in.danger_details else None,
        situation_flags_json=json.dumps(request_in.situation_flags) if request_in.situation_flags else None,
        location_type=request_in.location_type,
        rescuer_access=request_in.rescuer_access,
        access_problem_json=json.dumps(request_in.access_problems) if request_in.access_problems else None,
        accessibility_json=json.dumps(request_in.accessibility_requirements) if request_in.accessibility_requirements else None,
        photo_url=request_in.photo_url,
        status=RequestStatus.PENDING
    )

    db.add(new_req)
    db.flush()

    # 5. Insert Request Items
    if request_in.items and len(request_in.items) > 0:
        for it in request_in.items:
            db_item = RequestItem(
                request_id=new_req.id,
                category=it.category or "Relief",
                item_name=it.item_name.strip(),
                requested_quantity=max(1.0, float(it.requested_quantity)),
                unit=it.unit or "Units"
            )
            db.add(db_item)
    else:
        # Default item for evacuation request
        item_title = "Evacuation & Rescue Service" if request_in.request_type == "EVACUATION" else "Emergency Relief Package"
        db_item = RequestItem(
            request_id=new_req.id,
            category="Rescue" if request_in.request_type == "EVACUATION" else "Food & Water",
            item_name=item_title,
            requested_quantity=float(new_req.affected_people),
            unit="Persons" if request_in.request_type == "EVACUATION" else "Packs"
        )
        db.add(db_item)

    db.flush()

    # 6. Priority Scoring
    score, classification, factors = calculate_priority_score(
        new_req,
        zone=zone,
        waiting_hours=0.1
    )
    new_req.priority_score = score
    new_req.priority_classification = classification
    new_req.priority_factors_json = json.dumps(factors)

    db.commit()
    db.refresh(new_req)

    log_audit_event(
        db=db,
        actor_id=None,
        actor_name="Citizen Mobile App",
        actor_role="COMMUNITY",
        action="CITIZEN_REQUEST_INGESTED",
        entity_type="COMMUNITY_REQUEST",
        entity_id=new_req.tracking_code,
        previous_state=None,
        new_state=json.dumps({
            "tracking_code": new_req.tracking_code,
            "type": new_req.request_type,
            "method": new_req.communication_method,
            "status": str(new_req.status),
            "priority": score
        }),
        reason=f"Citizen {new_req.request_type} request received via {new_req.communication_method}"
    )

    return new_req


@router.post(
    "/citizen",
    response_model=CommunityRequestResponse
)
def create_citizen_request(
    request_in: CitizenEmergencyRequestCreate,
    db: Session = Depends(get_db)
):
    return _process_citizen_request(request_in, db)


@router.post(
    "/citizen/sync",
    response_model=CitizenSyncResponse
)
def sync_citizen_requests(
    payload: CitizenRequestSyncPayload,
    db: Session = Depends(get_db)
):
    results = []
    for req_in in payload.requests:
        req = _process_citizen_request(req_in, db)
        results.append(CitizenSyncResponseItem(
            tracking_code=req.tracking_code,
            status=req.status.value if hasattr(req.status, 'value') else str(req.status),
            message="Request synchronized with ResQFlow Command Center",
            received_at=req.created_at,
            communication_method=req.communication_method or "INTERNET",
            communication_status="SYNCED"
        ))

    return CitizenSyncResponse(
        synced_count=len(results),
        results=results
    )


@router.get(
    "/citizen/tracking/{tracking_code}",
    response_model=CommunityRequestResponse
)
def get_citizen_request_by_code(
    tracking_code: str,
    db: Session = Depends(get_db)
):
    req = db.query(CommunityRequest).filter(
        (CommunityRequest.tracking_code == tracking_code) |
        (CommunityRequest.idempotency_key == tracking_code)
    ).first()
    if not req:
        raise HTTPException(
            status_code=404,
            detail=f"Request with tracking code {tracking_code} not found"
        )
    return req


# ============================================================
# INBOUND SMS GATEWAY WEBHOOK & PARSER
# ============================================================

@router.post(
    "/sms-inbound",
    response_model=CommunityRequestResponse
)
def receive_inbound_sms(
    payload: dict,
    db: Session = Depends(get_db)
):
    # Accept multiple gateway formats (Twilio, Textlocal, Android SMS Gateway app, custom)
    body = payload.get("message") or payload.get("Body") or payload.get("content") or payload.get("text") or ""
    sender = payload.get("sender") or payload.get("From") or payload.get("number") or payload.get("phone") or "Citizen via SMS"

    body = str(body).strip()
    if not body:
        raise HTTPException(status_code=400, detail="Empty SMS body")

    # Check for structured compact format
    
    if body.startswith("RF:SOS|") or body.startswith("RF:SUP|"):
        parts = body.split("|")
        req_type = "EVACUATION" if parts[0] == "RF:SOS" else "SUPPLIES"
        tracking_code = parts[1] if len(parts) > 1 else None
        lat = None
        lon = None
        acc = None
        people = 1
        med_emergency = False
        danger = "NOT_SURE"
        situation_flags = []
        supplies_list = []

        if len(parts) > 2 and "," in parts[2]:
            try:
                coords = parts[2].split(",")
                lat = float(coords[0].strip())
                lon = float(coords[1].strip())
            except Exception:
                pass

        for p in parts[3:]:
            if p.startswith("ACC:"):
                try: acc = float(p.replace("ACC:", "").strip())
                except: pass
            elif p.startswith("P:"):
                try: people = int(p.replace("P:", "").strip())
                except: pass
            elif p.startswith("MED:"):
                med_val = p.replace("MED:", "").strip()
                med_emergency = (med_val == "1" or med_val.upper() == "YES" or med_val.upper() == "TRUE")
            elif p.startswith("DNG:"):
                danger = p.replace("DNG:", "").strip()
            elif p.startswith("SIT:"):
                situation_flags.append(p.replace("SIT:", "").strip())
            elif p.startswith("ITEMS:"):
                items_str = p.replace("ITEMS:", "").strip()
                supplies_list = [it.strip() for it in items_str.split(",") if it.strip()]

        items_payload = None
        if supplies_list:
            items_payload = [
                CitizenItemPayload(
                    category="Food & Water",
                    item_name=item_name,
                    requested_quantity=float(people),
                    unit="Units"
                )
                for item_name in supplies_list
            ]

        citizen_in = CitizenEmergencyRequestCreate(
            tracking_code=tracking_code,
            idempotency_key=tracking_code,
            request_type=req_type,
            latitude=lat,
            longitude=lon,
            location_accuracy=acc,
            location_name=f"GPS ({lat:.5f}, {lon:.5f}) [SMS from {sender}]",
            affected_people=people,
            situation_flags=situation_flags,
            medical_emergency=med_emergency,
            medical_conditions=["Medical assistance requested via SMS"] if med_emergency else [],
            immediate_danger=danger,
            additional_information=f"Inbound SMS: {body}",
            communication_method="SMS",
            communication_status="RECEIVED",
            items=items_payload
        )
        return _process_citizen_request(citizen_in, db)

    # Fallback to natural language SMS parser
    parsed = parse_natural_language_request(body)
    lat = parsed.latitude
    lon = parsed.longitude

    citizen_in = CitizenEmergencyRequestCreate(
        request_type="EVACUATION",
        latitude=lat,
        longitude=lon,
        location_name=parsed.extracted_location or f"SMS Report from {sender}",
        affected_people=max(1, parsed.affected_people),
        situation_flags=["SMS Emergency Report"],
        medical_emergency=parsed.urgency == "CRITICAL",
        immediate_danger="YES" if parsed.urgency == "CRITICAL" else "NOT_SURE",
        additional_information=f"Raw SMS from {sender}: {body}",
        communication_method="SMS",
        communication_status="RECEIVED"
    )
    return _process_citizen_request(citizen_in, db)