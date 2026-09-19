import datetime
import json
import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from typing import List

from app.database import get_db

from app.models import (
    CommunityRequest,
    Warehouse,
    Inventory,
    Allocation,
    AllocationItem,
    Delivery,
    Vehicle,
    Route,
    RequestStatus,
    ReliefStatus,
    User
)

from app.schemas import (
    AIResourceMatchRecommendation,
    AIFacilitySupportRecommendation,
    ApproveAllocationRequest,
    AllocationResponse
)

from app.auth import (
    get_current_user,
    log_audit_event
)

from app.ai.resource_matcher import (
    match_resources_for_request
)

from app.ai.facility_matcher import (
    match_facilities_for_request
)


router = APIRouter(
    prefix="/allocations",
    tags=["Resource Allocations"]
)


# ============================================================
# LIST ALLOCATIONS
# ============================================================

@router.get(
    "",
    response_model=List[AllocationResponse]
)
def list_allocations(
    db: Session = Depends(get_db)
):
    return (
        db.query(Allocation)
        .order_by(
            Allocation.created_at.desc()
        )
        .all()
    )


# ============================================================
# AI RESOURCE MATCHING
# ============================================================

@router.get(
    "/recommend/{request_id}",
    response_model=AIResourceMatchRecommendation
)
def get_match_recommendation(
    request_id: int,
    db: Session = Depends(get_db)
):
    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == request_id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    warehouses = (
        db.query(Warehouse)
        .filter(
            Warehouse.is_active == True
        )
        .all()
    )

    # --------------------------------------------------------
    # INVENTORY TRUST FILTER
    #
    # AI matching is allowed to use ONLY inventory that:
    # 1. Belongs to an active warehouse
    # 2. Is explicitly VERIFIED
    # 3. Has available quantity > 0
    #
    # UNKNOWN / EXPIRED inventory is ignored.
    # --------------------------------------------------------

    verified_inventory_warehouse_ids = {
        inv.warehouse_id
        for inv in (
            db.query(Inventory)
            .filter(
                Inventory.verification_status == "VERIFIED",
                Inventory.available_quantity > 0
            )
            .all()
        )
    }

    warehouses = [
        warehouse
        for warehouse in warehouses
        if warehouse.id
        in verified_inventory_warehouse_ids
    ]

    return match_resources_for_request(
        req,
        warehouses
    )


# ============================================================
# PUBLIC FACILITY SUPPORT
# ============================================================

@router.get(
    "/facility-support/{request_id}",
    response_model=AIFacilitySupportRecommendation
)
async def get_facility_support_recommendation(
    request_id: int,
    db: Session = Depends(get_db)
):
    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == request_id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    public_data_url = (
        "http://127.0.0.1:8000"
        "/api/public-data/facilities"
    )

    params = {
        "region": "nashik",
        "facility_type": "all"
    }

    try:
        async with httpx.AsyncClient(
            timeout=140.0
        ) as client:

            response = await client.get(
                public_data_url,
                params=params
            )

        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to retrieve public facility data: "
                + str(exc)
            )
        )

    data = response.json()

    facilities = data.get(
        "facilities",
        []
    )

    return match_facilities_for_request(
        request=req,
        facilities=facilities
    )


# ============================================================
# PROCUREMENT MANIFEST
# ============================================================

