from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    User,
    UserRole,
    CommunityRequest,
    ResponseUnit,
    ResponseAssignment,
)
from ..auth import get_current_user


router = APIRouter(
    prefix="/response-units",
    tags=["Response Units"],
)
print("RESQFLOW RESPONSE UNITS ROUTER LOADED")

# ============================================================
# Schemas
# ============================================================

class ResponseUnitCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    unit_type: str = Field(..., min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=150)
    members: int = Field(default=1, ge=1)
    operator_id: int


class AssignResponseTaskRequest(BaseModel):
    request_id: int


class UpdateTaskStatusRequest(BaseModel):
    status: str = Field(..., min_length=1, max_length=40)
    field_remarks: str | None = None
    people_assisted: int = Field(default=0, ge=0)
    people_rescued: int = Field(default=0, ge=0)
    shelter_destination: str | None = Field(
        default=None,
        max_length=150,
    )


# ============================================================
# Helper
# ============================================================

def require_coordinator(current_user: User):
    allowed_roles = {
        UserRole.ADMIN,
        UserRole.EMERGENCY_COORDINATOR,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Only an Emergency Coordinator or Admin can perform this action",
        )


def require_operator(current_user: User):
    if current_user.role != UserRole.RESPONSE_UNIT_OPERATOR:
        raise HTTPException(
            status_code=403,
            detail="Only a Response Unit Operator can perform this action",
        )


# ============================================================
# List Response Units
# ============================================================

@router.get("")
def get_response_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    units = (
        db.query(ResponseUnit)
        .order_by(ResponseUnit.id.desc())
        .all()
    )

    return [
        {
            "id": unit.id,
            "name": unit.name,
            "unit_type": unit.unit_type,
            "location": unit.location,
            "members": unit.members,
            "operator_id": unit.operator_id,
            "status": unit.status,
        }
        for unit in units
    ]


# ============================================================
# Create Response Unit
# ============================================================

