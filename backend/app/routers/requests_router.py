import json
from fastapi import APIRouter, Depends, HTTPException,Header
from sqlalchemy.orm import Session
from typing import List, Optional
import hmac
import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging
from app.config import settings
from datetime import datetime
import secrets
from pydantic import BaseModel
import re
from app.database import get_db
from app.models import (
    CommunityRequest,
    RequestItem,
    RequestVerification,
    AffectedZone,
    User,
    RequestStatus,
    RequestClarification,
    SmsDeviceRegistration,
    IST,
    SeverityLevel,
    ResponseAssignment,
    Allocation,
    Delivery,
    UserRole,
    Warehouse,
    ReliefStatus,
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
    CreateDuplicateClarificationInput,
    CitizenDuplicateClarificationResponseInput,
    CitizenRequestSyncPayload,
    CitizenSyncResponse,
    CitizenSyncResponseItem,
)
from app.auth import (
    get_current_user,
    get_optional_current_user,
    log_audit_event,
    require_role,
)
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
class SmsDeviceTokenInput(BaseModel):
    token: str
def require_sms_device(
    token: Optional[str] = Header(
        default=None,
        alias="X-ResQFlow-SMS-Token",
    ),
):
    expected = settings.RESQFLOW_SMS_DEVICE_TOKEN

    if not expected:
        raise HTTPException(
            status_code=503,
            detail="SMS device integration is not configured.",
        )

    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=401,
            detail="Invalid SMS device credentials.",
        )
def send_sms_wakeup_notification(fcm_token: str) -> bool:
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()

    if not service_account_json:
        logging.warning("FCM is not configured: missing service account.")
        return False

    try:
        try:
            app = firebase_admin.get_app()
        except ValueError:
            service_account = json.loads(service_account_json)
            app = firebase_admin.initialize_app(
                credentials.Certificate(service_account)
            )

        message = messaging.Message(
            data={"type": "SEND_PENDING_SMS"},
            token=fcm_token,
            android=messaging.AndroidConfig(priority="high"),
        )

        messaging.send(message, app=app)
        return True

    except Exception:
        logging.exception("Failed to send SMS wake-up notification.")
        return False
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
    exclude_assigned: bool = False,
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

    if exclude_assigned:
        query = query.filter(
            ~CommunityRequest.id.in_(
                db.query(ResponseAssignment.request_id).filter(
                    ResponseAssignment.status != "CANCELLED"
                )
            ),
            CommunityRequest.status.notin_([
                RequestStatus.DELIVERED,
                RequestStatus.REJECTED,
                RequestStatus.FLAGGED_DUPLICATE,
            ])
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
    current_user: Optional[User] = Depends(get_optional_current_user)
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

        request_type=request_in.request_type or "SUPPLIES",

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
@router.get("/my-duplicate-clarifications")
def get_my_duplicate_clarifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.COMMUNITY])
    ),
):
    account_phone = _normalise_clarification_phone(
        current_user.phone
    )

    if not account_phone:
        return []

    requests = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.reporter_phone.isnot(None)
        )
        .all()
    )

    notifications = []

    for req in requests:
        if (
            _normalise_clarification_phone(req.reporter_phone)
            != account_phone
        ):
            continue

        clarification = (
            db.query(RequestClarification)
            .filter(
                RequestClarification.request_id == req.id,
                RequestClarification.status == "PENDING",
            )
            .order_by(RequestClarification.id.desc())
            .first()
        )

        if not clarification:
            continue

        notifications.append({
            "id": clarification.id,
            "request_id": req.id,
            "tracking_code": req.tracking_code,
            "message": clarification.message,
            "created_at": (
                clarification.created_at.isoformat()
                if clarification.created_at
                else None
            ),
        })

    notifications.sort(
        key=lambda item: item["created_at"] or "",
        reverse=True,
    )

    return notifications

@router.get(
    "/my-requests",
    response_model=List[CommunityRequestResponse]
)
def get_my_requests(
    phone: str,
    db: Session = Depends(get_db)
):
    requests = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.reporter_phone == phone
        )
        .order_by(
            CommunityRequest.id.desc()
        )
        .all()
    )

    return requests
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
# DUPLICATE CLARIFICATION — SHARED WEBSITE RESPONSE STATE
# ============================================================

