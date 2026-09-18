import os

AI_DIR = os.path.join(os.path.dirname(__file__), "backend", "app", "ai")

matcher_code = """import math
from typing import List, Dict, Any, Tuple
from app.models import CommunityRequest, Warehouse, Inventory, RequestItem
from app.ai.duplicate_detector import haversine_distance_km
from app.schemas import AIResourceMatchRecommendation, MatchedWarehouseItem

def match_resources_for_request(
    request: CommunityRequest,
    warehouses: List[Warehouse]
) -> AIResourceMatchRecommendation:
    recommendations: List[MatchedWarehouseItem] = []
    remaining_shortages: List[Dict[str, Any]] = []
    is_partial = False
    rationale_points: List[str] = []

    # Map warehouses with distances
    wh_with_dist = []
    for wh in warehouses:
        if not wh.is_active:
            continue
        dist = haversine_distance_km(
            request.latitude, request.longitude,
            wh.latitude, wh.longitude
        )
        wh_with_dist.append((wh, dist))
        
    # Sort warehouses by distance ascending
    wh_with_dist.sort(key=lambda x: x[1])

    # Evaluate each required item in the request
    for req_item in request.items:
        needed_qty = req_item.requested_quantity - req_item.fulfilled_quantity
        if needed_qty <= 0:
            continue
            
        fulfilled_for_this_item = 0.0
        
        # Scan warehouses starting with closest
        for wh, dist_km in wh_with_dist:
            # Find matching inventory in warehouse
            inv_items = [
                inv for inv in wh.inventory
                if (inv.category.lower() == req_item.category.lower() or
                    req_item.category.lower() in inv.category.lower())
                and inv.available_quantity > 0
            ]
            
            for inv in inv_items:
                available = inv.available_quantity
                if available <= 0:
                    continue
                
                allocate_qty = min(needed_qty - fulfilled_for_this_item, available)
                if allocate_qty > 0:
                    fulfilled_for_this_item += allocate_qty
                    
                    # Check expiry date if batches exist
                    nearest_expiry = None
                    if inv.batches:
                        expiries = [b.expiry_date for b in inv.batches if b.expiry_date]
                        if expiries:
                            nearest_expiry = min(expiries).strftime("%Y-%m-%d")

                    recommendations.append(
                        MatchedWarehouseItem(
                            warehouse_id=wh.id,
                            warehouse_name=wh.name,
                            distance_km=round(dist_km, 1),
                            item_name=inv.item_name,
                            category=inv.category,
                            available_qty=available,
                            recommended_qty=allocate_qty,
                            unit=inv.unit,
                            expiry_date=nearest_expiry
                        )
                    )
                    
                    rationale_points.append(
                        f"Allocate {allocate_qty:g} {inv.unit} of {inv.item_name} from {wh.name} "
                        f"({dist_km:.1f} km away; {available:g} {inv.unit} in stock). "
                        f"Minimizes transport latency for {request.priority_classification.value if hasattr(request.priority_classification, 'value') else request.priority_classification} urgency."
                    )
                    
                if fulfilled_for_this_item >= needed_qty:
                    break
            if fulfilled_for_this_item >= needed_qty:
                break
                
        # If unable to fulfill 100%
        if fulfilled_for_this_item < needed_qty:
            is_partial = True
            shortage_amount = needed_qty - fulfilled_for_this_item
            remaining_shortages.append({
                "category": req_item.category,
                "item_name": req_item.item_name,
                "requested": needed_qty,
                "fulfilled": fulfilled_for_this_item,
                "shortage": shortage_amount,
                "unit": req_item.unit
            })
            rationale_points.append(
                f"Deficit alert: Unmet demand of {shortage_amount:g} {req_item.unit} for {req_item.item_name}. "
                f"Flagged for NGO/Donor emergency procurement radar."
            )

    summary_rationale = " ".join(rationale_points) if rationale_points else "No active warehouse has available matching inventory."

    return AIResourceMatchRecommendation(
        request_id=request.id,
        request_tracking_code=request.tracking_code,
        location_name=request.location_name,
        priority_classification=request.priority_classification.value if hasattr(request.priority_classification, 'value') else str(request.priority_classification),
        priority_score=request.authority_override_score if request.authority_override_score is not None else request.priority_score,
        is_partial=is_partial,
        summary_rationale=summary_rationale,
        recommendations=recommendations,
        remaining_shortages=remaining_shortages
    )
"""

with open(os.path.join(AI_DIR, "resource_matcher.py"), "w", encoding="utf-8") as f:
    f.write(matcher_code)

print("resource_matcher.py written successfully.")
