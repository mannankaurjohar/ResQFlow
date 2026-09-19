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
)
from app.auth import get_password_hash


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
        print("Database already contains data, skipping seed.")
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
    # Commit
    # ---------------------------------------------------------

    db.commit()

    print("Database initialization completed successfully.")
    print("GIS disaster context initialized.")
    print("No fake operational relief data was seeded.")