DEFAULT_DUPLICATE_QUESTION = (
    "We need to verify your request because it may be a duplicate. "
    "Is this a separate, genuine request? Please explain briefly."
)


def _normalise_clarification_phone(phone: Optional[str]) -> str:
    digits = re.sub(r"\D", "", phone or "")

    # Normalize Indian mobile numbers to the same 10-digit format.
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]

    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]

    return digits


def _clarification_payload(item: RequestClarification) -> dict:
    return {
        "id": item.id,
        "request_id": item.request_id,
        "question": item.question,
        "message": item.message,
        "reply_code": item.reply_code,
        "status": item.status,
        "response": item.response,
        "response_channel": item.response_channel,
        "sms_status": item.sms_status,
        "sms_error": item.sms_error,
        "decision": item.decision,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "responded_at": item.responded_at.isoformat() if item.responded_at else None,
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
    }


@router.post("/{id}/duplicate-clarification")
def create_duplicate_clarification(
    id: int,
    payload: CreateDuplicateClarificationInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.EMERGENCY_COORDINATOR])
    ),
):
    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")

    if req.status != RequestStatus.FLAGGED_DUPLICATE:
        raise HTTPException(
            status_code=409,
            detail="Only flagged duplicate requests can be clarified.",
        )

    # Do not create multiple unanswered clarifications for one request.
    existing = (
        db.query(RequestClarification)
        .filter(
            RequestClarification.request_id == id,
            RequestClarification.status == "PENDING",
        )
        .order_by(RequestClarification.id.desc())
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This request already has a pending clarification.",
        )

    question = (payload.question or "").strip() or None
    message = question or DEFAULT_DUPLICATE_QUESTION
    reply_code = secrets.token_hex(4).upper()


    sms_message = (
        f"ResQFlow request {req.tracking_code}: {message}\n"
        "Reply to this SMS in your own words to answer the question. "
        "Please reply from the phone number registered with your request."
    )


    clarification = RequestClarification(
        request_id=id,
        created_by_id=current_user.id,
        question=question,
        message=message,
        reply_code=reply_code,
        status="PENDING",
        sms_status=(
            "PENDING"
            if settings.RESQFLOW_SMS_DEVICE_TOKEN
            else "NOT_CONFIGURED"
        ),
    )

    db.add(clarification)

    # Record the authority's clarification action in the existing history.
    previous_review = (
        db.query(RequestVerification)
        .filter(RequestVerification.request_id == id)
        .order_by(RequestVerification.id.desc())
        .first()
    )

    if previous_review:
        db.add(
            RequestVerification(
                request_id=req.id,
                verified_by_id=current_user.id,
                is_duplicate=previous_review.is_duplicate,
                duplicate_of_id=previous_review.duplicate_of_id,
                similarity_score=previous_review.similarity_score,
                notes=question or "Default duplicate clarification sent.",
                action_taken="REQUEST_CLARIFICATION",
            )
        )

    log_audit_event(
        db=db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=(
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        ),
        action="DUPLICATE_CLARIFICATION_CREATED",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=RequestStatus.FLAGGED_DUPLICATE.value,
        new_state=RequestStatus.FLAGGED_DUPLICATE.value,
        reason=question or "Default clarification question",
    )

    db.commit()
    db.refresh(clarification)

    push_sent = False

    if clarification.sms_status == "PENDING":
        registration = (
            db.query(SmsDeviceRegistration)
            .filter(SmsDeviceRegistration.id == 1)
            .first()
        )

        if registration:
            push_sent = send_sms_wakeup_notification(
                registration.fcm_token
            )

    result = _clarification_payload(clarification)
    result["sms_message"] = sms_message
    result["sms_wakeup_sent"] = push_sent
    result["sms_delivery_note"] = (
        "SMS queued; Android wake-up sent."
        if push_sent
        else (
            "SMS is pending, but the Android wake-up failed or no device token is registered."
            if clarification.sms_status == "PENDING"
            else "SMS device integration is not configured."
        )
    )
    return result
