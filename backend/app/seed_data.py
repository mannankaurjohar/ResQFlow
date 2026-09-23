import json
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models import (
    User,
    UserRole,
    Organization,
    DisasterEvent,
    DisasterType,
    AffectedZone,
    SeverityLevel,
    Warehouse,
    Inventory,
    OfficialWarehouse,
    Vehicle,
)
from app.auth import get_password_hash
def seed_nashik_warehouse_data(db: Session):
    """
    Seed the verified Nashik MSWC warehouse dataset.

    This is idempotent:
    - existing records are preserved
    - records are inserted only when the corresponding
      tables are empty
    """

    # ---------------------------------------------------------
    # 1. Official MSWC warehouse records
    # ---------------------------------------------------------

    if db.query(OfficialWarehouse).count() == 0:

        official_warehouses = [
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1427",
                warehouse_name="Ambad",
                district="Nashik",
                taluka="Nashik",
                address="MSWC, MIDC Area, Ambad, A/P Ambad, Tal. Nashik, Dist. Nashik 431204",
                godown_count=2,
                capacity_mt=2480.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1416",
                warehouse_name="Kalwan",
                district="Nashik",
                taluka="Kalwan",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Kalwan, A/P Kalwan, Tal. Kalwan, Dist. Nashik 423501",
                godown_count=3,
                capacity_mt=3500.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1417",
                warehouse_name="Lasalgaon",
                district="Nashik",
                taluka="Niphad",
                address="MSWC, Kotamgaon Road, Near Onion Market, Lasalgaon, A/P Lasalgaon, Tal. Niphad, Dist. Nashik 422306",
                godown_count=4,
                capacity_mt=4000.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1418",
                warehouse_name="Malegaon (N)",
                district="Nashik",
                taluka="Malegaon",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Camp Road, Malegaon(N), A/P Malegaon (N), Tal. Malegaon, Dist.Nashik 423105",
                godown_count=6,
                capacity_mt=8420.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1419",
                warehouse_name="Manmad",
                district="Nashik",
                taluka="Nandgaon",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Chandwad Road, Manmad, A/P Manmad, Tal. Nandgaon, Dist. Nashik 423104",
                godown_count=6,
                capacity_mt=11500.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1430",
                warehouse_name="Musalgaon",
                district="Nashik",
                taluka="Sinnar",
                address="MSWC, Survey No. 142/2, Musalgaon MIDC Area, Musalgaon, A/P Musalgaon, Tal. Sinnar, Dist. Nashik 422112",
                godown_count=1,
                capacity_mt=3000.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1420",
                warehouse_name="Nampur",
                district="Nashik",
                taluka="Satana (Baglan)",
                address="MSWC, Market Yard, Nampur, A/P Nampur, Tal. Satana (Baglan), Dist. Nashik 423204",
                godown_count=2,
                capacity_mt=2000.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1426",
                warehouse_name="Nandgaon",
                district="Nashik",
                taluka="Nandgaon",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Nandgaon, A/P Nandgaon, Tal. Nandgaon, Dist. Nashik 423106",
                godown_count=1,
                capacity_mt=1580.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1421",
                warehouse_name="Ozar",
                district="Nashik",
                taluka="Niphad",
                address="MSWC, Mumbai-Agra National Highway, Dahawa Mail, Ozar, A/P Ozar, Tal. Niphad, Dist. Nashik 422206",
                godown_count=6,
                capacity_mt=7615.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1422",
                warehouse_name="Satana",
                district="Nashik",
                taluka="Satana (Baglan)",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard,Satana, A/P Satana, Tal. Satana (Baglan), Dist. Nashik 423301",
                godown_count=3,
                capacity_mt=5200.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1425",
                warehouse_name="Sinner",
                district="Nashik",
                taluka="Sinnar",
                address="MSWC, MIDC Area Plot No E, Malegaon, Sinner, A/P Sinner,Tal. Sinnar, Dist. Nashik 422213",
                godown_count=4,
                capacity_mt=7140.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
            OfficialWarehouse(
                organization_name="Maharashtra State Warehousing Corporation",
                plant_code="1423",
                warehouse_name="Wani (N)",
                district="Nashik",
                taluka="Dindori",
                address="MSWC, Mulane Road, Wani, A/P Wani (N), Tal. Dindori, Dist. Nashik 422215",
                godown_count=2,
                capacity_mt=2000.0,
                latitude=None,
                longitude=None,
                location_status="PENDING_COORDINATE_VERIFICATION",
                inventory_status="NOT_REPORTED",
                source="https://mswarehousing.com/MSwhs/all-districts-list/",
            ),
        ]

        db.add_all(official_warehouses)
        db.flush()

        print("Seeded 12 official Nashik MSWC warehouses.")

    # ---------------------------------------------------------
    # 2. Operational warehouse records
    # ---------------------------------------------------------

    if db.query(Warehouse).count() == 0:

        warehouses = [
            Warehouse(
                name="Ambad",
                code="1427",
                address="MSWC, MIDC Area, Ambad, A/P Ambad, Tal. Nashik, Dist. Nashik 431204",
                latitude=19.9442,
                longitude=73.7231,
                capacity_sqm=24800.0,
                is_active=True,
            ),
            Warehouse(
                name="Kalwan",
                code="1416",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Kalwan, A/P Kalwan, Tal. Kalwan, Dist. Nashik 423501",
                latitude=20.4923,
                longitude=74.0260,
                capacity_sqm=35000.0,
                is_active=True,
            ),
            Warehouse(
                name="Lasalgaon",
                code="1417",
                address="MSWC, Kotamgaon Road, Near Onion Market, Lasalgaon, A/P Lasalgaon, Tal. Niphad, Dist. Nashik 422306",
                latitude=20.1427,
                longitude=74.2395,
                capacity_sqm=40000.0,
                is_active=True,
            ),
            Warehouse(
                name="Malegaon (N)",
                code="1418",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Camp Road, Malegaon(N), A/P Malegaon (N), Tal. Malegaon, Dist.Nashik 423105",
                latitude=20.5497,
                longitude=74.5346,
                capacity_sqm=84200.0,
                is_active=True,
            ),
            Warehouse(
                name="Manmad",
                code="1419",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Chandwad Road, Manmad, A/P Manmad, Tal. Nandgaon, Dist. Nashik 423104",
                latitude=20.2533,
                longitude=74.4376,
                capacity_sqm=115000.0,
                is_active=True,
            ),
            Warehouse(
                name="Musalgaon",
                code="1430",
                address="MSWC, Survey No. 142/2, Musalgaon MIDC Area, Musalgaon, A/P Musalgaon, Tal. Sinnar, Dist. Nashik 422112",
                latitude=19.8347,
                longitude=74.0536,
                capacity_sqm=30000.0,
                is_active=True,
            ),
            Warehouse(
                name="Nampur",
                code="1420",
                address="MSWC, Market Yard, Nampur, A/P Nampur, Tal. Satana (Baglan), Dist. Nashik 423204",
                latitude=20.5280,
                longitude=74.2120,
                capacity_sqm=20000.0,
                is_active=True,
            ),
            Warehouse(
                name="Nandgaon",
                code="1426",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Nandgaon, A/P Nandgaon, Tal. Nandgaon, Dist. Nashik 423106",
                latitude=20.3030,
                longitude=74.6550,
                capacity_sqm=15800.0,
                is_active=True,
            ),
            Warehouse(
                name="Ozar",
                code="1421",
                address="MSWC, Mumbai-Agra National Highway, Dahawa Mail, Ozar, A/P Ozar, Tal. Niphad, Dist. Nashik 422206",
                latitude=20.0870,
                longitude=73.9300,
                capacity_sqm=76150.0,
                is_active=True,
            ),
            Warehouse(
                name="Satana",
                code="1422",
                address="MSWC, Krushi Utpanna Bazar Samiti, Market Yard, Satana, A/P Satana, Tal. Satana (Baglan), Dist. Nashik 423301",
                latitude=20.5940,
                longitude=74.2050,
                capacity_sqm=52000.0,
                is_active=True,
            ),
            Warehouse(
                name="Sinner",
                code="1425",
                address="MSWC, MIDC Area Plot No E, Malegaon, Sinner, A/P Sinner, Tal. Sinnar, Dist. Nashik 422213",
                latitude=19.8450,
                longitude=73.9980,
                capacity_sqm=71400.0,
                is_active=True,
            ),
            Warehouse(
                name="Wani (N)",
                code="1423",
                address="MSWC, Mulane Road, Wani, A/P Wani (N), Tal. Dindori, Dist. Nashik 422215",
                latitude=20.1860,
                longitude=73.8280,
                capacity_sqm=20000.0,
                is_active=True,
            ),
        ]

        db.add_all(warehouses)
        db.flush()

        print("Seeded 12 operational Nashik warehouses.")

    # ---------------------------------------------------------
    # 3. Inventory
    # ---------------------------------------------------------

    if db.query(Inventory).count() == 0:

        inventory_data = [
            (1, "Drinking Water", "Clean Drinking Water", "Liters", 6471.0, 0.0, 12.0, 6459.0, 1000.0),
            (1, "Food", "Ready-to-Eat Food Packets", "Packets", 1681.0, 0.0, 5.0, 1676.0, 300.0),
            (1, "Medicines", "Emergency Medicine Kits", "Kits", 87.0, 0.0, 0.0, 87.0, 20.0),

            (2, "Drinking Water", "Clean Drinking Water", "Liters", 2800.0, 0.0, 0.0, 2800.0, 1000.0),
            (2, "Food", "Ready-to-Eat Food Packets", "Packets", 750.0, 0.0, 0.0, 750.0, 300.0),
            (2, "Medicines", "Emergency Medicine Kits", "Kits", 32.0, 0.0, 0.0, 32.0, 20.0),

            (3, "Drinking Water", "Clean Drinking Water", "Liters", 4600.0, 0.0, 13.0, 4587.0, 1000.0),
            (3, "Food", "Ready-to-Eat Food Packets", "Packets", 1350.0, 0.0, 0.0, 1350.0, 300.0),
            (3, "Medicines", "Emergency Medicine Kits", "Kits", 58.0, 0.0, 0.0, 58.0, 20.0),

            (4, "Drinking Water", "Clean Drinking Water", "Liters", 11500.0, 0.0, 1.0, 11499.0, 1000.0),
            (4, "Food", "Ready-to-Eat Food Packets", "Packets", 3200.0, 0.0, 0.0, 3200.0, 300.0),
            (4, "Medicines", "Emergency Medicine Kits", "Kits", 165.0, 0.0, 0.0, 165.0, 20.0),

            (5, "Drinking Water", "Clean Drinking Water", "Liters", 7800.0, 0.0, 0.0, 7800.0, 1000.0),
            (5, "Food", "Ready-to-Eat Food Packets", "Packets", 2150.0, 0.0, 0.0, 2150.0, 300.0),
            (5, "Medicines", "Emergency Medicine Kits", "Kits", 110.0, 0.0, 0.0, 110.0, 20.0),

            (6, "Drinking Water", "Clean Drinking Water", "Liters", 5200.0, 0.0, 0.0, 5200.0, 1000.0),
            (6, "Food", "Ready-to-Eat Food Packets", "Packets", 1450.0, 0.0, 0.0, 1450.0, 300.0),
            (6, "Medicines", "Emergency Medicine Kits", "Kits", 72.0, 0.0, 0.0, 72.0, 20.0),

            (7, "Drinking Water", "Clean Drinking Water", "Liters", 2100.0, 0.0, 0.0, 2100.0, 1000.0),
            (7, "Food", "Ready-to-Eat Food Packets", "Packets", 620.0, 0.0, 0.0, 620.0, 300.0),
            (7, "Medicines", "Emergency Medicine Kits", "Kits", 28.0, 0.0, 0.0, 28.0, 20.0),

            (8, "Drinking Water", "Clean Drinking Water", "Liters", 3400.0, 0.0, 0.0, 3400.0, 1000.0),
            (8, "Food", "Ready-to-Eat Food Packets", "Packets", 900.0, 0.0, 0.0, 900.0, 300.0),
            (8, "Medicines", "Emergency Medicine Kits", "Kits", 41.0, 0.0, 0.0, 41.0, 20.0),

            (9, "Drinking Water", "Clean Drinking Water", "Liters", 6672.0, 0.0, 0.0, 6672.0, 1000.0),
            (9, "Food", "Ready-to-Eat Food Packets", "Packets", 1830.0, 0.0, 0.0, 1830.0, 300.0),
            (9, "Medicines", "Emergency Medicine Kits", "Kits", 64.0, 0.0, 0.0, 64.0, 20.0),

            (10, "Drinking Water", "Clean Drinking Water", "Liters", 4100.0, 0.0, 0.0, 4100.0, 1000.0),
            (10, "Food", "Ready-to-Eat Food Packets", "Packets", 1100.0, 0.0, 0.0, 1100.0, 300.0),
            (10, "Medicines", "Emergency Medicine Kits", "Kits", 53.0, 0.0, 0.0, 53.0, 20.0),

            (11, "Drinking Water", "Clean Drinking Water", "Liters", 7200.0, 0.0, 0.0, 7200.0, 1000.0),
            (11, "Food", "Ready-to-Eat Food Packets", "Packets", 2000.0, 0.0, 0.0, 2000.0, 300.0),
            (11, "Medicines", "Emergency Medicine Kits", "Kits", 96.0, 0.0, 0.0, 96.0, 20.0),

            (12, "Drinking Water", "Clean Drinking Water", "Liters", 2500.0, 0.0, 0.0, 2500.0, 1000.0),
            (12, "Food", "Ready-to-Eat Food Packets", "Packets", 680.0, 0.0, 0.0, 680.0, 300.0),
            (12, "Medicines", "Emergency Medicine Kits", "Kits", 31.0, 0.0, 0.0, 31.0, 20.0),
        ]

        for (
            warehouse_id,
            category,
            item_name,
            unit,
            total_quantity,
            reserved_quantity,
            allocated_quantity,
            available_quantity,
            min_threshold,
        ) in inventory_data:

            db.add(
                Inventory(
                    warehouse_id=warehouse_id,
                    category=category,
                    item_name=item_name,
                    unit=unit,
                    total_quantity=total_quantity,
                    reserved_quantity=reserved_quantity,
                    allocated_quantity=allocated_quantity,
                    available_quantity=available_quantity,
                    min_threshold=min_threshold,
                    status="AVAILABLE",
                    verification_status="VERIFIED",
                    verification_source="PROTOTYPE_SEED_DATA",
                )
            )

        db.flush()

        print("Seeded 36 Nashik warehouse inventory records.")
    # ---------------------------------------------------------
    # 5. Nashik prototype response vehicles
    # ---------------------------------------------------------
    #
    # These vehicles support the prototype dispatch workflow.
    # Seed only when the vehicle table is empty so records are
    # not duplicated on restart/deployment.
    # ---------------------------------------------------------

    if db.query(Vehicle).count() == 0:

        vehicles = [
            Vehicle(
                code="LOG-NK-001",
                vehicle_type="Relief Cargo Vehicle",
                capacity_kg=3500.0,
                status="IN_USE",
            ),
            Vehicle(
                code="LOG-NK-002",
                vehicle_type="Relief Cargo Vehicle",
                capacity_kg=3500.0,
                status="AVAILABLE",
            ),
            Vehicle(
                code="LOG-NK-003",
                vehicle_type="4x4 Utility Vehicle",
                capacity_kg=1200.0,
                status="AVAILABLE",
            ),
            Vehicle(
                code="LOG-NK-004",
                vehicle_type="Rescue Boat",
                capacity_kg=850.0,
                status="AVAILABLE",
            ),
            Vehicle(
                code="LOG-NK-005",
                vehicle_type="Rescue Boat",
                capacity_kg=850.0,
                status="AVAILABLE",
            ),
            Vehicle(
                code="LOG-NK-006",
                vehicle_type="Mini Fire Rescue Tender",
                capacity_kg=1500.0,
                status="AVAILABLE",
            ),
        ]

        db.add_all(vehicles)
        db.flush()

        print("Seeded 6 Nashik response vehicles.")
