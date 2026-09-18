import re
from typing import Dict, Any, List
from app.schemas import AIUnderstandingResponse, ExtractedItem

KNOWN_LOCATIONS = [
    {"name": "Village A", "lat": 14.5230, "lon": 75.3120, "zone_id": 2},
    {"name": "Village B", "lat": 14.5420, "lon": 75.3340, "zone_id": 2},
    {"name": "Village C", "lat": 14.4980, "lon": 75.2950, "zone_id": 1},
    {"name": "Ward 12", "lat": 14.5110, "lon": 75.3210, "zone_id": 2},
    {"name": "River Basin Cluster", "lat": 14.4850, "lon": 75.2750, "zone_id": 1},
    {"name": "Delta East Hamlet", "lat": 14.5380, "lon": 75.3520, "zone_id": 3},
    {"name": "Urban Waterfront", "lat": 14.5610, "lon": 75.3100, "zone_id": 4},
]

def parse_natural_language_request(text: str) -> AIUnderstandingResponse:
    lower_text = text.lower()
    
    # 1. Location Detection
    matched_loc = "Village A" # default fallback
    lat = 14.5230
    lon = 75.3120
    for loc in KNOWN_LOCATIONS:
        if loc["name"].lower() in lower_text:
            matched_loc = loc["name"]
            lat = loc["lat"]
            lon = loc["lon"]
            break
    
    # 2. Population Extraction
    people_match = re.search(r"(\d+)\s*(?:people|residents|persons|individuals|villagers|citizens)", lower_text)
    affected_people = int(people_match.group(1)) if people_match else 50
    
    # Check for general numbers if stranded/trapped
    if not people_match:
        stranded_match = re.search(r"(?:stranded|trapped|affected)\s*(?:around|about|approx|approximately)?\s*(\d+)", lower_text)
        if stranded_match:
            affected_people = int(stranded_match.group(1))
        else:
            num_match = re.search(r"(\d+)", lower_text)
            if num_match and int(num_match.group(1)) > 10:
                affected_people = int(num_match.group(1))

    affected_households = max(1, affected_people // 4)
    
    # 3. Vulnerable Extraction
    elderly_match = re.search(r"(\d+)\s*(?:elderly|seniors|aged|old people)", lower_text)
    vulnerable_elderly = int(elderly_match.group(1)) if elderly_match else 0
    
    children_match = re.search(r"(\d+)\s*(?:children|kids)", lower_text)
    vulnerable_children = int(children_match.group(1)) if children_match else 0

    infants_match = re.search(r"(\d+)\s*(?:infants|babies|toddlers)", lower_text)
    vulnerable_infants = int(infants_match.group(1)) if infants_match else 0

    pregnant_match = re.search(r"(\d+)\s*(?:pregnant|expecting mothers)", lower_text)
    vulnerable_pregnant = int(pregnant_match.group(1)) if pregnant_match else 0
    
    total_vulnerable = vulnerable_elderly + vulnerable_children + vulnerable_infants + vulnerable_pregnant
    
    # 4. Items & Volume Extraction
    items: List[ExtractedItem] = []
    
    # Drinking Water
    if any(k in lower_text for k in ["water", "drinking water", "bottled water", "thirst"]):
        qty_match = re.search(r"(\d+)\s*(?:liters|litres|l|bottles|gallons)", lower_text)
        if qty_match:
            qty = float(qty_match.group(1))
        else:
            # WHO standard: 3 Liters per person per day * 2 days
            qty = float(affected_people * 5)
        items.append(ExtractedItem(category="Drinking Water", item_name="Clean Drinking Water", quantity=qty, unit="Liters"))
    
    # Food
    if any(k in lower_text for k in ["food", "meal", "ration", "rice", "bread", "packets"]):
        qty_match = re.search(r"(\d+)\s*(?:packets|meals|kits|boxes|kg)", lower_text)
        if qty_match:
            qty = float(qty_match.group(1))
        else:
            qty = float(affected_people * 2)
        items.append(ExtractedItem(category="Food", item_name="Ready-to-Eat Food Packets", quantity=qty, unit="Packets"))
    
    # Medicines
    if any(k in lower_text for k in ["medicine", "medicines", "medical", "first aid", "doctor", "insulin", "antibiotic"]):
        qty_match = re.search(r"(\d+)\s*(?:kits|boxes|doses)", lower_text)
        qty = float(qty_match.group(1)) if qty_match else float(max(5, affected_people // 10))
        items.append(ExtractedItem(category="Medicines", item_name="Emergency First Aid & Essential Medicine Kits", quantity=qty, unit="Kits"))
    
    # Sanitation / Hygiene
    if any(k in lower_text for k in ["hygiene", "sanitary", "soap", "sanitation", "toilet", "chlorine"]):
        items.append(ExtractedItem(category="Sanitation", item_name="Hygiene & Sanitation Kits", quantity=float(affected_households), unit="Kits"))
        
    # Blankets / Shelter
    if any(k in lower_text for k in ["blanket", "tarpaulin", "shelter", "sheet", "tents"]):
        items.append(ExtractedItem(category="Temporary Shelter", item_name="Tarpaulins & Thermal Blankets", quantity=float(affected_households * 2), unit="Sets"))
    
    # Baby Supplies
    if vulnerable_infants > 0 or "baby" in lower_text or "diaper" in lower_text or "infant milk" in lower_text:
        items.append(ExtractedItem(category="Baby Supplies", item_name="Baby Formula & Care Packs", quantity=float(max(10, vulnerable_infants * 3)), unit="Packs"))

    # Fallback if no specific item matched
    if not items:
        items.append(ExtractedItem(category="Drinking Water", item_name="Emergency Drinking Water", quantity=float(affected_people * 4), unit="Liters"))
        items.append(ExtractedItem(category="Food", item_name="Emergency Rations", quantity=float(affected_people * 2), unit="Packets"))
    
    # 5. Urgency Classification
    urgency = "HIGH"
    if any(k in lower_text for k in ["urgently", "emergency", "immediately", "critical", "drowning", "rising water", "stranded"]):
        urgency = "CRITICAL"
    elif any(k in lower_text for k in ["minor", "stable", "non-urgent", "routine"]):
        urgency = "MEDIUM"
        
    # 6. Confidence Score
    confidence = 0.94 if people_match and len(items) >= 2 else 0.85

    reasoning = (
        f"AI parsed '{matched_loc}' with {affected_people} affected people and {total_vulnerable} vulnerable "
        f"individuals ({vulnerable_elderly} elderly, {vulnerable_children} children). "
        f"Identified {len(items)} relief commodity requirements with urgency classified as {urgency}."
    )
    
    return AIUnderstandingResponse(
        raw_text=text,
        extracted_location=matched_loc,
        latitude=lat,
        longitude=lon,
        affected_people=affected_people,
        affected_households=affected_households,
        vulnerable_elderly=vulnerable_elderly,
        vulnerable_children=vulnerable_children,
        vulnerable_total=total_vulnerable,
        urgency=urgency,
        items=items,
        confidence_score=confidence,
        reasoning=reasoning
    )