@router.post("/sms-device/register-token")
def register_sms_device_token(
    payload: SmsDeviceTokenInput,
    db: Session = Depends(get_db),
    _device=Depends(require_sms_device),
):
    token = payload.token.strip()

    if not token:
        raise HTTPException(status_code=400, detail="FCM token is required.")

    registration = (
        db.query(SmsDeviceRegistration)
        .filter(SmsDeviceRegistration.id == 1)
        .first()
    )

    if registration:
        registration.fcm_token = token
    else:
        registration = SmsDeviceRegistration(id=1, fcm_token=token)
        db.add(registration)

    db.commit()

    return {"registered": True}
@router.get("/sms-device/next")
def get_next_sms_for_device(
    db: Session = Depends(get_db),
    _device=Depends(require_sms_device),
):
    row = (
        db.query(RequestClarification, CommunityRequest)
        .join(
            CommunityRequest,
            RequestClarification.request_id == CommunityRequest.id,
        )
        .filter(
            RequestClarification.sms_status == "PENDING",
            RequestClarification.status == "PENDING",
        )
        .order_by(RequestClarification.id.asc())
        .first()
    )

    if not row:
        return {"message": None}

    clarification, req = row

    if not (req.reporter_phone or "").strip():
        clarification.sms_status = "FAILED"
        clarification.sms_error = "No registered citizen phone number."
        db.commit()
        return {"message": None}

    # Claim atomically so concurrent polls cannot claim the same message.
    claimed = (
        db.query(RequestClarification)
        .filter(
            RequestClarification.id == clarification.id,
            RequestClarification.sms_status == "PENDING",
            RequestClarification.status == "PENDING",
        )
        .update(
            {"sms_status": "SENDING"},
            synchronize_session=False,
        )
    )

    if claimed != 1:
        db.rollback()
        return {"message": None}

    db.commit()

    sms_message = (
        f"ResQFlow request {req.tracking_code}: {clarification.message}\n"
        "Reply to this SMS in your own words to answer the question. "
        "Please reply from the phone number registered with your request."
    )

    return {
        "id": clarification.id,
        "to": req.reporter_phone,
        "text": sms_message,
    }


@router.post("/sms-device/{clarification_id}/result")
def report_sms_result(
    clarification_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    _device=Depends(require_sms_device),
):
    result = str(payload.get("result", "")).upper()

    if result not in {"SENT", "FAILED"}:
        raise HTTPException(
            status_code=400,
            detail="result must be SENT or FAILED.",
        )

    clarification = (
        db.query(RequestClarification)
        .filter(RequestClarification.id == clarification_id)
        .first()
    )

    if not clarification:
        raise HTTPException(
            status_code=404,
            detail="Clarification not found.",
        )

    if clarification.sms_status != "SENDING":
        raise HTTPException(
            status_code=409,
            detail="Clarification is not awaiting an SMS result.",
        )

    clarification.sms_status = result
    clarification.sms_error = (
        None
        if result == "SENT"
        else str(payload.get("error", "Android SMS sending failed."))[:1000]
    )

    db.commit()

    return {
        "id": clarification.id,
        "sms_status": clarification.sms_status,
    }


@router.get("/{id}/duplicate-clarification")
def get_duplicate_clarification(
    id: int,
    phone: str,
    db: Session = Depends(get_db),
):
    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")

    supplied_phone = _normalise_clarification_phone(phone)
    registered_phone = _normalise_clarification_phone(req.reporter_phone)

    if (
        not supplied_phone
        or not registered_phone
        or supplied_phone != registered_phone
    ):
        raise HTTPException(
            status_code=403,
            detail="The phone number does not match this request.",
        )

    clarification = (
        db.query(RequestClarification)
        .filter(RequestClarification.request_id == id)
        .order_by(RequestClarification.id.desc())
        .first()
    )

    if not clarification:
        raise HTTPException(
            status_code=404,
            detail="No clarification has been requested for this request.",
        )

    return _clarification_payload(clarification)