@router.post(
    "/procurement-manifest/{request_id}"
)
def create_procurement_manifest(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Creates a procurement manifest when VERIFIED
    warehouse inventory cannot satisfy a request.

    IMPORTANT:
    - Does NOT invent inventory.
    - Does NOT deduct warehouse stock.
    - Does NOT assign a vehicle.
    - Does NOT dispatch anything.
    - UNKNOWN / EXPIRED inventory is ignored.
    """

    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id == request_id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    warehouses = (
        db.query(Warehouse)
        .filter(
            Warehouse.is_active == True
        )
        .all()
    )

    # --------------------------------------------------------
    # INVENTORY TRUST FILTER
    #
    # Procurement analysis must only consider stock that
    # has been explicitly verified.
    # --------------------------------------------------------

    verified_inventory_warehouse_ids = {
        inv.warehouse_id
        for inv in (
            db.query(Inventory)
            .filter(
                Inventory.verification_status == "VERIFIED",
                Inventory.available_quantity > 0
            )
            .all()
        )
    }

    warehouses = [
        warehouse
        for warehouse in warehouses
        if warehouse.id
        in verified_inventory_warehouse_ids
    ]

    recommendation = (
        match_resources_for_request(
            req,
            warehouses
        )
    )

    if not recommendation.remaining_shortages:
        raise HTTPException(
            status_code=400,
            detail=(
                "No procurement shortage exists "
                "for this request."
            )
        )

    manifest_id = (
        "PROC-2026-"
        + f"{req.id:05d}"
    )

    items = []

    for shortage in (
        recommendation.remaining_shortages
    ):
        items.append({
            "category":
                shortage.get(
                    "category",
                    "Not reported"
                ),

            "item_name":
                shortage.get(
                    "item_name",
                    "Not reported"
                ),

            "quantity":
                float(
                    shortage.get(
                        "shortage",
                        0
                    )
                ),

            "unit":
                shortage.get(
                    "unit",
                    "units"
                )
        })

    manifest = {
        "manifest_id":
            manifest_id,

        "manifest_type":
            "PROCUREMENT",

        "status":
            "PENDING_PROCUREMENT",

        "request_id":
            req.id,

        "request_tracking_code":
            req.tracking_code,

        "location_name":
            req.location_name,

        "latitude":
            req.latitude,

        "longitude":
            req.longitude,

        "affected_people":
            req.affected_people,

        "priority_classification":
            recommendation.priority_classification,

        "priority_score":
            recommendation.priority_score,

        "items":
            items,

        "source":
            "ResQFlow AI verified shortage analysis",

        "inventory_deducted":
            False,

        "vehicle_assigned":
            False,

        "dispatch_status":
            "NOT_DISPATCHED",

        "created_at":
            datetime.datetime.utcnow().isoformat()
    }

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
            else "Authority Commander"
        ),

        actor_role="AUTHORITY",

        action=
            "CREATE_PROCUREMENT_MANIFEST",

        entity_type=
            "PROCUREMENT_MANIFEST",

        entity_id=
            manifest_id,

        previous_state=
            "UNMET_REQUIREMENT",

        new_state=
            json.dumps({
                "status":
                    "PENDING_PROCUREMENT",

                "items":
                    items,

                "inventory_deducted":
                    False
            }),

        reason=(
            "Procurement manifest created for "
            "verified unmet requirements at "
            + req.location_name
        )
    )

    db.commit()

    return manifest


# ============================================================
# APPROVE ALLOCATION
# ============================================================

@router.post(
    "/approve",
    response_model=AllocationResponse
)
def approve_allocation(
    payload: ApproveAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    req = (
        db.query(CommunityRequest)
        .filter(
            CommunityRequest.id ==
            payload.request_id
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    warehouse = (
        db.query(Warehouse)
        .filter(
            Warehouse.id ==
            payload.warehouse_id
        )
        .first()
    )

    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail="Warehouse not found"
        )

    # --------------------------------------------------------
    # Verify that allocation items were actually provided.
    # --------------------------------------------------------

    if not payload.items:
        raise HTTPException(
            status_code=400,
            detail=(
                "No inventory items were provided "
                "for allocation."
            )
        )

    relief_id = (
        payload.relief_id
        or
        "RELIEF-2026-"
        + f"{req.id:05d}"
    )

    existing_alloc = (
        db.query(Allocation)
        .filter(
            Allocation.relief_id ==
            relief_id
        )
        .first()
    )

    if existing_alloc:
        return existing_alloc

    allocation = Allocation(
        request_id=req.id,
        warehouse_id=warehouse.id,
        relief_id=relief_id,
        status="APPROVED",
        ai_score=(
            req.authority_override_score
            if req.authority_override_score
            is not None
            else req.priority_score
        ),
        ai_rationale=(
            "Authority "
            +
            (
                current_user.full_name
                if current_user
                else "Command"
            )
            +
            " approved verified inventory "
            "from "
            +
            warehouse.name
            +
            "."
        ),
        is_partial=False,
        approved_by_id=(
            current_user.id
            if current_user
            else None
        ),
        approved_at=
            datetime.datetime.utcnow(),
        override_notes=
            payload.override_notes
    )

    db.add(allocation)

    db.flush()

    total_requested_units = 0.0
    total_allocated_units = 0.0

    allocation_items_created = 0

    # --------------------------------------------------------
    # Process every requested allocation item
    # --------------------------------------------------------

    for item_data in payload.items:

        category = str(
            item_data.get(
                "category",
                ""
            )
        ).strip()

        item_name = str(
            item_data.get(
                "item_name",
                ""
            )
        ).strip()

        requested_alloc_qty = float(
            item_data.get(
                "allocated_quantity",
                0
            )
        )

        unit = str(
            item_data.get(
                "unit",
                "units"
            )
        ).strip()

        if requested_alloc_qty <= 0:
            continue

        # ----------------------------------------------------
        # FIND MATCHING INVENTORY
        #
        # HARD SAFETY RULE:
        # Only VERIFIED inventory with available stock
        # can ever be allocated.
        # ----------------------------------------------------

        inv_query = (
            db.query(Inventory)
            .filter(
                Inventory.warehouse_id ==
                warehouse.id,

                Inventory.verification_status ==
                "VERIFIED",

                Inventory.available_quantity >
                0
            )
        )

        # Match item name when supplied.
        if item_name:
            inv_query = inv_query.filter(
                Inventory.item_name.ilike(
                    "%" +
                    item_name +
                    "%"
                )
            )

        # Match category when supplied.
        if category:
            inv_query = inv_query.filter(
                Inventory.category.ilike(
                    "%" +
                    category +
                    "%"
                )
            )

        inv = inv_query.first()

        # ----------------------------------------------------
        # NO VERIFIED INVENTORY
        # ----------------------------------------------------

        if not inv:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No VERIFIED available inventory "
                    "for "
                    +
                    (
                        item_name
                        or category
                        or "requested item"
                    )
                    +
                    " is available at "
                    +
                    warehouse.name
                    +
                    ". Unknown or unverified stock "
                    "cannot be allocated. Create a "
                    "procurement manifest instead."
                )
            )

        # ----------------------------------------------------
        # VERIFY QUANTITY
        # ----------------------------------------------------

        if (
            inv.available_quantity
            <
            requested_alloc_qty
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Insufficient VERIFIED inventory "
                    "for "
                    +
                    item_name
                    +
                    ". Available: "
                    +
                    str(
                        inv.available_quantity
                    )
                    +
                    " "
                    +
                    inv.unit
                    +
                    ". Required: "
                    +
                    str(
                        requested_alloc_qty
                    )
                    +
                    " "
                    +
                    unit
                )
            )

        # ----------------------------------------------------
        # LOCK VERIFIED INVENTORY
        # ----------------------------------------------------

        inv.available_quantity -= (
            requested_alloc_qty
        )

        inv.allocated_quantity += (
            requested_alloc_qty
        )

        allocation_item = AllocationItem(
            allocation_id=
                allocation.id,

            category=
                category,

            item_name=
                item_name
                or
                inv.item_name,

            requested_quantity=
                requested_alloc_qty,

            allocated_quantity=
                requested_alloc_qty,

            unit=
                unit
        )

        db.add(
            allocation_item
        )

        allocation_items_created += 1

        # ----------------------------------------------------
        # UPDATE REQUEST FULFILLMENT
        # ----------------------------------------------------

        for req_item in req.items:

            if (
                category.lower()
                in
                req_item.category.lower()
            ):
                remaining_for_item = max(
                    0.0,
                    req_item.requested_quantity
                    -
                    req_item.fulfilled_quantity
                )

                fulfilled_now = min(
                    remaining_for_item,
                    requested_alloc_qty
                )

                req_item.fulfilled_quantity += (
                    fulfilled_now
                )

                total_requested_units += (
                    req_item.requested_quantity
                )

                total_allocated_units += (
                    req_item.fulfilled_quantity
                )

                break

    # --------------------------------------------------------
    # Ensure at least one valid inventory item was allocated
    # --------------------------------------------------------

    if allocation_items_created == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "No valid VERIFIED inventory items "
                "were available for allocation."
            )
        )

    # --------------------------------------------------------
    # Determine request status
    # --------------------------------------------------------

    request_is_fully_fulfilled = True

    for req_item in req.items:

        if (
            req_item.fulfilled_quantity
            <
            req_item.requested_quantity
        ):
            request_is_fully_fulfilled = False
            break

    if request_is_fully_fulfilled:

        req.status = (
            RequestStatus.ALLOCATED
        )

        allocation.is_partial = False

    else:

        req.status = (
            RequestStatus.PARTIALLY_FULFILLED
        )

        allocation.is_partial = True

    # --------------------------------------------------------
    # CREATE DELIVERY RECORD
    #
    # IMPORTANT:
    # This does NOT dispatch the vehicle.
    # --------------------------------------------------------

    existing_delivery = (
        db.query(Delivery)
        .filter(
            Delivery.allocation_id ==
            allocation.id
        )
        .first()
    )

    if not existing_delivery:

        delivery = Delivery(
            relief_id=
                relief_id,

            allocation_id=
                allocation.id,

            vehicle_id=
                None,

            driver_name=
                None,

            driver_phone=
                None,

            origin_warehouse_id=
                warehouse.id,

            destination_location_name=
                req.location_name,

            destination_lat=
                req.latitude,

            destination_lon=
                req.longitude,

            status=
                ReliefStatus.ALLOCATED,

            dispatched_at=
                None,

            estimated_delivery_at=
                None,

            notes=(
                "Allocation approved and "
                "inventory locked. "
                "Awaiting logistics dispatch."
            )
        )

        db.add(
            delivery
        )

        db.flush()

        # ----------------------------------------------------
        # GENERATE ROUTE PLAN ONLY
        #
        # Do NOT assign a vehicle yet.
        # ----------------------------------------------------

        route = Route(
            delivery_id=
                delivery.id,

            waypoints_json=
                json.dumps([
                    {
                        "lat":
                            warehouse.latitude,

                        "lon":
                            warehouse.longitude,

                        "name":
                            warehouse.name
                    },

                    {
                        "lat":
                            (
                                warehouse.latitude
                                +
                                req.latitude
                            )
                            / 2,

                        "lon":
                            (
                                warehouse.longitude
                                +
                                req.longitude
                            )
                            / 2,

                        "name":
                            "Route Checkpoint"
                    },

                    {
                        "lat":
                            req.latitude,

                        "lon":
                            req.longitude,

                        "name":
                            req.location_name
                    }
                ]),

            total_distance_km=
                round(
                    abs(
                        req.latitude
                        -
                        warehouse.latitude
                    )
                    * 111.0
                    +
                    abs(
                        req.longitude
                        -
                        warehouse.longitude
                    )
                    * 90.0,
                    1
                ),

            estimated_time_mins=
                45,

            avoids_flooded_bridges=
                True
        )

        db.add(
            route
        )

    # --------------------------------------------------------
    # COMMIT INVENTORY LOCK + ALLOCATION
    # --------------------------------------------------------

    db.commit()

    db.refresh(
        allocation
    )

    # --------------------------------------------------------
    # AUDIT
    # --------------------------------------------------------

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
            else "Authority Commander"
        ),

        actor_role=
            "AUTHORITY",

        action=
            "APPROVE_ALLOCATION",

        entity_type=
            "ALLOCATION",

        entity_id=
            relief_id,

        previous_state=
            "PENDING_ALLOCATION",

        new_state=
            json.dumps({
                "status":
                    "APPROVED",

                "warehouse":
                    warehouse.name,

                "partial":
                    allocation.is_partial,

                "vehicle_assigned":
                    False,

                "dispatch_status":
                    "NOT_DISPATCHED"
            }),

        reason=(
            "Approved verified relief allocation "
            "for "
            +
            req.location_name
            +
            " ("
            +
            req.tracking_code
            +
            "). Inventory locked; dispatch "
            "requires separate logistics approval."
        )
    )

    return allocation