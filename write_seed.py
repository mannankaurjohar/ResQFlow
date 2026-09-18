import os

APP_DIR = os.path.join(os.path.dirname(__file__), "backend", "app")

seed_code = """import json
import datetime
from sqlalchemy.orm import Session
from app.database import Base, engine
from app.models import (
    User, UserRole, Organization, DisasterEvent, DisasterType,
    AffectedZone, SeverityLevel, CommunityRequest, RequestItem, RequestVerification,
    Warehouse, Inventory, InventoryBatch, Donation, DonationItem,
    Allocation, AllocationItem, Vehicle, Delivery, Route, ReliefCenter,
    AuditLog, RequestStatus, ReliefStatus
)
from app.auth import get_password_hash, log_audit_event

def seed_all_data(db: Session, force_reset: bool = False):
    if force_reset:
        # Clear tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    # Check if already seeded
    if db.query(User).first() and not force_reset:
        print("Database already contains data, skipping seed.")
        return

    print("Seeding fresh demo dataset for ResQFlow AI...")

    # 1. Organizations
    org_auth = Organization(name="State Disaster Management Authority (SDMA)", org_type="AUTHORITY", contact_person="Director Rajesh Varma", phone="+91 94480 11223", email="command@sdma.gov.in", latitude=14.4700, longitude=75.2800)
    org_wh_a = Organization(name="Central Humanitarian Logistics Depot", org_type="WAREHOUSE", contact_person="Col. P. Nair", phone="+91 94480 22334", email="depot.central@relief.org", latitude=14.4650, longitude=75.2850)
    org_wh_b = Organization(name="Northern Delta Logistics Hub", org_type="WAREHOUSE", contact_person="Sunil Hegde", phone="+91 94480 33445", email="depot.north@relief.org", latitude=14.7800, longitude=75.4500)
    org_ngo1 = Organization(name="Red Crescent Flood Relief", org_type="NGO", contact_person="Farah Khan", phone="+91 94480 44556", email="flood@redcrescent.org", latitude=14.4820, longitude=75.2900)
    org_ngo2 = Organization(name="CleanWater Global Mission", org_type="NGO", contact_person="David Miller", phone="+91 94480 55667", email="action@cleanwater.org", latitude=14.5100, longitude=75.3300)
    org_ngo3 = Organization(name="Rapid Medical Emergency NGO", org_type="NGO", contact_person="Dr. Swathi Rao", phone="+91 94480 66778", email="response@rapidmed.org", latitude=14.4950, longitude=75.3100)
    
    db.add_all([org_auth, org_wh_a, org_wh_b, org_ngo1, org_ngo2, org_ngo3])
    db.flush()

    # 2. Users (7 Personas)
    hashed_pwd = get_password_hash("password123")
    users = [
        User(username="authority_admin", email="authority@resqflow.org", hashed_password=hashed_pwd, full_name="Command Officer Rajesh Varma", role=UserRole.AUTHORITY, organization_id=org_auth.id, phone="+91 98801 11222"),
        User(username="volunteer_lead", email="volunteer@resqflow.org", hashed_password=hashed_pwd, full_name="Aarav Sen (Field Lead)", role=UserRole.VOLUNTEER, organization_id=org_ngo1.id, phone="+91 98802 22333"),
        User(username="ngo_coordinator", email="ngo@resqflow.org", hashed_password=hashed_pwd, full_name="Farah Khan (Director)", role=UserRole.NGO_MANAGER, organization_id=org_ngo1.id, phone="+91 98803 33444"),
        User(username="warehouse_manager", email="warehouse@resqflow.org", hashed_password=hashed_pwd, full_name="Vikram Seth (Depot Master)", role=UserRole.WAREHOUSE_MANAGER, organization_id=org_wh_a.id, phone="+91 98804 44555"),
        User(username="donor_user", email="donor@resqflow.org", hashed_password=hashed_pwd, full_name="Anita & Vikram Sharma", role=UserRole.DONOR, organization_id=None, phone="+91 98805 55666"),
        User(username="citizen_user", email="citizen@resqflow.org", hashed_password=hashed_pwd, full_name="Pooja Kulkarni (Citizen)", role=UserRole.COMMUNITY, organization_id=None, phone="+91 98806 66777"),
        User(username="system_admin", email="admin@resqflow.org", hashed_password=hashed_pwd, full_name="Antigravity System Admin", role=UserRole.ADMIN, organization_id=org_auth.id, phone="+91 98807 77888")
    ]
    db.add_all(users)
    db.flush()

    # 3. Disaster Event (Floods)
    disaster = DisasterEvent(
        name="Tungabhadra River Monsoon Flash Flood 2026",
        disaster_type=DisasterType.FLOOD,
        status="ACTIVE",
        severity=SeverityLevel.HIGH,
        description="Severe monsoon rainfall caused flash flooding across lower delta and river basin wards. Multiple embankments inundated."
    )
    db.add(disaster)
    db.flush()

    # 4. 5 Affected Zones with Polygons
    zone_a_poly = [[14.475, 75.265], [14.495, 75.265], [14.498, 75.290], [14.470, 75.285]]
    zone_b_poly = [[14.510, 75.300], [14.545, 75.305], [14.540, 75.340], [14.505, 75.335]]
    zone_c_poly = [[14.520, 75.340], [14.550, 75.345], [14.550, 75.370], [14.515, 75.365]]
    zone_d_poly = [[14.550, 75.295], [14.580, 75.300], [14.575, 75.330], [14.545, 75.325]]
    zone_e_poly = [[14.450, 75.240], [14.470, 75.245], [14.465, 75.265], [14.445, 75.260]]

    zones = [
        AffectedZone(disaster_id=disaster.id, name="Zone A (River Basin)", code="ZONE-A", severity_level=SeverityLevel.HIGH, water_level_meters=2.1, population=7400, households=1600, center_lat=14.4850, center_lon=75.2750, polygon_geojson=json.dumps(zone_a_poly)),
        AffectedZone(disaster_id=disaster.id, name="Zone B (Delta Lowlands & Village A)", code="ZONE-B", severity_level=SeverityLevel.SEVERE, water_level_meters=2.8, population=9800, households=2200, center_lat=14.5250, center_lon=75.3180, polygon_geojson=json.dumps(zone_b_poly), is_isolated=True),
        AffectedZone(disaster_id=disaster.id, name="Zone C (Eastern Polders)", code="ZONE-C", severity_level=SeverityLevel.MODERATE, water_level_meters=1.4, population=5600, households=1250, center_lat=14.5320, center_lon=75.3520, polygon_geojson=json.dumps(zone_c_poly)),
        AffectedZone(disaster_id=disaster.id, name="Zone D (Urban Waterfront)", code="ZONE-D", severity_level=SeverityLevel.HIGH, water_level_meters=1.9, population=12500, households=2900, center_lat=14.5620, center_lon=75.3120, polygon_geojson=json.dumps(zone_d_poly)),
        AffectedZone(disaster_id=disaster.id, name="Zone E (Highland Evacuation Ridge)", code="ZONE-E", severity_level=SeverityLevel.LOW, water_level_meters=0.4, population=4200, households=950, center_lat=14.4580, center_lon=75.2520, polygon_geojson=json.dumps(zone_e_poly))
    ]
    db.add_all(zones)
    db.flush()

    # 5. Warehouses
    wh_a = Warehouse(organization_id=org_wh_a.id, name="Warehouse A (Central Logistics Hub)", code="WH-CENTRAL-01", address="Industrial Zone North, Plot 14", latitude=14.4650, longitude=75.2850, capacity_sqm=3500.0)
    wh_b = Warehouse(organization_id=org_wh_b.id, name="Warehouse B (Northern NGO Depot)", code="WH-NORTH-02", address="Highway 4 Bypass, Km 30", latitude=14.7800, longitude=75.4500, capacity_sqm=2200.0)
    wh_c = Warehouse(organization_id=org_wh_a.id, name="Warehouse C (South Coastal Reserve)", code="WH-SOUTH-03", address="Coastal Highway 17, Port Sector", latitude=14.3200, longitude=75.1800, capacity_sqm=4000.0)
    db.add_all([wh_a, wh_b, wh_c])
    db.flush()

    # 6. Inventory & Batches
    now = datetime.datetime.utcnow()
    two_months = now + datetime.timedelta(days=60)
    one_year = now + datetime.timedelta(days=365)
    one_week = now + datetime.timedelta(days=7)

    # Warehouse A inventory (Central: 7 km from Village A)
    inv_a1 = Inventory(warehouse_id=wh_a.id, category="Drinking Water", item_name="Packaged Drinking Water (20L Jerrycans)", unit="L", total_quantity=3500.0, reserved_quantity=0.0, allocated_quantity=500.0, available_quantity=3000.0, min_threshold=500.0, status="AVAILABLE")
    inv_a2 = Inventory(warehouse_id=wh_a.id, category="Food", item_name="Ready-to-Eat Emergency Food Packets", unit="Packets", total_quantity=2000.0, reserved_quantity=0.0, allocated_quantity=200.0, available_quantity=1800.0, min_threshold=300.0, status="AVAILABLE")
    inv_a3 = Inventory(warehouse_id=wh_a.id, category="Medicines", item_name="Emergency First Aid & Trauma Kits", unit="Kits", total_quantity=180.0, reserved_quantity=0.0, allocated_quantity=20.0, available_quantity=160.0, min_threshold=30.0, status="AVAILABLE")
    inv_a4 = Inventory(warehouse_id=wh_a.id, category="Sanitation", item_name="Disinfectant & Hygiene Care Packs", unit="Kits", total_quantity=450.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=450.0, min_threshold=50.0, status="AVAILABLE")
    inv_a5 = Inventory(warehouse_id=wh_a.id, category="Temporary Shelter", item_name="Heavy-Duty Waterproof Tarpaulins", unit="Units", total_quantity=600.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=600.0, min_threshold=100.0, status="AVAILABLE")

    # Warehouse B inventory (30 km away)
    inv_b1 = Inventory(warehouse_id=wh_b.id, category="Drinking Water", item_name="Chlorinated Clean Drinking Water", unit="L", total_quantity=5000.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=5000.0, min_threshold=800.0, status="AVAILABLE")
    inv_b2 = Inventory(warehouse_id=wh_b.id, category="Food", item_name="High-Calorie Meal Rations", unit="Packets", total_quantity=3500.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=3500.0, min_threshold=500.0, status="AVAILABLE")
    inv_b3 = Inventory(warehouse_id=wh_b.id, category="Baby Supplies", item_name="Infant Milk Formula & Baby Care Kits", unit="Packs", total_quantity=150.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=150.0, min_threshold=20.0, status="AVAILABLE")

    # Warehouse C inventory (South Coastal)
    inv_c1 = Inventory(warehouse_id=wh_c.id, category="Medicines", item_name="Antibiotics, ORS & Water Purification Tablets", unit="Kits", total_quantity=250.0, reserved_quantity=0.0, allocated_quantity=50.0, available_quantity=200.0, min_threshold=40.0, status="AVAILABLE")
    inv_c2 = Inventory(warehouse_id=wh_c.id, category="Drinking Water", item_name="Bottled Spring Water", unit="L", total_quantity=2000.0, reserved_quantity=0.0, allocated_quantity=0.0, available_quantity=2000.0, min_threshold=300.0, status="AVAILABLE")
    
    db.add_all([inv_a1, inv_a2, inv_a3, inv_a4, inv_a5, inv_b1, inv_b2, inv_b3, inv_c1, inv_c2])
    db.flush()

    # Batches
    b1 = InventoryBatch(inventory_id=inv_a1.id, batch_number="BAT-WTR-202609-01", quantity=3500.0, expiry_date=one_year)
    b2 = InventoryBatch(inventory_id=inv_a3.id, batch_number="BAT-MED-202609-04", quantity=180.0, expiry_date=two_months)
    b3 = InventoryBatch(inventory_id=inv_c1.id, batch_number="BAT-MED-EXP-WARN", quantity=30.0, expiry_date=one_week) # Expiring alert!
    db.add_all([b1, b2, b3])
    db.flush()

    # 7. Vehicles
    vehicles = [
        Vehicle(code="RESQ-V01", vehicle_type="Heavy 4x4 Supply Truck", capacity_kg=3500.0, status="AVAILABLE", driver_name="Ramesh Yadav", driver_phone="+91 98451 22390", current_lat=14.466, current_lon=75.286),
        Vehicle(code="RESQ-V02", vehicle_type="Amphibious All-Terrain Vehicle", capacity_kg=1800.0, status="AVAILABLE", driver_name="Kiran Shenoy", driver_phone="+91 98451 33401", current_lat=14.470, current_lon=75.290),
        Vehicle(code="RESQ-V03", vehicle_type="Inflatable Rescue Boat (Zodiac)", capacity_kg=850.0, status="AVAILABLE", driver_name="Sanjay Naik", driver_phone="+91 98451 44512", current_lat=14.520, current_lon=75.310),
        Vehicle(code="RESQ-V04", vehicle_type="Heavy Emergency Cargo Drone", capacity_kg=60.0, status="AVAILABLE", driver_name="Remote Pilot Meera", driver_phone="+91 98451 55623", current_lat=14.465, current_lon=75.285),
        Vehicle(code="RESQ-V05", vehicle_type="High-Clearance 4x4 Jeep", capacity_kg=1200.0, status="AVAILABLE", driver_name="Tanveer Ahmed", driver_phone="+91 98451 66734", current_lat=14.510, current_lon=75.320)
    ]
    db.add_all(vehicles)
    db.flush()

    # 8. Relief Centers
    rc1 = ReliefCenter(zone_id=zones[1].id, name="North Delta Government High School Shelter", latitude=14.5300, longitude=75.3250, capacity=1200, current_occupancy=540, contact_phone="+91 836 220199", has_medical_post=True)
    rc2 = ReliefCenter(zone_id=zones[0].id, name="River Basin Community Stadium Camp", latitude=14.4820, longitude=75.2800, capacity=2000, current_occupancy=1450, contact_phone="+91 836 220188", has_medical_post=True)
    rc3 = ReliefCenter(zone_id=zones[4].id, name="Highland Safe Elevation Evacuation Hub", latitude=14.4550, longitude=75.2500, capacity=3500, current_occupancy=820, contact_phone="+91 836 220177", has_medical_post=True)
    db.add_all([rc1, rc2, rc3])
    db.flush()

    # 9. Requests (including the Signature Village A Request)
    req_village_a = CommunityRequest(
        tracking_code="FR-1048",
        zone_id=zones[1].id,
        reporter_name="Sarpanch Ramesh",
        reporter_phone="+91 94812 33491",
        reporter_role="Community Leader",
        location_name="Village A",
        latitude=14.5230,
        longitude=75.3120,
        affected_people=350,
        affected_households=85,
        vulnerable_elderly=40,
        vulnerable_children=25,
        vulnerable_infants=5,
        vulnerable_pregnant=3,
        urgency=SeverityLevel.CRITICAL,
        raw_description="Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children.",
        priority_score=88.0,
        priority_classification=SeverityLevel.CRITICAL,
        priority_factors_json=json.dumps([
            {"factor": "Affected Population", "points": 25.0, "reason": "350 people stranded (Extremely high density)"},
            {"factor": "Vulnerable Demographics", "points": 20.0, "reason": "65 vulnerable people (40 elderly, 25 children)"},
            {"factor": "Resource Essentiality", "points": 20.0, "reason": "Drinking water shortage & emergency medicine required"},
            {"factor": "Flood Severity Zone", "points": 15.0, "reason": "Severe inundation (Water level: 2.8m, Village isolated)"},
            {"factor": "Response Latency", "points": 8.0, "reason": "Request pending 5 hours without full delivery"}
        ]),
        status=RequestStatus.PENDING,
        created_at=now - datetime.timedelta(hours=5.2)
    )
    db.add(req_village_a)
    db.flush()

    items_a = [
        RequestItem(request_id=req_village_a.id, category="Drinking Water", item_name="Drinking Water", requested_quantity=2000.0, unit="L", fulfilled_quantity=0.0),
        RequestItem(request_id=req_village_a.id, category="Food", item_name="Ready-to-Eat Food Packets", requested_quantity=700.0, unit="Packets", fulfilled_quantity=0.0),
        RequestItem(request_id=req_village_a.id, category="Medicines", item_name="Emergency First Aid & Medicine Kits", requested_quantity=35.0, unit="Kits", fulfilled_quantity=0.0)
    ]
    db.add_all(items_a)

    # Pre-seed duplicate candidate for Hackathon duplicate detection demo:
    req_dup = CommunityRequest(
        tracking_code="FR-1052",
        zone_id=zones[1].id,
        reporter_name="Citizen Suresh",
        reporter_phone="+91 94812 99881",
        reporter_role="Citizen",
        location_name="Village A (North Sector)",
        latitude=14.5240,
        longitude=75.3130,
        affected_people=320,
        affected_households=75,
        vulnerable_elderly=35,
        vulnerable_children=20,
        urgency=SeverityLevel.CRITICAL,
        raw_description="Around 320 villagers stranded in Village A north sector. Need drinking water and food packets urgently.",
        priority_score=84.0,
        priority_classification=SeverityLevel.CRITICAL,
        status=RequestStatus.FLAGGED_DUPLICATE,
        created_at=now - datetime.timedelta(hours=1.5)
    )
    db.add(req_dup)
    db.flush()

    verif_dup = RequestVerification(
        request_id=req_dup.id,
        verified_by_id=users[1].id,
        is_duplicate=True,
        duplicate_of_id=req_village_a.id,
        similarity_score=0.91,
        notes="Potential duplicate detected — 91% similarity with FR-1048. Village A North Sector within 180m radius.",
        action_taken="FLAGGED"
    )
    db.add(verif_dup)

    # Pre-seed requests across other zones (Total 20+ requests)
    other_requests_data = [
        ("Ward 12", 14.5110, 75.3210, zones[1].id, 520, SeverityLevel.CRITICAL, 82.0, "Critical drinking water crisis. Contamination in local wells. Need 5000L water."),
        ("Village B", 14.5420, 75.3340, zones[1].id, 120, SeverityLevel.HIGH, 68.0, "Water level rising near community hall. Need drinking water and blankets."),
        ("River Basin Cluster 1", 14.4850, 75.2750, zones[0].id, 180, SeverityLevel.HIGH, 72.0, "Flood water breached bank. 40 families evacuated to school roof."),
        ("Delta East Hamlet", 14.5380, 75.3520, zones[2].id, 65, SeverityLevel.MEDIUM, 54.0, "Road cutoff. Requesting baby food and milk powder for 12 infants."),
        ("Urban Waterfront Block 4", 14.5610, 75.3100, zones[3].id, 240, SeverityLevel.HIGH, 70.0, "Basement flooding in low-income housing colony. Clean water needed."),
        ("Causeway Approach Slum", 14.5290, 75.3200, zones[1].id, 90, SeverityLevel.MEDIUM, 58.0, "Temporary tarpaulins torn by heavy wind. Need shelter materials."),
        ("Old Canal Settlement", 14.4920, 75.2880, zones[0].id, 75, SeverityLevel.MEDIUM, 52.0, "Food supplies ruined by ground runoff. Rations needed.")
    ]

    for idx, (loc, lat, lon, zid, pop, urg, score, desc) in enumerate(other_requests_data):
        code = f"FR-{1055 + idx}"
        req_obj = CommunityRequest(
            tracking_code=code,
            zone_id=zid,
            reporter_name=f"Community Rep {loc}",
            location_name=loc,
            latitude=lat,
            longitude=lon,
            affected_people=pop,
            affected_households=max(1, pop // 4),
            vulnerable_elderly=max(2, pop // 12),
            vulnerable_children=max(5, pop // 8),
            urgency=urg,
            raw_description=desc,
            priority_score=score,
            priority_classification=urg,
            status=RequestStatus.PENDING,
            created_at=now - datetime.timedelta(hours=3 + idx)
        )
        db.add(req_obj)
        db.flush()
        db.add(RequestItem(request_id=req_obj.id, category="Drinking Water", item_name="Clean Drinking Water", requested_quantity=float(pop * 3), unit="L"))
        db.add(RequestItem(request_id=req_obj.id, category="Food", item_name="Emergency Food Rations", requested_quantity=float(pop * 2), unit="Packets"))

    # 10. Signature Delivered Donation: D-10284 & RELIEF-2026-00482 (Directly from Prompt!)
    # Donor Anita & Vikram Sharma donated 500 water bottles -> Delivered to Flood Zone B -> 250 people supported
    don_signature = Donation(
        donor_id=users[4].id,
        donor_name="Anita & Vikram Sharma",
        donor_email="anita.sharma@gmail.com",
        tracking_id="D-10284",
        relief_id="RELIEF-2026-00482",
        target_zone_id=zones[1].id,
        status=ReliefStatus.DELIVERED,
        notes="500 water bottles for flood relief in Zone B delta.",
        created_at=now - datetime.timedelta(hours=8.0)
    )
    db.add(don_signature)
    db.flush()

    don_it = DonationItem(
        donation_id=don_signature.id,
        category="Drinking Water",
        item_name="Drinking Water Bottles (1L)",
        quantity=500.0,
        unit="Bottles"
    )
    db.add(don_it)

    # Create Completed Allocation & Delivery for RELIEF-2026-00482
    alloc_sig = Allocation(
        request_id=req_village_a.id,
        warehouse_id=wh_a.id,
        relief_id="RELIEF-2026-00482",
        status="DELIVERED",
        ai_score=88.0,
        ai_rationale="Allocated 500 water bottles from Warehouse A to Village A Sector 2.",
        is_partial=False,
        approved_by_id=users[0].id,
        approved_at=now - datetime.timedelta(hours=4.5),
        created_at=now - datetime.timedelta(hours=5.0)
    )
    db.add(alloc_sig)
    db.flush()

    alloc_it_sig = AllocationItem(
        allocation_id=alloc_sig.id,
        category="Drinking Water",
        item_name="Drinking Water Bottles",
        requested_quantity=500.0,
        allocated_quantity=500.0,
        unit="Bottles"
    )
    db.add(alloc_it_sig)

    deliv_sig = Delivery(
        relief_id="RELIEF-2026-00482",
        allocation_id=alloc_sig.id,
        vehicle_id=vehicles[0].id,
        driver_name="Ramesh Yadav",
        driver_phone="+91 98451 22390",
        origin_warehouse_id=wh_a.id,
        destination_location_name="Village A, Shelter Point 2",
        destination_lat=14.5235,
        destination_lon=75.3125,
        status=ReliefStatus.DELIVERED,
        dispatched_at=now - datetime.timedelta(hours=3.5),
        delivered_at=now - datetime.timedelta(hours=1.2),
        proof_photo_url="https://images.unsplash.com/photo-1547841243-eacb14453cd9?auto=format&fit=crop&w=600&q=80",
        recipient_signature="Gram Panchayat Head - Rameshwar",
        notes="Verified delivery: 500 / 500 water bottles received in good condition. Supported ~250 stranded villagers."
    )
    db.add(deliv_sig)
    db.flush()

    route_sig = Route(
        delivery_id=deliv_sig.id,
        waypoints_json=json.dumps([
            {"lat": 14.465, "lon": 75.285, "name": "Warehouse A Central"},
            {"lat": 14.495, "lon": 75.295, "name": "Checkpoint Causeway Bypass"},
            {"lat": 14.523, "lon": 75.312, "name": "Village A Shelter"}
        ]),
        total_distance_km=7.8,
        estimated_time_mins=32,
        avoids_flooded_bridges=True
    )
    db.add(route_sig)

    # 11. Initial Chained Cryptographic Audit Logs
    import hashlib
    prev_hash = "0" * 64
    audit_events = [
        ("System Initialization", "SYSTEM", "GENESIS", "SYSTEM", "0", None, "INITIAL_STATE", "Genesis disaster coordination block created"),
        ("Command Officer Rajesh Varma", "AUTHORITY", "ESCALATE_DISASTER", "DISASTER_EVENT", "FLOOD-2026", "NORMAL", "HIGH_ALERT", "Monsoon surge exceeded warning threshold"),
        ("Anita & Vikram Sharma", "DONOR", "PLEDGE_DONATION", "DONATION", "D-10284", None, "500 Water Bottles", "Donation registered with relief tracking ID RELIEF-2026-00482"),
        ("Command Officer Rajesh Varma", "AUTHORITY", "APPROVE_ALLOCATION", "ALLOCATION", "RELIEF-2026-00482", "RECOMMENDED", "APPROVED", "Approved 500 bottles from Warehouse A"),
        ("Logistics Dispatcher", "LOGISTICS", "DISPATCH_DELIVERY", "DELIVERY", "RELIEF-2026-00482", "ALLOCATED", "IN_TRANSIT", "Dispatched on Heavy 4x4 Truck RESQ-V01"),
        ("Field Officer Aarav Sen", "VOLUNTEER", "CONFIRM_DELIVERY", "DELIVERY", "RELIEF-2026-00482", "IN_TRANSIT", "DELIVERED", "Handover completed to Village A council with digital verification")
    ]

    for idx, (actor_n, actor_r, act, etype, eid, pstate, nstate, reason) in enumerate(audit_events):
        log_time = now - datetime.timedelta(hours=8 - idx)
        payload = f"{prev_hash}|{log_time.isoformat()}|{actor_n}|{actor_r}|{act}|{etype}|{eid}|{pstate or ''}|{nstate or ''}|{reason or ''}"
        curr_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        audit_entry = AuditLog(
            actor_id=1,
            actor_name=actor_n,
            actor_role=actor_r,
            action=act,
            entity_type=etype,
            entity_id=eid,
            previous_state=pstate,
            new_state=nstate,
            reason=reason,
            timestamp=log_time,
            prev_hash=prev_hash,
            curr_hash=curr_hash
        )
        db.add(audit_entry)
        prev_hash = curr_hash

    db.commit()
    print("Database seeding completed successfully! All 13 hackathon demo steps prepared.")
"""

with open(os.path.join(APP_DIR, "seed_data.py"), "w", encoding="utf-8") as f:
    f.write(seed_code)

print("seed_data.py written successfully.")