@router.post("/{id}/duplicate-clarification/respond")
def respond_to_duplicate_clarification(
    id: int,
    payload: CitizenDuplicateClarificationResponseInput,
    db: Session = Depends(get_db),
):
    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")

    supplied_phone = _normalise_clarification_phone(payload.phone)
    registered_phone = _normalise_clarification_phone(req.reporter_phone)

    if (
        not supplied_phone
        or not registered_phone
        or supplied_phone != registered_phone
    ):
        raise HTTPException(
            status_code=403,
            detail="The phone number does not match this request.",
        )

    response_text = payload.response.strip()
    if not response_text:
        raise HTTPException(
            status_code=400,
            detail="Please enter a response.",
        )

    clarification = (
        db.query(RequestClarification)
        .filter(
            RequestClarification.request_id == id,
            RequestClarification.status == "PENDING",
        )
        .order_by(RequestClarification.id.desc())
        .first()
    )

    if not clarification:
        latest = (
            db.query(RequestClarification)
            .filter(RequestClarification.request_id == id)
            .order_by(RequestClarification.id.desc())
            .first()
        )

        if latest and latest.status == "ANSWERED":
            return _clarification_payload(latest)

        raise HTTPException(
            status_code=409,
            detail="There is no pending clarification to answer.",
        )

    # Conditional update: only the first response can claim PENDING.
    # A later website/SMS response cannot overwrite the saved answer.
    updated = (
        db.query(RequestClarification)
        .filter(
            RequestClarification.id == clarification.id,
            RequestClarification.status == "PENDING",
        )
        .update(
            {
                RequestClarification.status: "ANSWERED",
                RequestClarification.response: response_text,
                RequestClarification.response_channel: "WEBSITE",
                RequestClarification.responded_at: datetime.now(IST),
                RequestClarification.updated_at: datetime.now(IST),
            },
            synchronize_session=False,
        )
    )

    if not updated:
        db.rollback()
        latest = (
            db.query(RequestClarification)
            .filter(RequestClarification.id == clarification.id)
            .first()
        )
        if latest and latest.status == "ANSWERED":
            return _clarification_payload(latest)

        raise HTTPException(
            status_code=409,
            detail="The clarification could not be answered. Refresh and try again.",
        )

    db.commit()

    clarification = (
        db.query(RequestClarification)
        .filter(RequestClarification.id == clarification.id)
        .first()
    )

    return _clarification_payload(clarification)

@router.get("/{id}/duplicate-clarification/authority")
def get_authority_duplicate_clarification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.EMERGENCY_COORDINATOR])
    ),
):
    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found."
        )

    clarification = (
        db.query(RequestClarification)
        .filter(RequestClarification.request_id == id)
        .order_by(RequestClarification.id.desc())
        .first()
    )

    if not clarification:
        raise HTTPException(
            status_code=404,
            detail="No clarification exists for this request."
        )

    return _clarification_payload(clarification)

# ============================================================
# AUTHORITY DUPLICATE REVIEW
# ============================================================

