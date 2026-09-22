import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db

from app.models import (
    Donation,
    DonationItem,
    Delivery,
    Allocation,
    CommunityRequest,
    ReliefStatus,
    User
)

from app.schemas import (
    DonationCreate,
    DonationResponse,
    ReliefTraceResponse,
    TimelineStep
)

from app.auth import (
    get_current_user,
    log_audit_event
)


router = APIRouter(
    prefix="/donations",
    tags=["Donations & Transparency"]
)


@router.get(
    "",
    response_model=List[DonationResponse]
)
def list_donations(
    db: Session = Depends(get_db)
):
    return (
        db.query(Donation)
        .order_by(
            Donation.created_at.desc()
        )
        .all()
    )


@router.post(
    "",
    response_model=DonationResponse
)
def create_donation(
    donation_in: DonationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(
        get_current_user
    )
):
    count = (
        db.query(Donation).count()
        + 10284
    )

    tracking_id = f"D-{count}"

    relief_id = (
        f"RELIEF-2026-0"
        f"{count % 1000:03d}"
    )

    donation = Donation(
        donor_id=(
            current_user.id
            if current_user
            else None
        ),
        donor_name=
            donation_in.donor_name,
        donor_email=
            donation_in.donor_email,
        tracking_id=
            tracking_id,
        relief_id=
            relief_id,
        target_zone_id=
            donation_in.target_zone_id,
        status=
            ReliefStatus.DONATED,
        notes=
            donation_in.notes
    )

    db.add(donation)
    db.flush()

    for it in donation_in.items:

        db_it = DonationItem(
            donation_id=
                donation.id,
            category=
                it.category,
            item_name=
                it.item_name,
            quantity=
                it.quantity,
            unit=
                it.unit
        )

        db.add(db_it)

    db.commit()
    db.refresh(donation)

    log_audit_event(
        db=db,
        actor_id=(
            current_user.id
            if current_user
            else None
        ),
        actor_name=
            donation.donor_name,
        actor_role=
            "DONOR",
        action=
            "CREATE_DONATION",
        entity_type=
            "DONATION",
        entity_id=
            donation.tracking_id,
        previous_state=
            None,
        new_state=
            f"Relief ID: {relief_id}",
        reason=
            "Citizen relief contribution pledged"
    )

    return donation


@router.get(
    "/{identifier}/trace",
    response_model=ReliefTraceResponse
)
def trace_relief_package(
    identifier: str,
    db: Session = Depends(get_db)
):

    clean_id = (
        identifier
        .strip()
        .upper()
    )

    # ========================================================
    # FIND DONATION
    # ========================================================

    donation = (
        db.query(Donation)
        .filter(
            (Donation.relief_id == clean_id)
            |
            (Donation.tracking_id == clean_id)
        )
        .first()
    )

    # ========================================================
    # FIND DELIVERY
    # ========================================================

    delivery = (
        db.query(Delivery)
        .filter(
            Delivery.relief_id == clean_id
        )
        .first()
    )

    if donation and not delivery:

        delivery = (
            db.query(Delivery)
            .filter(
                Delivery.relief_id ==
                donation.relief_id
            )
            .first()
        )

    # ========================================================
    # FIND ALLOCATION + REQUEST
    # ========================================================

    allocation = None
    request = None

    if delivery:

        allocation = (
            delivery.allocation
        )

        if allocation:
            request = (
                allocation.request
            )

    # ========================================================
    # FIND ALLOCATION DIRECTLY
    # ========================================================

    if not delivery and not allocation:

        allocation = (
            db.query(Allocation)
            .filter(
                Allocation.relief_id ==
                clean_id
            )
            .first()
        )

        if allocation:

            request = (
                allocation.request
            )

            delivery = (
                allocation.delivery
            )

    # ========================================================
    # FIND COMMUNITY REQUEST
    # ========================================================

    if not request:

        request = (
            db.query(CommunityRequest)
            .filter(
                CommunityRequest.tracking_code ==
                clean_id
            )
            .first()
        )

        if (
            request
            and
            request.allocations
        ):

            allocation = (
                request.allocations[0]
            )

            delivery = (
                allocation.delivery
            )

    # ========================================================
    # NOTHING FOUND
    # ========================================================

    if (
        not donation
        and
        not delivery
        and
        not allocation
        and
        not request
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                f"No relief journey record found "
                f"for identifier '{clean_id}'"
            )
        )

    # ========================================================
    # ITEMS SUMMARY
    # ========================================================

    items_summary = []

    if (
        allocation
        and
        allocation.items
    ):

        for item in allocation.items:

            items_summary.append({
                "category":
                    item.category,
                "item_name":
                    item.item_name,
                "quantity":
                    item.allocated_quantity,
                "unit":
                    item.unit
            })

    elif (
        donation
        and
        donation.items
    ):

        for item in donation.items:

            items_summary.append({
                "category":
                    item.category,
                "item_name":
                    item.item_name,
                "quantity":
                    item.quantity,
                "unit":
                    item.unit
            })

    elif (
        request
        and
        request.items
    ):

        for item in request.items:

            items_summary.append({
                "category":
                    item.category,
                "item_name":
                    item.item_name,
                "quantity":
                    item.requested_quantity,
                "unit":
                    item.unit
            })

    # ========================================================
    # CURRENT STATUS
    # ========================================================

    if delivery:

        current_status = (
            delivery.status
        )

    elif allocation:

        current_status = (
            ReliefStatus.ALLOCATED
        )

    elif donation:

        current_status = (
            donation.status
        )

    else:

        current_status = (
            ReliefStatus.DONATED
        )

    # ========================================================
    # STATUS ORDER
    #
    # IMPORTANT:
    # Each timeline stage uses its EXACT status index.
    #
    # 0 = DONATED
    # 1 = RECEIVED
    # 2 = VERIFIED
    # 3 = STORED
    # 4 = ALLOCATED
    # 5 = DISPATCHED
    # 6 = IN_TRANSIT
    # 7 = DELIVERED / COMMUNITY HANDOVER
