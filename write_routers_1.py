import os

ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "backend", "app", "routers")

# 1. auth_router.py
auth_router_code = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserLogin, Token, UserResponse
from app.auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        # Check by email
        user = db.query(User).filter(User.email == login_data.username).first()
        
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
    )
    return Token(access_token=access_token, token_type="bearer", user=user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/demo-users", response_model=List[UserResponse])
def get_demo_users(db: Session = Depends(get_db)):
    # Returns the pre-seeded role accounts for 1-click role switching in the hackathon demo
    return db.query(User).filter(User.is_active == True).all()
"""

with open(os.path.join(ROUTERS_DIR, "auth_router.py"), "w", encoding="utf-8") as f:
    f.write(auth_router_code)

print("auth_router.py written")

# 2. requests_router.py
requests_router_code = """import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import (
    CommunityRequest, RequestItem, RequestVerification, AffectedZone,
    User, UserRole, RequestStatus, SeverityLevel
)
from app.schemas import (
    CommunityRequestCreate, CommunityRequestResponse, AIUnderstandingResponse,
    ExplainPriorityResponse, OverridePriorityRequest, VerifyRequestInput
)
from app.auth import get_current_user, log_audit_event
from app.ai.nlp_parser import parse_natural_language_request
from app.ai.priority_engine import calculate_priority_score, explain_priority
from app.ai.duplicate_detector import detect_duplicates

router = APIRouter(prefix="/requests", tags=["Community Requests"])

@router.post("/parse-nlp", response_model=AIUnderstandingResponse)
def parse_natural_language(payload: dict):
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    return parse_natural_language_request(text)

@router.get("", response_model=List[CommunityRequestResponse])
def list_requests(
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    zone_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CommunityRequest)
    if status:
        query = query.filter(CommunityRequest.status == status)
    if urgency:
        query = query.filter(CommunityRequest.urgency == urgency)
    if zone_id:
        query = query.filter(CommunityRequest.zone_id == zone_id)
        
    return query.order_by(CommunityRequest.priority_score.desc()).all()

@router.post("", response_model=CommunityRequestResponse)
def create_request(
    request_in: CommunityRequestCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # 1. Generate tracking code
    count = db.query(CommunityRequest).count() + 1048
    tracking_code = f"FR-{count}"

    # 2. Match zone if not provided
    zone = None
    if request_in.zone_id:
        zone = db.query(AffectedZone).filter(AffectedZone.id == request_in.zone_id).first()
    else:
        # Default or proximity zone
        zone = db.query(AffectedZone).first()

    # 3. Create request object
    new_req = CommunityRequest(
        tracking_code=tracking_code,
        zone_id=zone.id if zone else None,
        reporter_name=request_in.reporter_name or "Anonymous Citizen",
        reporter_phone=request_in.reporter_phone,
        reporter_role=request_in.reporter_role or "Citizen",
        location_name=request_in.location_name,
        latitude=request_in.latitude,
        longitude=request_in.longitude,
        affected_people=request_in.affected_people,
        affected_households=request_in.affected_households,
        vulnerable_elderly=request_in.vulnerable_elderly,
        vulnerable_children=request_in.vulnerable_children,
        vulnerable_infants=request_in.vulnerable_infants,
        vulnerable_pregnant=request_in.vulnerable_pregnant,
        urgency=request_in.urgency,
        raw_description=request_in.raw_description,
        status=RequestStatus.PENDING
    )
    db.add(new_req)
    db.flush() # get ID

    # 4. Add items
    for it in request_in.items:
        db_it = RequestItem(
            request_id=new_req.id,
            category=it.category,
            item_name=it.item_name,
            requested_quantity=it.requested_quantity,
            unit=it.unit
        )
        db.add(db_it)
    db.flush()

    # 5. Run AI Priority Engine
    score, classification, factors = calculate_priority_score(new_req, zone=zone, waiting_hours=0.5)
    new_req.priority_score = score
    new_req.priority_classification = classification
    new_req.priority_factors_json = json.dumps(factors)

    # 6. Run AI Duplicate Detector
    existing = db.query(CommunityRequest).filter(CommunityRequest.id != new_req.id).all()
    is_dup, candidate, sim_score, reason = detect_duplicates(new_req, existing)

    if is_dup and candidate:
        new_req.status = RequestStatus.FLAGGED_DUPLICATE
        verif = RequestVerification(
            request_id=new_req.id,
            is_duplicate=True,
            duplicate_of_id=candidate.id,
            similarity_score=sim_score,
            notes=reason,
            action_taken="FLAGGED"
        )
        db.add(verif)

    db.commit()
    db.refresh(new_req)

    # 7. Audit log
    actor_name = current_user.full_name if current_user else "Public Citizen"
    actor_role = current_user.role.value if current_user and hasattr(current_user.role, 'value') else "COMMUNITY"
    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=actor_name,
        actor_role=actor_role,
        action="CREATE_REQUEST",
        entity_type="COMMUNITY_REQUEST",
        entity_id=new_req.tracking_code,
        previous_state=None,
        new_state=json.dumps({"status": new_req.status.value if hasattr(new_req.status, 'value') else str(new_req.status), "score": score}),
        reason=f"Community request filed from {new_req.location_name}"
    )

    return new_req

@router.get("/{id}", response_model=CommunityRequestResponse)
def get_request(id: int, db: Session = Depends(get_db)):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.get("/{id}/priority", response_model=ExplainPriorityResponse)
def get_priority_explanation(id: int, db: Session = Depends(get_db)):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return explain_priority(req)

@router.post("/{id}/override-priority", response_model=ExplainPriorityResponse)
def override_priority(
    id: int,
    payload: OverridePriorityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    old_score = req.priority_score
    req.authority_override_score = payload.override_score
    req.override_reason = payload.override_reason
    req.override_by = current_user.full_name

    db.commit()
    db.refresh(req)

    log_audit_event(
        db=db,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action="OVERRIDE_PRIORITY",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=f"Score: {old_score}",
        new_state=f"Override Score: {payload.override_score}",
        reason=payload.override_reason
    )

    return explain_priority(req)

@router.post("/{id}/verify", response_model=CommunityRequestResponse)
def verify_request(
    id: int,
    payload: VerifyRequestInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    action = payload.action.upper()
    if action == "APPROVED":
        req.status = RequestStatus.VERIFIED
    elif action == "MERGED":
        req.status = RequestStatus.VERIFIED
    elif action == "REJECTED":
        req.status = RequestStatus.REJECTED

    verif = RequestVerification(
        request_id=req.id,
        verified_by_id=current_user.id if current_user else None,
        is_duplicate=action == "MERGED",
        duplicate_of_id=payload.duplicate_of_id,
        similarity_score=1.0 if action == "MERGED" else 0.0,
        notes=payload.notes,
        action_taken=action
    )
    db.add(verif)
    db.commit()
    db.refresh(req)

    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=current_user.full_name if current_user else "Volunteer",
        actor_role=current_user.role.value if current_user and hasattr(current_user.role, 'value') else "VOLUNTEER",
        action=f"VERIFY_{action}",
        entity_type="COMMUNITY_REQUEST",
        entity_id=req.tracking_code,
        previous_state=None,
        new_state=req.status.value if hasattr(req.status, 'value') else str(req.status),
        reason=payload.notes
    )

    return req
"""

with open(os.path.join(ROUTERS_DIR, "requests_router.py"), "w", encoding="utf-8") as f:
    f.write(requests_router_code)

print("requests_router.py written")