@router.post(
    "/{id}/duplicate-review",
    response_model=CommunityRequestResponse
)
def review_duplicate(
    id: int,
    payload: VerifyRequestInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.EMERGENCY_COORDINATOR])
)
):
    action = payload.action.strip().upper()

    allowed_actions = {
        "CONFIRM_DUPLICATE",
        "MARK_NOT_DUPLICATE",
        "REQUEST_CLARIFICATION",
    }

    if action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid duplicate review action. Use "
                "CONFIRM_DUPLICATE, MARK_NOT_DUPLICATE "
                "or REQUEST_CLARIFICATION."
            )
        )

    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    if req.status != RequestStatus.FLAGGED_DUPLICATE:
        raise HTTPException(
            status_code=409,
            detail="Only flagged duplicate requests can be reviewed here."
        )

    previous_review = (
        db.query(RequestVerification)
        .filter(RequestVerification.request_id == req.id)
        .order_by(RequestVerification.id.desc())
        .first()
    )

    if not previous_review:
        raise HTTPException(
            status_code=409,
            detail="Duplicate detection history was not found."
        )

    if action == "CONFIRM_DUPLICATE":
        if not payload.duplicate_of_id:
            raise HTTPException(
                status_code=400,
                detail="Select the original request before confirming a duplicate."
            )

        if payload.duplicate_of_id == req.id:
            raise HTTPException(
                status_code=400,
                detail="A request cannot be a duplicate of itself."
            )

        original = (
            db.query(CommunityRequest)
            .filter(
                CommunityRequest.id == payload.duplicate_of_id
            )
            .first()
        )

        if not original:
            raise HTTPException(
                status_code=404,
                detail="Original request not found."
            )

        req.status = RequestStatus.FLAGGED_DUPLICATE

    elif action == "MARK_NOT_DUPLICATE":
        req.status = RequestStatus.PENDING

    # REQUEST_CLARIFICATION deliberately leaves the request flagged.
    # It cannot proceed through normal allocation or approval.

    verification = RequestVerification(
        request_id=req.id,
        verified_by_id=current_user.id,
        is_duplicate=(action == "CONFIRM_DUPLICATE"),
        duplicate_of_id=(
            payload.duplicate_of_id
            if action == "CONFIRM_DUPLICATE"
            else previous_review.duplicate_of_id
        ),
        similarity_score=previous_review.similarity_score,
        notes=payload.notes,
        action_taken=action
    )

    db.add(verification)
    db.flush()

    log_audit_event(
        db=db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=(
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        ),
        action=f"DUPLICATE_REVIEW_{action}",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=RequestStatus.FLAGGED_DUPLICATE.value,
        new_state=req.status.value,
        reason=payload.notes
    )
    if action in {"CONFIRM_DUPLICATE", "MARK_NOT_DUPLICATE"}:
        latest_clarification = (
            db.query(RequestClarification)
            .filter(RequestClarification.request_id == req.id)
            .order_by(RequestClarification.id.desc())
            .first()
        )

        if latest_clarification:
            latest_clarification.status = "CLOSED"
            latest_clarification.decision = action
            latest_clarification.reviewed_by_id = current_user.id
            latest_clarification.reviewed_at = datetime.now(IST)
    db.commit()
    db.refresh(req)

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
        reporter_name=request_in.reporter_name or "Citizen Mobile User",
        reporter_phone=request_in.reporter_phone,
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
        request_type=request_in.request_type or "SUPPLIES",
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

@router.post("/sms-clarification-status")
def check_sms_clarification_status(
    payload: dict,
    db: Session = Depends(get_db),
):
    phone = str(payload.get("phone") or "").strip()
    sender_digits = _normalise_clarification_phone(phone)

    if not sender_digits:
        return {"eligible": False, "reason": "invalid_phone"}

    pending_clarifications = (
        db.query(RequestClarification, CommunityRequest)
        .join(
            CommunityRequest,
            CommunityRequest.id == RequestClarification.request_id,
        )
        .filter(RequestClarification.status == "PENDING")
        .all()
    )

    matches = [
        clarification
        for clarification, req in pending_clarifications
        if _normalise_clarification_phone(req.reporter_phone)
        == sender_digits
    ]

    if len(matches) == 1:
        return {"eligible": True}

    if len(matches) > 1:
        return {"eligible": False, "reason": "multiple_pending"}

    return {"eligible": False, "reason": "no_pending"}


# ============================================================
# INBOUND SMS GATEWAY WEBHOOK & PARSER
# ============================================================