@router.post("")
def create_response_unit(
    payload: ResponseUnitCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_coordinator(current_user)

    operator = (
        db.query(User)
        .filter(
            User.id == payload.operator_id,
            User.role == UserRole.RESPONSE_UNIT_OPERATOR,
            User.is_active == True,
        )
        .first()
    )

    if not operator:
        raise HTTPException(
            status_code=404,
            detail="Active Response Unit Operator not found",
        )

    existing_unit = (
        db.query(ResponseUnit)
        .filter(
            ResponseUnit.operator_id == payload.operator_id
        )
        .first()
    )

    if existing_unit:
        raise HTTPException(
            status_code=400,
            detail="This operator is already assigned to a response unit",
        )

    unit = ResponseUnit(
        name=payload.name,
        unit_type=payload.unit_type,
        location=payload.location,
        members=payload.members,
        operator_id=payload.operator_id,
        status="AVAILABLE",
    )

    db.add(unit)
    db.commit()
    db.refresh(unit)

    return {
        "id": unit.id,
        "name": unit.name,
        "unit_type": unit.unit_type,
        "location": unit.location,
        "members": unit.members,
        "operator_id": unit.operator_id,
        "status": unit.status,
    }


# ============================================================
# Assign REAL Community Request to Response Unit
# ============================================================

@router.post("/{unit_id}/assign")
def assign_response_task(
    unit_id: int,
    payload: AssignResponseTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_coordinator(current_user)

    # --------------------------------------------------------
    # Find the response unit
    # --------------------------------------------------------

    unit = (
        db.query(ResponseUnit)
        .filter(ResponseUnit.id == unit_id)
        .first()
    )

    if not unit:
        raise HTTPException(
            status_code=404,
            detail="Response unit not found",
        )

    # --------------------------------------------------------
    # Find the REAL citizen/community report
    # --------------------------------------------------------

    request = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == payload.request_id
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Community request not found",
        )

    # --------------------------------------------------------
    # Prevent duplicate active assignment
    # --------------------------------------------------------

    existing_assignment = (
        db.query(ResponseAssignment)
        .filter(
            ResponseAssignment.request_id == request.id,
            ResponseAssignment.status.notin_(
                ["COMPLETED", "CANCELLED"]
            ),
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="This request is already assigned to a response unit",
        )

    # --------------------------------------------------------
    # Create REAL assignment
    # --------------------------------------------------------

    assignment = ResponseAssignment(
        request_id=request.id,
        response_unit_id=unit.id,
        assigned_by_id=current_user.id,
        status="ASSIGNED",
        assigned_at=datetime.utcnow(),
    )

    db.add(assignment)

    # Mark the unit as assigned
    unit.status = "ASSIGNED"

    db.commit()
    db.refresh(assignment)

    return {
        "message": "Response task assigned successfully",
        "assignment": {
            "id": assignment.id,
            "request_id": assignment.request_id,
            "response_unit_id": assignment.response_unit_id,
            "assigned_by_id": assignment.assigned_by_id,
            "status": assignment.status,
            "assigned_at": assignment.assigned_at,
        },
        "request": {
            "id": request.id,
            "tracking_code": request.tracking_code,
            "location_name": request.location_name,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "affected_people": request.affected_people,
            "affected_households": request.affected_households,
            "urgency": (
                request.urgency.value
                if hasattr(request.urgency, "value")
                else str(request.urgency)
            ),
            "priority_score": request.priority_score,
            "raw_description": request.raw_description,
            "request_type": request.request_type,
            "medical_emergency": request.medical_emergency,
            "immediate_danger": request.immediate_danger,
        },
        "response_unit": {
            "id": unit.id,
            "name": unit.name,
            "unit_type": unit.unit_type,
            "operator_id": unit.operator_id,
        },
    }


# ============================================================
# ============================================================
# Track REAL Community Request
# ============================================================

@router.get("/track/{request_ref}")
def track_response_request(
    request_ref: str,
    db: Session = Depends(get_db),
):
    """
    Public tracking endpoint.

    request_ref may be:
    - the real CommunityRequest.id
    - the real CommunityRequest.tracking_code

    All returned response-unit information comes directly
    from the database.
    """

    request = None

    # Real numeric request ID
    if request_ref.isdigit():
        request = (
            db.query(CommunityRequest)
            .filter(
                CommunityRequest.id == int(request_ref)
            )
            .first()
        )

    # Or real tracking code
    if not request:
        request = (
            db.query(CommunityRequest)
            .filter(
                CommunityRequest.tracking_code == request_ref
            )
            .first()
        )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Community request not found",
        )

    assignment = (
        db.query(ResponseAssignment)
        .filter(
            ResponseAssignment.request_id == request.id
        )
        .order_by(ResponseAssignment.assigned_at.desc())
        .first()
    )

    unit = assignment.response_unit if assignment else None

    request_status = (
        request.status.value
        if hasattr(request.status, "value")
        else str(request.status or "")
    ).upper()

    assignment_status = (
        assignment.status.upper()
        if assignment
        else None
    )

    # The response-unit lifecycle is driven by the REAL
    # ResponseAssignment status. Before assignment, the
    # CommunityRequest status is used.
    lifecycle = [
        ("SUBMITTED", "Submitted"),
        ("VERIFIED", "Verified"),
        ("APPROVED", "Approved"),
        ("ASSIGNED", "Response Unit Assigned"),
        ("ACCEPTED", "Accepted"),
        ("IN_TRANSIT", "In Transit"),
        ("ON_SCENE", "On Scene"),
        ("RESPONDING", "Responding"),
        ("COMPLETED", "Completed"),
    ]

    request_rank = {
        "SUBMITTED": 0,
        "PENDING": 0,
        "VERIFIED": 1,
        "APPROVED": 2,
        "ALLOCATED": 2,
    }

    assignment_rank = {
        "ASSIGNED": 3,
        "ACCEPTED": 4,
        "IN_TRANSIT": 5,
        "ON_SCENE": 6,
        "RESPONDING": 7,
        "COMPLETED": 8,
    }

    if assignment_status in assignment_rank:
        current_rank = assignment_rank[assignment_status]
        current_status = assignment_status
    else:
        if (
            request_status == "DELIVERED"
            or (
                assignment is not None
                and assignment.completed_at is not None
            )
        ):
            current_rank = len(lifecycle)
        else:
            current_rank = request_rank.get(request_status, 0)

        current_status = request_status or "SUBMITTED"

    timestamps = {
        "SUBMITTED": request.created_at,
        "VERIFIED": None,
        "APPROVED": None,
        "ASSIGNED": assignment.assigned_at if assignment else None,
        "ACCEPTED": assignment.accepted_at if assignment else None,
        "IN_TRANSIT": None,
        "ON_SCENE": None,
        "RESPONDING": None,
        "COMPLETED": assignment.completed_at if assignment else None,
    }

    timeline = []

    for index, (status_key, label) in enumerate(lifecycle):
        if index < current_rank:
            state = "COMPLETED"
        elif index == current_rank:
            state = "CURRENT"
        else:
            state = "PENDING"

        timeline.append({
            "status": status_key,
            "label": label,
            "state": state,
            "created_at": timestamps.get(status_key),
        })

    return {
        "request": {
            "id": request.id,
            "tracking_code": request.tracking_code,
            "status": request_status,
            "location_name": request.location_name,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "affected_people": request.affected_people,
            "affected_households": request.affected_households,
            "urgency": (
                request.urgency.value
                if hasattr(request.urgency, "value")
                else str(request.urgency)
            ),
            "priority_score": request.priority_score,
            "priority_classification": (
                request.priority_classification.value
                if hasattr(
                    request.priority_classification,
                    "value",
                )
                else str(request.priority_classification)
            ),
            "request_type": request.request_type,
            "medical_emergency": request.medical_emergency,
            "immediate_danger": request.immediate_danger,
            "raw_description": request.raw_description,
            "created_at": request.created_at,
        },

        "response": {
            "current_status": current_status,
            "assignment_id": assignment.id if assignment else None,
            "assigned_at": assignment.assigned_at if assignment else None,
            "accepted_at": assignment.accepted_at if assignment else None,
            "completed_at": assignment.completed_at if assignment else None,
            "field_remarks": (
                assignment.field_remarks
                if assignment
                else None
            ),
            "people_assisted": (
                assignment.people_assisted
                if assignment
                else 0
            ),
            "people_rescued": (
                assignment.people_rescued
                if assignment
                else 0
            ),
            "shelter_destination": (
                assignment.shelter_destination
                if assignment
                else None
            ),
        },

        "response_unit": (
            {
                "id": unit.id,
                "name": unit.name,
                "unit_type": unit.unit_type,
                "location": unit.location,
                "members": unit.members,
                "status": unit.status,
            }
            if unit
            else None
        ),

        "timeline": timeline,
    }

# Get Tasks for Logged-in Response Unit Operator
# ============================================================

@router.get("/my-tasks")
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_operator(current_user)

    unit = (
        db.query(ResponseUnit)
        .filter(
            ResponseUnit.operator_id == current_user.id
        )
        .first()
    )

    if not unit:
        return []

    assignments = (
        db.query(ResponseAssignment)
        .filter(
            ResponseAssignment.response_unit_id == unit.id
        )
        .order_by(
            ResponseAssignment.assigned_at.desc()
        )
        .all()
    )

    results = []

    for assignment in assignments:
        request = assignment.request

        results.append({
            "assignment": {
                "id": assignment.id,
                "status": assignment.status,
                "assigned_at": assignment.assigned_at,
                "accepted_at": assignment.accepted_at,
                "completed_at": assignment.completed_at,
                "field_remarks": assignment.field_remarks,
                "people_assisted": assignment.people_assisted,
                "people_rescued": assignment.people_rescued,
                "shelter_destination": assignment.shelter_destination,
            },
            "request": {
                "id": request.id,
                "tracking_code": request.tracking_code,
                "reporter_name": request.reporter_name,
                "reporter_phone": request.reporter_phone,
                "location_name": request.location_name,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "affected_people": request.affected_people,
                "affected_households": request.affected_households,
                "vulnerable_elderly": request.vulnerable_elderly,
                "vulnerable_children": request.vulnerable_children,
                "vulnerable_infants": request.vulnerable_infants,
                "vulnerable_pregnant": request.vulnerable_pregnant,
                "urgency": (
                    request.urgency.value
                    if hasattr(request.urgency, "value")
                    else str(request.urgency)
                ),
                "priority_score": request.priority_score,
                "priority_classification": (
                    request.priority_classification.value
                    if hasattr(
                        request.priority_classification,
                        "value",
                    )
                    else str(request.priority_classification)
                ),
                "raw_description": request.raw_description,
                "request_type": request.request_type,
                "medical_emergency": request.medical_emergency,
                "immediate_danger": request.immediate_danger,
                "danger_details_json": request.danger_details_json,
                "photo_url": request.photo_url,
                "created_at": request.created_at,
            },
            "response_unit": {
                "id": unit.id,
                "name": unit.name,
                "unit_type": unit.unit_type,
                "location": unit.location,
                "members": unit.members,
            },
        })

    return results


# ============================================================
# Update Task Status
# ============================================================

@router.patch("/tasks/{assignment_id}/status")
def update_task_status(
    assignment_id: int,
    payload: UpdateTaskStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_operator(current_user)

    unit = (
        db.query(ResponseUnit)
        .filter(
            ResponseUnit.operator_id == current_user.id
        )
        .first()
    )

    if not unit:
        raise HTTPException(
            status_code=404,
            detail="No response unit assigned to this operator",
        )

    assignment = (
        db.query(ResponseAssignment)
        .filter(
            ResponseAssignment.id == assignment_id,
            ResponseAssignment.response_unit_id == unit.id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assigned task not found",
        )

    allowed_transitions = {
        "ASSIGNED": ["ACCEPTED"],
        "ACCEPTED": ["IN_TRANSIT"],
        "IN_TRANSIT": ["ON_SCENE"],
        "ON_SCENE": ["RESPONDING"],
        "RESPONDING": ["COMPLETED"],
        "COMPLETED": [],
    }

    current_status = assignment.status
    new_status = payload.status.upper()

    if new_status not in allowed_transitions.get(
        current_status,
        [],
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{current_status} â†’ {new_status}"
            ),
        )

    assignment.status = new_status

    if new_status == "ACCEPTED":
        assignment.accepted_at = datetime.utcnow()

    if new_status == "COMPLETED":
        assignment.completed_at = datetime.utcnow()

        assignment.field_remarks = (
            payload.field_remarks
        )

        assignment.people_assisted = (
            payload.people_assisted
        )

        assignment.people_rescued = (
            payload.people_rescued
        )

        assignment.shelter_destination = (
            payload.shelter_destination
        )

        unit.status = "AVAILABLE"

    elif new_status in {
        "IN_TRANSIT",
        "ON_SCENE",
        "RESPONDING",
    }:
        unit.status = "BUSY"

    db.commit()
    db.refresh(assignment)

    return {
        "message": "Task status updated successfully",
        "assignment_id": assignment.id,
        "status": assignment.status,
        "accepted_at": assignment.accepted_at,
        "completed_at": assignment.completed_at,
    }
