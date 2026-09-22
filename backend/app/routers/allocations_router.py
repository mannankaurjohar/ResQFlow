
import json
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
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
    response_model=List[AllocationResponse]
)
def approve_allocation(
    payload: ApproveAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    # ========================================================
    # FIND REQUEST
    # ========================================================

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

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if not payload.items:
        raise HTTPException(
            status_code=400,
            detail=(
                "No warehouse allocation groups "
                "were provided."
            )
        )

    allocations_created = []

    # ========================================================
    # PROCESS EACH WAREHOUSE
    # ========================================================

    for warehouse_group in payload.items:

        warehouse = (
            db.query(Warehouse)
            .filter(
                Warehouse.id ==
                warehouse_group.warehouse_id
            )
            .first()
        )

        if not warehouse:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Warehouse not found: "
                    +
                    str(
                        warehouse_group.warehouse_id
                    )
                )
            )

        if not warehouse_group.items:
            continue

        # ----------------------------------------------------
        # UNIQUE RELIEF ID PER ALLOCATION
        #
        # FR-1049 remains the request tracking code.
        # Each warehouse allocation gets its own internal
        # relief identifier.
        # ----------------------------------------------------

        allocation_number = (
            len(allocations_created) + 1
        )

        base_relief_id = (
            payload.relief_id
            or
            req.tracking_code
            or
            "RELIEF-2026-"
            +
            f"{req.id:05d}"
        )

        relief_id = (
            f"{base_relief_id}-A{allocation_number}"
        )

        # ----------------------------------------------------
# CHECK FOR EXISTING ALLOCATION
# ----------------------------------------------------

        # ----------------------------------------------------