@router.post(
    "/sms-inbound",
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
    # Clarification replies must never enter emergency-request parsing.
    if body.upper().startswith("RF:CLAR|"):
        parts = body.split("|", 2)

        if len(parts) != 3:
            raise HTTPException(
                status_code=400,
                detail="Invalid clarification reply format."
            )

        reply_code = parts[1].strip().upper()
        response_text = parts[2].strip()

        if not reply_code or not response_text:
            raise HTTPException(
                status_code=400,
                detail="Clarification code and response are required."
            )

        clarification = (
            db.query(RequestClarification)
            .filter(RequestClarification.reply_code == reply_code)
            .first()
        )

        if not clarification:
            raise HTTPException(
                status_code=404,
                detail="Clarification code not found."
            )

        req = (
            db.query(CommunityRequest)
            .filter(CommunityRequest.id == clarification.request_id)
            .first()
        )

        if not req:
            raise HTTPException(
                status_code=404,
                detail="Associated request not found."
            )

        sender_digits = _normalise_clarification_phone(sender)
        registered_digits = _normalise_clarification_phone(
            req.reporter_phone
        )

        if (
            not sender_digits
            or not registered_digits
            or sender_digits != registered_digits
        ):
            raise HTTPException(
                status_code=403,
                detail="Sender does not match the registered request phone."
            )

        # If already answered, preserve the first response.
        if clarification.status == "ANSWERED":
            return _clarification_payload(clarification)

        if clarification.status != "PENDING":
            raise HTTPException(
                status_code=409,
                detail="This clarification is no longer accepting responses."
            )

        # Conditional update prevents two channels from overwriting each other.
        updated = (
            db.query(RequestClarification)
            .filter(
                RequestClarification.id == clarification.id,
                RequestClarification.status == "PENDING",
            )
            .update(
                {
                    RequestClarification.status: "ANSWERED",
                    RequestClarification.response: response_text,
                    RequestClarification.response_channel: "SMS",
                    RequestClarification.responded_at: datetime.now(IST),
                    RequestClarification.updated_at: datetime.now(IST),
                },
                synchronize_session=False,
            )
        )

        if not updated:
            db.rollback()
            latest = (
                db.query(RequestClarification)
                .filter(RequestClarification.id == clarification.id)
                .first()
            )

            if latest and latest.status == "ANSWERED":
                return _clarification_payload(latest)

            raise HTTPException(
                status_code=409,
                detail="Clarification response could not be saved. Please retry."
            )

        db.commit()

        saved = (
            db.query(RequestClarification)
            .filter(RequestClarification.id == clarification.id)
            .first()
        )

        return _clarification_payload(saved)

    # Match ordinary SMS replies to a pending clarification by registered phone.
    # Keep structured SOS and supply messages on their existing path.
    if not body.startswith("RF:SOS|") and not body.startswith("RF:SUP|"):
        sender_digits = _normalise_clarification_phone(sender)

        if sender_digits:
            pending_clarifications = (
                db.query(RequestClarification, CommunityRequest)
                .join(
                    CommunityRequest,
                    CommunityRequest.id == RequestClarification.request_id,
                )
                .filter(RequestClarification.status == "PENDING")
                .order_by(RequestClarification.id.desc())
                .all()
            )

            matching_clarifications = [
                (clarification, req)
                for clarification, req in pending_clarifications
                if _normalise_clarification_phone(req.reporter_phone)
                == sender_digits
            ]

            if len(matching_clarifications) == 1:
                clarification, req = matching_clarifications[0]

                updated = (
                    db.query(RequestClarification)
                    .filter(
                        RequestClarification.id == clarification.id,
                        RequestClarification.status == "PENDING",
                    )
                    .update(
                        {
                            RequestClarification.status: "ANSWERED",
                            RequestClarification.response: body,
                            RequestClarification.response_channel: "SMS",
                            RequestClarification.responded_at: datetime.now(IST),
                            RequestClarification.updated_at: datetime.now(IST),
                        },
                        synchronize_session=False,
                    )
                )

                if not updated:
                    db.rollback()
                    raise HTTPException(
                        status_code=409,
                        detail="Clarification response could not be saved. Please retry.",
                    )

                db.commit()
                saved = (
                    db.query(RequestClarification)
                    .filter(RequestClarification.id == clarification.id)
                    .first()
                )
                return _clarification_payload(saved)

            if len(matching_clarifications) > 1:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Multiple pending clarifications match this phone number. "
                        "Please reply using the RF:CLAR|CODE|answer format."
                    ),
                )

    # Never parse an ordinary Android SMS as a new emergency request
    # if it was forwarded specifically as a clarification reply.
    if payload.get("source") == "android_clarification_reply":
        return {
            "status": "IGNORED",
            "reason": "no_pending_clarification",
        }

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
            location_name=(
                f"GPS ({lat:.5f}, {lon:.5f}) [SMS from {sender}]"
                if lat is not None and lon is not None
                else f"Location unavailable [SMS from {sender}]"
            ),
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





# ============================================================
# APPROVE EVACUATION REQUEST
# ============================================================


