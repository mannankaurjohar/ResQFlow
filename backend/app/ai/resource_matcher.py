import math
from typing import List, Dict, Any

from app.models import CommunityRequest, Warehouse
from app.ai.duplicate_detector import haversine_distance_km
from app.schemas import (
    AIResourceMatchRecommendation,
    MatchedWarehouseItem
)


def match_resources_for_request(
    request: CommunityRequest,
    warehouses: List[Warehouse]
) -> AIResourceMatchRecommendation:

    recommendations: List[MatchedWarehouseItem] = []
    remaining_shortages: List[Dict[str, Any]] = []

    is_partial = False
    rationale_points: List[str] = []

    # =========================================================
    # 1. CALCULATE DISTANCE FOR EVERY ACTIVE WAREHOUSE
    # =========================================================

    warehouses_with_distance = []

    for warehouse in warehouses:

        if not warehouse.is_active:
            continue

        if (
            warehouse.latitude is None
            or warehouse.longitude is None
        ):
            continue

        distance_km = haversine_distance_km(
            request.latitude,
            request.longitude,
            warehouse.latitude,
            warehouse.longitude
        )

        warehouses_with_distance.append(
            (warehouse, distance_km)
        )

    # Nearest warehouse first
    warehouses_with_distance.sort(
        key=lambda x: x[1]
    )

    # =========================================================
    # 2. PROCESS EACH REQUESTED ITEM INDEPENDENTLY
    # =========================================================

    for request_item in request.items:

        needed_quantity = (
            request_item.requested_quantity
            - request_item.fulfilled_quantity
        )

        if needed_quantity <= 0:
            continue

        fulfilled_quantity = 0.0

        # -----------------------------------------------------
        # Search nearest → farthest
        # -----------------------------------------------------

        for warehouse, distance_km in warehouses_with_distance:

            if fulfilled_quantity >= needed_quantity:
                break

            # -------------------------------------------------
            # ONLY VERIFIED AVAILABLE INVENTORY
            # -------------------------------------------------

            matching_inventory = []

            for inventory in warehouse.inventory:

                if (
                    inventory.verification_status
                    != "VERIFIED"
                ):
                    continue

                if inventory.available_quantity <= 0:
                    continue

                # -------------------------------------------------
                # Match requested item.
                #
                # First preference:
                # exact item name.
                #
                # Second preference:
                # category match.
                # -------------------------------------------------

                item_name_match = (
                    inventory.item_name.strip().lower()
                    ==
                    request_item.item_name.strip().lower()
                )

                category_match = (
                    inventory.category.strip().lower()
                    ==
                    request_item.category.strip().lower()
                )

                if item_name_match:
                    matching_inventory.append(
                        (inventory, 2)
                    )

                elif category_match:
                    matching_inventory.append(
                        (inventory, 1)
                    )

            # Exact item matches should be preferred.
            matching_inventory.sort(
                key=lambda x: x[1],
                reverse=True
            )

            # -------------------------------------------------
            # Allocate from this warehouse
            # -------------------------------------------------

            for inventory, _match_score in matching_inventory:

                if fulfilled_quantity >= needed_quantity:
                    break

                available_quantity = (
                    inventory.available_quantity
                )

                quantity_needed = (
                    needed_quantity
                    - fulfilled_quantity
                )

                recommended_quantity = min(
                    quantity_needed,
                    available_quantity
                )

                if recommended_quantity <= 0:
                    continue

                fulfilled_quantity += (
                    recommended_quantity
                )

                # -------------------------------------------------
                # Find nearest expiry for display
                # -------------------------------------------------

                nearest_expiry = None

                if inventory.batches:

                    expiry_dates = [
                        batch.expiry_date
                        for batch in inventory.batches
                        if batch.expiry_date
                    ]

                    if expiry_dates:

                        nearest_expiry = min(
                            expiry_dates
                        ).strftime("%Y-%m-%d")

                # -------------------------------------------------
                # Add recommendation
                # -------------------------------------------------

                recommendations.append(
                    MatchedWarehouseItem(
                        warehouse_id=warehouse.id,
                        warehouse_name=warehouse.name,
                        distance_km=round(
                            distance_km,
                            1
                        ),
                        item_name=inventory.item_name,
                        category=inventory.category,
                        available_qty=available_quantity,
                        recommended_qty=recommended_quantity,
                        unit=inventory.unit,
                        expiry_date=nearest_expiry
                    )
                )

                rationale_points.append(
                    f"{inventory.item_name}: "
                    f"allocate {recommended_quantity:g} "
                    f"{inventory.unit} from "
                    f"{warehouse.name} "
                    f"({distance_km:.1f} km away; "
                    f"{available_quantity:g} "
                    f"{inventory.unit} verified available)."
                )

        # =====================================================
        # 3. CHECK WHETHER THE ITEM WAS FULLY FULFILLED
        # =====================================================

        if fulfilled_quantity < needed_quantity:

            is_partial = True

            shortage = (
                needed_quantity
                - fulfilled_quantity
            )

            remaining_shortages.append(
                {
                    "category":
                        request_item.category,

                    "item_name":
                        request_item.item_name,

                    "requested":
                        needed_quantity,

                    "fulfilled":
                        fulfilled_quantity,

                    "shortage":
                        shortage,

                    "unit":
                        request_item.unit
                }
            )

            rationale_points.append(
                f"Deficit alert: "
                f"{shortage:g} "
                f"{request_item.unit} of "
                f"{request_item.item_name} "
                f"remains unavailable from "
                f"verified warehouse inventory."
            )

    # =========================================================
    # 4. BUILD SUMMARY
    # =========================================================

    if rationale_points:

        summary_rationale = " ".join(
            rationale_points
        )

    else:

        summary_rationale = (
            "No verified warehouse inventory "
            "matches the requested items."
        )

    # =========================================================
    # 5. RETURN AI RECOMMENDATION
    # =========================================================

    return AIResourceMatchRecommendation(
        request_id=request.id,

        request_tracking_code=
            request.tracking_code,

        location_name=
            request.location_name,

        priority_classification=(
            request.priority_classification.value
            if hasattr(
                request.priority_classification,
                "value"
            )
            else str(
                request.priority_classification
            )
        ),

        priority_score=(
            request.authority_override_score
            if request.authority_override_score
            is not None
            else request.priority_score
        ),

        is_partial=is_partial,

        summary_rationale=
            summary_rationale,

        recommendations=
            recommendations,

        remaining_shortages=
            remaining_shortages
    )