# CHECK FOR EXISTING ALLOCATION
# ----------------------------------------------------

        # ----------------------------------------------------
        # CREATE ALLOCATION
        # ----------------------------------------------------

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
                datetime.utcnow(),

            override_notes=
                payload.override_notes
        )

        db.add(allocation)

        db.flush()

        allocation_items_created = 0

        # ====================================================
        # PROCESS ITEMS FOR THIS WAREHOUSE
        # ====================================================

        for item_data in warehouse_group.items:

            category = str(
                item_data.category
            ).strip()

            item_name = str(
                item_data.item_name
            ).strip()

            requested_alloc_qty = float(
                item_data.allocated_quantity
            )

            unit = str(
                item_data.unit
            ).strip()

            if requested_alloc_qty <= 0:
                continue

            # ------------------------------------------------
            # FIND VERIFIED INVENTORY
            # ------------------------------------------------

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

            # Exact item-name match first
            inv = None

            if item_name:

                inv = (
                    inv_query
                    .filter(
                        Inventory.item_name.ilike(
                            item_name
                        )
                    )
                    .first()
                )

            # Partial item-name match
            if not inv and item_name:

                inv = (
                    inv_query
                    .filter(
                        Inventory.item_name.ilike(
                            "%" +
                            item_name +
                            "%"
                        )
                    )
                    .first()
                )

            # Category fallback
            if not inv and category:

                inv = (
                    inv_query
                    .filter(
                        Inventory.category.ilike(
                            "%" +
                            category +
                            "%"
                        )
                    )
                    .first()
                )

            # ------------------------------------------------
            # NO VERIFIED INVENTORY
            # ------------------------------------------------

            if not inv:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "No VERIFIED available "
                        "inventory for "
                        +
                        (
                            item_name
                            or
                            category
                            or
                            "requested item"
                        )
                        +
                        " at "
                        +
                        warehouse.name
                        +
                        ". Unknown or unverified "
                        "stock cannot be allocated."
                    )
                )

            # ------------------------------------------------
            # VERIFY QUANTITY
            # ------------------------------------------------

            if (
                inv.available_quantity
                <
                requested_alloc_qty
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Insufficient VERIFIED "
                        "inventory for "
                        +
                        item_name
                        +
                        " at "
                        +
                        warehouse.name
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

            # ------------------------------------------------
            # LOCK INVENTORY
            # ------------------------------------------------

            inv.available_quantity -= (
                requested_alloc_qty
            )

            inv.allocated_quantity += (
                requested_alloc_qty
            )

            # ------------------------------------------------
            # CREATE ALLOCATION ITEM
            # ------------------------------------------------

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

            # ------------------------------------------------
            # UPDATE REQUEST FULFILLMENT
            # ------------------------------------------------

            remaining_to_fulfill = (
                requested_alloc_qty
            )

            for req_item in req.items:

                if remaining_to_fulfill <= 0:
                    break

                category_matches = (
                    category.lower()
                    in
                    req_item.category.lower()
                )

                name_matches = (
                    not item_name
                    or
                    item_name.lower()
                    in
                    req_item.item_name.lower()
                    or
                    req_item.item_name.lower()
                    in
                    item_name.lower()
                )

                if (
                    category_matches
                    and
                    name_matches
                ):

                    remaining_for_item = max(
                        0.0,

                        req_item.requested_quantity
                        -
                        req_item.fulfilled_quantity
                    )

                    fulfilled_now = min(
                        remaining_for_item,
                        remaining_to_fulfill
                    )

                    req_item.fulfilled_quantity += (
                        fulfilled_now
                    )

                    remaining_to_fulfill -= (
                        fulfilled_now
                    )

        # ====================================================
        # VALIDATE ALLOCATION
        # ====================================================

        if allocation_items_created == 0:

            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid VERIFIED inventory "
                    "items were allocated from "
                    +
                    warehouse.name
                    +
                    "."
                )
            )

        # ====================================================
        # DETERMINE WHETHER THIS ALLOCATION IS PARTIAL
        # ====================================================

        allocation.is_partial = False

        for allocation_item in (
            db.query(AllocationItem)
            .filter(
                AllocationItem.allocation_id ==
                allocation.id
            )
            .all()
        ):

            if (
                allocation_item.allocated_quantity
                <
                allocation_item.requested_quantity
            ):
                allocation.is_partial = True
                break

        # ====================================================
        # CREATE DELIVERY
        # ====================================================

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

        db.add(delivery)

        db.flush()

        # ====================================================
        # CREATE ROUTE PLAN
        # ====================================================

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

        db.add(route)

        allocations_created.append(
            allocation
        )

    # ========================================================
    # ENSURE AT LEAST ONE ALLOCATION WAS CREATED
    # ========================================================

    if not allocations_created:

        raise HTTPException(
            status_code=409,
            detail=(
                "No new allocations were created. "
                "The requested allocations may "
                "already exist."
            )
        )

    # ========================================================
    # DETERMINE REQUEST STATUS
    # ========================================================

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

    else:

        req.status = (
            RequestStatus.PARTIALLY_FULFILLED
        )

    # ========================================================
    # COMMIT EVERYTHING TOGETHER
    # ========================================================

    db.commit()

    # ========================================================
    # REFRESH ALLOCATIONS
    # ========================================================

    for allocation in allocations_created:

        db.refresh(
            allocation
        )

    # ========================================================
    # AUDIT LOG
    # ========================================================

    warehouse_names = [
        allocation.warehouse.name
        for allocation
        in allocations_created
    ]

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
            "APPROVE_MULTI_WAREHOUSE_ALLOCATION",

        entity_type=
            "COMMUNITY_REQUEST",

        entity_id=
            req.tracking_code,

        previous_state=
            "PENDING_ALLOCATION",

        new_state=
            json.dumps({
                "status":
                    req.status.value
                    if hasattr(
                        req.status,
                        "value"
                    )
                    else str(
                        req.status
                    ),

                "warehouses":
                    warehouse_names,

                "allocation_count":
                    len(
                        allocations_created
                    ),

                "vehicle_assigned":
                    False,

                "dispatch_status":
                    "NOT_DISPATCHED"
            }),

        reason=(
            "Approved verified relief allocation "
            "across "
            +
            str(
                len(
                    allocations_created
                )
            )
            +
            " warehouse(s) for "
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

    db.commit()

    return allocations_created