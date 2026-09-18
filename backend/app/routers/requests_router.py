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
    CommunityRequestResponse,
    AIUnderstandingResponse,
    ExplainPriorityResponse,
    OverridePriorityRequest,
    VerifyRequestInput,
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