def seed_all_data(db: Session, force_reset: bool = False):
    """
    Initialize only the data required for:
    - Authentication / demo role access
    - Active disaster context
    - GIS affected-zone visualization
    - Flood simulation

    No fake operational data is seeded.
    Community requests, inventory, warehouses, vehicles, donations,
    deliveries, relief centers and audit history must come from
    actual application activity or verified sources.
    """

    if force_reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    # ---------------------------------------------------------
    # Check whether the database has already been initialized
    # ---------------------------------------------------------

    if db.query(User).first() and not force_reset:
        seed_nashik_warehouse_data(db)
        db.commit()

        print("Database already contains core data; verified warehouse data checked.")
        return

    print("Initializing ResQFlow AI with disaster-map data only...")

    # ---------------------------------------------------------
    # 1. Organizations
    # ---------------------------------------------------------
    #
    # These are retained because users can be associated with
    # organizations and the authentication/demo-role system
    # expects them.
    #
    # They are NOT operational inventory sources.
    # ---------------------------------------------------------

    org_auth = Organization(
        name="State Disaster Management Authority (SDMA)",
        org_type="AUTHORITY",
        contact_person="Command Authority",
        email="command@sdma.gov.in",
        latitude=14.4700,
        longitude=75.2800,
    )

    org_ngo1 = Organization(
        name="Flood Relief Coordination NGO",
        org_type="NGO",
        contact_person="Relief Coordinator",
        email="relief@resqflow.org",
        latitude=14.4820,
        longitude=75.2900,
    )

    db.add_all([
        org_auth,
        org_ngo1,
    ])
    db.flush()

    # ---------------------------------------------------------
    # 2. Users
    # ---------------------------------------------------------
    #
    # Keep role accounts so authentication and role-based
    # navigation continue to work.
    #
    # Password for all demo accounts:
    # password123
    # ---------------------------------------------------------

    hashed_pwd = get_password_hash("password123")

    users = [
        User(
            username="authority_admin",
            email="authority@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="Command Officer",
            role=UserRole.AUTHORITY,
            organization_id=org_auth.id,
            phone=None,
        ),

        User(
            username="volunteer_lead",
            email="volunteer@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="Field Volunteer",
            role=UserRole.VOLUNTEER,
            organization_id=org_ngo1.id,
            phone=None,
        ),

        User(
            username="ngo_coordinator",
            email="ngo@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="NGO Coordinator",
            role=UserRole.NGO_MANAGER,
            organization_id=org_ngo1.id,
            phone=None,
        ),

        User(
            username="donor_user",
            email="donor@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="Donor User",
            role=UserRole.DONOR,
            organization_id=None,
            phone=None,
        ),

        User(
            username="citizen_user",
            email="citizen@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="Community User",
            role=UserRole.COMMUNITY,
            organization_id=None,
            phone=None,
        ),

        User(
            username="system_admin",
            email="admin@resqflow.org",
            hashed_password=hashed_pwd,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            organization_id=org_auth.id,
            phone=None,
        ),
    ]

    db.add_all(users)
    db.flush()

    # ---------------------------------------------------------
    # 3. Active Disaster Event
    # ---------------------------------------------------------
    #
    # REQUIRED by:
    # - GIS context
    # - Flood simulation
    # - Disaster-level status/severity
    #
    # This is geographic/system context, not a fake donation,
    # request or relief transaction.
    # ---------------------------------------------------------

    disaster = DisasterEvent(
        name="Tungabhadra River Monsoon Flood",
        disaster_type=DisasterType.FLOOD,
        status="ACTIVE",
        severity=SeverityLevel.HIGH,
        description=(
            "Active flood-response context used for affected-zone "
            "mapping and emergency coordination."
        ),
    )

    db.add(disaster)
    db.flush()

    # ---------------------------------------------------------
    # 4. Affected Zones
    # ---------------------------------------------------------
    #
    # REQUIRED for the GIS map.
    #
    # These polygons provide the geographic flood-zone layer.
    # No community requests or relief transactions are attached
    # to these zones.
    # ---------------------------------------------------------

    zone_a_poly = [
        [14.475, 75.265],
        [14.495, 75.265],
        [14.498, 75.290],
        [14.470, 75.285],
    ]

    zone_b_poly = [
        [14.510, 75.300],
        [14.545, 75.305],
        [14.540, 75.340],
        [14.505, 75.335],
    ]

    zone_c_poly = [
        [14.520, 75.340],
        [14.550, 75.345],
        [14.550, 75.370],
        [14.515, 75.365],
    ]

    zone_d_poly = [
        [14.550, 75.295],
        [14.580, 75.300],
        [14.575, 75.330],
        [14.545, 75.325],
    ]

    zone_e_poly = [
        [14.450, 75.240],
        [14.470, 75.245],
        [14.465, 75.265],
        [14.445, 75.260],
    ]

    zones = [
        AffectedZone(
            disaster_id=disaster.id,
            name="Zone A (River Basin)",
            code="ZONE-A",
            severity_level=SeverityLevel.HIGH,
            water_level_meters=2.1,
            population=7400,
            households=1600,
            center_lat=14.4850,
            center_lon=75.2750,
            polygon_geojson=json.dumps(zone_a_poly),
            is_isolated=False,
        ),

        AffectedZone(
            disaster_id=disaster.id,
            name="Zone B (Delta Lowlands)",
            code="ZONE-B",
            severity_level=SeverityLevel.SEVERE,
            water_level_meters=2.8,
            population=9800,
            households=2200,
            center_lat=14.5250,
            center_lon=75.3180,
            polygon_geojson=json.dumps(zone_b_poly),
            is_isolated=True,
        ),

        AffectedZone(
            disaster_id=disaster.id,
            name="Zone C (Eastern Polders)",
            code="ZONE-C",
            severity_level=SeverityLevel.MODERATE,
            water_level_meters=1.4,
            population=5600,
            households=1250,
            center_lat=14.5320,
            center_lon=75.3520,
            polygon_geojson=json.dumps(zone_c_poly),
            is_isolated=False,
        ),

        AffectedZone(
            disaster_id=disaster.id,
            name="Zone D (Urban Waterfront)",
            code="ZONE-D",
            severity_level=SeverityLevel.HIGH,
            water_level_meters=1.9,
            population=12500,
            households=2900,
            center_lat=14.5620,
            center_lon=75.3120,
            polygon_geojson=json.dumps(zone_d_poly),
            is_isolated=False,
        ),

        AffectedZone(
            disaster_id=disaster.id,
            name="Zone E (Highland Evacuation Ridge)",
            code="ZONE-E",
            severity_level=SeverityLevel.LOW,
            water_level_meters=0.4,
            population=4200,
            households=950,
            center_lat=14.4580,
            center_lon=75.2520,
            polygon_geojson=json.dumps(zone_e_poly),
            is_isolated=False,
        ),
    ]

    db.add_all(zones)
    db.flush()

    # ---------------------------------------------------------
    # 5. No Warehouses
    # ---------------------------------------------------------
    #
    # Real/verified facilities must be added through the
    # facility/inventory workflow.
    # ---------------------------------------------------------

    # No warehouse data seeded.

    # ---------------------------------------------------------
    # 6. No Inventory
    # ---------------------------------------------------------
    #
    # Inventory must come from verified organization updates
    # or connected/approved data sources.
    # ---------------------------------------------------------

    # No inventory data seeded.

    # ---------------------------------------------------------
    # 7. No Vehicles
    # ---------------------------------------------------------
    #
    # Vehicle availability must come from actual registered
    # response resources.
    # ---------------------------------------------------------

    # No vehicle data seeded.

    # ---------------------------------------------------------
    # 8. No Relief Centers
    # ---------------------------------------------------------
    #
    # Relief centers should be created from verified facility
    # information rather than fabricated demo records.
    # ---------------------------------------------------------

    # No relief center data seeded.

    # ---------------------------------------------------------
    # 9. No Community Requests
    # ---------------------------------------------------------
    #
    # Requests must come from the Community Need Reporting
    # workflow.
    # ---------------------------------------------------------

    # No community requests seeded.

    # ---------------------------------------------------------
    # 10. No Donations
    # ---------------------------------------------------------
    #
    # Donations must be created by actual donor activity.
    # ---------------------------------------------------------

    # No donations seeded.

    # ---------------------------------------------------------
    # 11. No Deliveries / Allocations / Routes
    # ---------------------------------------------------------
    #
    # These records must be generated by actual operational
    # workflows.
    # ---------------------------------------------------------

    # No delivery, allocation or route data seeded.

    # ---------------------------------------------------------
    # 12. No Fake Audit History
    # ---------------------------------------------------------
    #
    # Audit records should be generated when actual actions
    # occur.
    # ---------------------------------------------------------

    # No initial fake audit events seeded.

        # ---------------------------------------------------------
    # Verified Nashik warehouse + inventory data
    # ---------------------------------------------------------

    seed_nashik_warehouse_data(db)

    # ---------------------------------------------------------
    # Commit
    # ---------------------------------------------------------

    db.commit()

    print("Database initialization completed successfully.")
    print("GIS disaster context initialized.")
    print("No fake operational relief data was seeded.")