# 8 = COMPLETED
    # ========================================================

    status_order = [
        ReliefStatus.DONATED,
        ReliefStatus.RECEIVED,
        ReliefStatus.VERIFIED,
        ReliefStatus.STORED,
        ReliefStatus.ALLOCATED,
        ReliefStatus.DISPATCHED,
        ReliefStatus.IN_TRANSIT,
        ReliefStatus.DELIVERED
    ]

    is_request_only = (
        request is not None
        and donation is None
        and allocation is None
        and delivery is None
    )

    current_idx = (
        status_order.index(
            current_status
        )
        if current_status in status_order
        else -1
    )

    # ========================================================
    # BASE created_at
    # ========================================================

    base_time = (
        donation.created_at
        if donation
        else (
            request.created_at
            if request
            else datetime.datetime.utcnow()
        )
    )

    # ========================================================
    # TIMELINE
    # ========================================================

    timeline_steps = [

        # ====================================================
        # 0. DONATED / COMMUNITY NEED
        # ====================================================

        TimelineStep(
            step="DONATED",

            label=(
                "Community Need Registered"
                if is_request_only
                else "Pledged by Donor"
            ),

            status=(
                "CURRENT"
                if is_request_only
                else (
                    "COMPLETED"
                    if current_idx > 0
                    else (
                        "CURRENT"
                        if current_idx == 0
                        else "PENDING"
                    )
                )
            ),

            created_at=(
                base_time.strftime(
                    "%b %d, %H:%M"
                )
                if (
                    is_request_only
                    or
                    current_idx >= 0
                )
                else None
            ),

            actor=(
                "Community Request System"
                if is_request_only
                else (
                    donation.donor_name
                    if donation
                    else None
                )
            ),

            details=(
                "Community relief requirement registered "
                "and awaiting verified allocation."
                if is_request_only
                else
                "Relief pledge registered in central "
                "transparent ledger."
            )
        ),

        # ====================================================
        # 1. RECEIVED
        # ====================================================

        TimelineStep(
            step="RECEIVED",

            label="Received at Warehouse",

            status=(
                "COMPLETED"
                if current_idx > 1
                else (
                    "CURRENT"
                    if current_idx == 1
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=1.2
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 1
                else None
            ),

            actor=(
                "Warehouse Inflow Inspector"
                if current_idx >= 1
                else None
            ),

            details=(
                "Cargo verified, scanned, and physical "
                "condition authenticated."
                if current_idx >= 1
                else None
            )
        ),

        # ====================================================
        # 2. VERIFIED
        # ====================================================

        TimelineStep(
            step="VERIFIED",

            label="Quality & Batch Verified",

            status=(
                "COMPLETED"
                if current_idx > 2
                else (
                    "CURRENT"
                    if current_idx == 2
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=1.8
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 2
                else None
            ),

            actor=(
                "Relief Quality Officer"
                if current_idx >= 2
                else None
            ),

            details=(
                "Lot numbers and expiration dates certified "
                "safe for consumption."
                if current_idx >= 2
                else None
            )
        ),

        # ====================================================
        # 3. STORED
        # ====================================================

        TimelineStep(
            step="STORED",

            label="Stored in Warehouse",

            status=(
                "COMPLETED"
                if current_idx > 3
                else (
                    "CURRENT"
                    if current_idx == 3
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=2.4
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 3
                else None
            ),

            actor=(
                "Inventory Controller"
                if current_idx >= 3
                else None
            ),

            details=(
                f"Stored at "
                f"{allocation.warehouse.name}."
                if (
                    current_idx >= 3
                    and
                    allocation
                    and
                    allocation.warehouse
                )
                else None
            )
        ),

        # ====================================================
        # 4. ALLOCATED
        # ====================================================

        TimelineStep(
            step="ALLOCATED",

            label="AI Matched & Authority Approved",

            status=(
                "COMPLETED"
                if current_idx > 4
                else (
                    "CURRENT"
                    if current_idx == 4
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=3.5
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 4
                else None
            ),

            actor=(
                "Emergency Operations Authority"
                if current_idx >= 4
                else None
            ),

            details=(
                f"Matched to "
                f"{request.location_name}."
                if (
                    current_idx >= 4
                    and
                    request
                )
                else None
            )
        ),

        # ====================================================
        # 5. DISPATCHED
        # ====================================================

        TimelineStep(
            step="DISPATCHED",

            label="Loaded & Manifest Issued",

            status=(
                "COMPLETED"
                if current_idx > 5
                else (
                    "CURRENT"
                    if current_idx == 5
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=4.2
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 5
                else None
            ),

            actor=(
                "Logistics Dispatcher"
                if current_idx >= 5
                else None
            ),

            details=(
                (
                    f"Loaded onto "
                    f"{delivery.vehicle.vehicle_type}."
                )
                if (
                    current_idx >= 5
                    and
                    delivery
                    and
                    delivery.vehicle
                )
                else (
                    "Relief vehicle dispatched from "
                    "the approved warehouse."
                    if current_idx >= 5
                    else None
                )
            )
        ),

        # ====================================================
        # 6. IN TRANSIT
        # ====================================================

        TimelineStep(
            step="IN_TRANSIT",

            label="In Transit",

            status=(
                "COMPLETED"
                if current_idx > 6
                else (
                    "CURRENT"
                    if current_idx == 6
                    else "PENDING"
                )
            ),

            created_at=(
                (
                    base_time
                    +
                    datetime.timedelta(
                        hours=4.9
                    )
                ).strftime(
                    "%b %d, %H:%M"
                )
                if current_idx >= 6
                else None
            ),

            actor=(
                delivery.driver_name
                if (
                    delivery
                    and
                    delivery.driver_name
                )
                else (
                    "Logistics Dispatcher"
                    if current_idx >= 6
                    else None
                )
            ),

            details=(
                "Delivery is being transported to "
                "the verified destination."
                if current_idx >= 6
                else None
            )
        ),

        # ====================================================
        # 7. VERIFIED COMMUNITY HANDOVER
        # ====================================================

        TimelineStep(
            step="DELIVERED",

            label="Verified Community Handover",

            status=(
                "COMPLETED"
                if current_idx >= 7
                else "PENDING"
            ),

            created_at=(
                delivery.delivered_at.strftime(
                    "%b %d, %H:%M"
                )
                if (
                    delivery
                    and
                    delivery.delivered_at
                )
                else None
            ),

            actor=(
                "Community Representative"
                if current_idx >= 7
                else None
            ),

            details=(
                f"Relief received at "
                f"{request.location_name}."
                if (
                    current_idx >= 7
                    and
                    request
                )
                else None
            )
        ),

        # ====================================================
        # 8. COMPLETED
        # ====================================================

        TimelineStep(
            step="COMPLETED",

            label="Delivery Completed",

            status=(
                "COMPLETED"
                if current_idx >= 7
                else "PENDING"
            ),

            created_at=(
                delivery.delivered_at.strftime(
                    "%b %d, %H:%M"
                )
                if (
                    delivery
                    and
                    delivery.delivered_at
                )
                else None
            ),

            actor=(
                "Relief Operations System"
                if current_idx >= 7
                else None
            ),

            details=(
                "Delivery completed with verified "
                "handover evidence and recipient confirmation."
                if current_idx >= 7
                else None
            )
        )
    ]

    # ========================================================
    # PROOF OF DELIVERY
    # ========================================================

    proof = None

    if (
        current_idx >= 7
        and
        delivery
    ):

        proof = {
            "delivered_at": (
                delivery.delivered_at.isoformat()
                if delivery.delivered_at
                else None
            ),

            "recipient_signature": (
                delivery.recipient_signature
                if delivery.recipient_signature
                else None
            ),

            "proof_photo_url": (
                delivery.proof_photo_url
                if delivery.proof_photo_url
                else None
            ),

            "notes": (
                delivery.notes
                if delivery.notes
                else None
            )
        }

    # ========================================================
    # RESPONSE
    # ========================================================

    return ReliefTraceResponse(

        relief_id=
            clean_id,

        donation_id=(
            donation.tracking_id
            if donation
            else None
        ),

        donor_name=(
            donation.donor_name
            if donation
            else None
        ),

        request_tracking_code=(
            request.tracking_code
            if request
            else None
        ),

        destination_location=(
            request.location_name
            if request
            else "Not reported"
        ),

        destination_zone=(
            request.zone.name
            if request
            and request.zone
            else "Not reported"
        ),

        current_status=
            current_status,

        people_supported=(
            request.affected_people
            if request
            else 0
        ),

        items_summary=
            items_summary,

        origin_warehouse=(
            allocation.warehouse.name
            if (
                allocation
                and
                allocation.warehouse
            )
            else None
        ),

        assigned_vehicle=(
            delivery.vehicle.code
            if (
                delivery
                and
                delivery.vehicle
            )
            else None
        ),

        driver_contact=(
            delivery.driver_phone
            if delivery
            else None
        ),

        timeline=
            timeline_steps,

        proof_of_delivery=
            proof
    )