@router.post(
    "/{id}/approve-evacuation",
    response_model=CommunityRequestResponse
)
def approve_evacuation(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = (
        db.query(CommunityRequest)
        .filter(CommunityRequest.id == id)
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )
    if req.status == RequestStatus.FLAGGED_DUPLICATE:
        raise HTTPException(
            status_code=409,
            detail="This request is under duplicate review and cannot be approved."
        )

    if req.request_type != "EVACUATION":
        raise HTTPException(
            status_code=400,
            detail="Only evacuation requests can be approved here"
        )

    if req.status == RequestStatus.REJECTED:
        raise HTTPException(
            status_code=400,
            detail="Rejected request cannot be approved"
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE EVACUATION RESPONSE
    # --------------------------------------------------------

    existing_allocation = (
        db.query(Allocation)
        .filter(
            Allocation.request_id == req.id
        )
        .first()
    )

    if existing_allocation:
        req.status = RequestStatus.ALLOCATED
        db.commit()
        db.refresh(req)
        return req

    # --------------------------------------------------------
    # EVACUATION REQUEST MUST HAVE A DESTINATION
    # --------------------------------------------------------

    if req.latitude is None or req.longitude is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Evacuation request must have valid "
                "location coordinates."
            )
        )

    # --------------------------------------------------------
    # SELECT AN ACTIVE WAREHOUSE
    #
    # This does NOT allocate or consume inventory.
    # The warehouse is only used as the origin required
    # by the existing Delivery model.
    # --------------------------------------------------------

    warehouses = (
        db.query(Warehouse)
        .filter(
            Warehouse.is_active == True
        )
        .all()
    )

    if not warehouses:
        raise HTTPException(
            status_code=409,
            detail="No active warehouse is available for response operations."
        )

    warehouse = min(
        warehouses,
        key=lambda w: (
            (w.latitude - req.latitude) ** 2
            +
            (w.longitude - req.longitude) ** 2
        )
    )

    # --------------------------------------------------------
    # CREATE RESPONSE ALLOCATION
    #
    # No AllocationItems are created because evacuation
    # does not consume relief inventory.
    # --------------------------------------------------------

    relief_id = (
        f"{req.tracking_code}-EVAC"
    )

    allocation = Allocation(
        request_id=req.id,
        warehouse_id=warehouse.id,
        relief_id=relief_id,
        status="APPROVED",
        ai_score=(
            req.authority_override_score
            if req.authority_override_score is not None
            else req.priority_score
        ),
        ai_rationale=(
            "Evacuation response approved by "
            +
            (
                current_user.full_name
                if current_user
                else "Command"
            )
            +
            "."
        ),
        is_partial=False,
        approved_by_id=(
            current_user.id
            if current_user
            else None
        ),
        approved_at=datetime.utcnow(),
        override_notes=None
    )

    db.add(allocation)
    db.flush()

    # --------------------------------------------------------
    # CREATE RESPONSE OPERATION
    # --------------------------------------------------------

    delivery = Delivery(
        relief_id=relief_id,
        allocation_id=allocation.id,
        vehicle_id=None,
        driver_name=None,
        driver_phone=None,
        origin_warehouse_id=warehouse.id,
        destination_location_name=req.location_name,
        destination_lat=req.latitude,
        destination_lon=req.longitude,
        status=ReliefStatus.ALLOCATED,
        dispatched_at=None,
        estimated_delivery_at=None,
        notes=(
            "Evacuation response approved. "
            "Awaiting response-unit assignment and dispatch."
        )
    )

    db.add(delivery)

    # --------------------------------------------------------
    # MOVE REQUEST OUT OF PRIORITY RELIEF REQUESTS
    # --------------------------------------------------------

    previous_status = (
        req.status.value
        if hasattr(req.status, "value")
        else str(req.status)
    )

    req.status = RequestStatus.ALLOCATED

    db.commit()
    db.refresh(req)

    # --------------------------------------------------------
    # AUDIT
    # --------------------------------------------------------

    log_audit_event(
        db=db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=(
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        ),
        action="APPROVE_EVACUATION",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=previous_status,
        new_state="ALLOCATED",
        reason="Evacuation response approved and created"
    )

    return req
