from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
import enum
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    AUTHORITY = "AUTHORITY"
    VOLUNTEER = "VOLUNTEER"
    NGO_MANAGER = "NGO_MANAGER"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER"
    DONOR = "DONOR"
    COMMUNITY = "COMMUNITY"
    ADMIN = "ADMIN"

class DisasterType(str, enum.Enum):
    FLOOD = "FLOOD"
    CYCLONE = "CYCLONE"
    EARTHQUAKE = "EARTHQUAKE"
    LANDSLIDE = "LANDSLIDE"
    WILDFIRE = "WILDFIRE"

class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ALLOCATED = "ALLOCATED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FLAGGED_DUPLICATE = "FLAGGED_DUPLICATE"
    REJECTED = "REJECTED"

class ReliefStatus(str, enum.Enum):
    DONATED = "DONATED"
    RECEIVED = "RECEIVED"
    VERIFIED = "VERIFIED"
    STORED = "STORED"
    ALLOCATED = "ALLOCATED"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    org_type = Column(String(50), nullable=False) # NGO, WAREHOUSE, AUTHORITY, RELIEF_CAMP
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    users = relationship("User", back_populates="organization")
    warehouses = relationship("Warehouse", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.COMMUNITY, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    organization = relationship("Organization", back_populates="users")

class DisasterEvent(Base):
    __tablename__ = "disaster_events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    disaster_type = Column(SQLEnum(DisasterType), default=DisasterType.FLOOD, nullable=False)
    status = Column(String(50), default="ACTIVE")
    severity = Column(SQLEnum(SeverityLevel), default=SeverityLevel.HIGH, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    zones = relationship("AffectedZone", back_populates="disaster")

class AffectedZone(Base):
    __tablename__ = "affected_zones"
    id = Column(Integer, primary_key=True, index=True)
    disaster_id = Column(Integer, ForeignKey("disaster_events.id"), nullable=False)
    name = Column(String(120), nullable=False)
    code = Column(String(30), unique=True, index=True, nullable=False)
    severity_level = Column(SQLEnum(SeverityLevel), default=SeverityLevel.MODERATE, nullable=False)
    water_level_meters = Column(Float, default=1.5)
    population = Column(Integer, default=5000)
    households = Column(Integer, default=1200)
    polygon_geojson = Column(Text, nullable=True)
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    is_isolated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    disaster = relationship("DisasterEvent", back_populates="zones")
    requests = relationship("CommunityRequest", back_populates="zone")
    relief_centers = relationship("ReliefCenter", back_populates="zone")

class CommunityRequest(Base):
    __tablename__ = "community_requests"
    id = Column(Integer, primary_key=True, index=True)
    tracking_code = Column(String(50), unique=True, index=True, nullable=False)
    zone_id = Column(Integer, ForeignKey("affected_zones.id"), nullable=True)
    reporter_name = Column(String(100), nullable=True)
    reporter_phone = Column(String(50), nullable=True)
    reporter_role = Column(String(50), default="Citizen")
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    affected_people = Column(Integer, default=1)
    affected_households = Column(Integer, default=1)
    vulnerable_elderly = Column(Integer, default=0)
    vulnerable_children = Column(Integer, default=0)
    vulnerable_infants = Column(Integer, default=0)
    vulnerable_pregnant = Column(Integer, default=0)
    urgency = Column(SQLEnum(SeverityLevel), default=SeverityLevel.HIGH, nullable=False)
    raw_description = Column(Text, nullable=False)
    ai_extracted_json = Column(Text, nullable=True)
    
    priority_score = Column(Float, default=50.0)
    priority_classification = Column(SQLEnum(SeverityLevel), default=SeverityLevel.MEDIUM)
    priority_factors_json = Column(Text, nullable=True)
    authority_override_score = Column(Float, nullable=True)
    override_reason = Column(Text, nullable=True)
    override_by = Column(String(100), nullable=True)
    
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    updated_at = Column(DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))

    zone = relationship("AffectedZone", back_populates="requests")
    items = relationship("RequestItem", back_populates="request", cascade="all, delete-orphan")
    verifications = relationship("RequestVerification", foreign_keys="RequestVerification.request_id", back_populates="request")
    allocations = relationship("Allocation", back_populates="request")

class RequestItem(Base):
    __tablename__ = "request_items"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("community_requests.id"), nullable=False)
    category = Column(String(80), nullable=False)
    item_name = Column(String(150), nullable=False)
    requested_quantity = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)
    fulfilled_quantity = Column(Float, default=0.0)

    request = relationship("CommunityRequest", back_populates="items")

class RequestVerification(Base):
    __tablename__ = "request_verifications"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("community_requests.id"), nullable=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey("community_requests.id"), nullable=True)
    similarity_score = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    action_taken = Column(String(50), default="FLAGGED")
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    request = relationship("CommunityRequest", foreign_keys=[request_id], back_populates="verifications")

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String(120), nullable=False)
    code = Column(String(30), unique=True, index=True, nullable=False)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity_sqm = Column(Float, default=1000.0)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="warehouses")
    inventory = relationship("Inventory", back_populates="warehouse")
    allocations = relationship("Allocation", back_populates="warehouse")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    category = Column(
        String(80),
        nullable=False
    )

    item_name = Column(
        String(150),
        nullable=False
    )

    unit = Column(
        String(30),
        nullable=False
    )

    total_quantity = Column(
        Float,
        default=0.0
    )

    reserved_quantity = Column(
        Float,
        default=0.0
    )

    allocated_quantity = Column(
        Float,
        default=0.0
    )

    available_quantity = Column(
        Float,
        default=0.0
    )

    min_threshold = Column(
        Float,
        default=100.0
    )

    status = Column(
        String(50),
        default="AVAILABLE"
    )

    # -------------------------------------------------
    # INVENTORY TRUST / VERIFICATION
    # -------------------------------------------------

    verification_status = Column(
        String(30),
        default="UNKNOWN",
        nullable=False
    )

    verification_source = Column(
        String(255),
        nullable=True
    )

    verified_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    verified_at = Column(
        DateTime,
        nullable=True
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(IST),
        onupdate=lambda: datetime.now(IST)
    )

    warehouse = relationship(
        "Warehouse",
        back_populates="inventory"
    )

    batches = relationship(
        "InventoryBatch",
        back_populates="inventory"
    )
   

class InventoryBatch(Base):
    __tablename__ = "inventory_batches"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    batch_number = Column(String(60), nullable=False)
    quantity = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    inventory = relationship("Inventory", back_populates="batches")

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    donor_name = Column(String(100), nullable=False)
    donor_email = Column(String(120), nullable=True)
    tracking_id = Column(String(50), unique=True, index=True, nullable=False)
    relief_id = Column(String(50), unique=True, index=True, nullable=False)
    target_zone_id = Column(Integer, ForeignKey("affected_zones.id"), nullable=True)
    status = Column(SQLEnum(ReliefStatus), default=ReliefStatus.DONATED, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    items = relationship("DonationItem", back_populates="donation")

class DonationItem(Base):
    __tablename__ = "donation_items"
    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
    category = Column(String(80), nullable=False)
    item_name = Column(String(150), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)

    donation = relationship("Donation", back_populates="items")

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("community_requests.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    relief_id = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(String(50), default="RECOMMENDED")
    ai_score = Column(Float, default=85.0)
    ai_rationale = Column(Text, nullable=True)
    is_partial = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    override_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    request = relationship("CommunityRequest", back_populates="allocations")
    warehouse = relationship("Warehouse", back_populates="allocations")
    items = relationship("AllocationItem", back_populates="allocation")
    delivery = relationship("Delivery", back_populates="allocation", uselist=False)

class AllocationItem(Base):
    __tablename__ = "allocation_items"
    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(Integer, ForeignKey("allocations.id"), nullable=False)
    category = Column(String(80), nullable=False)
    item_name = Column(String(150), nullable=False)
    requested_quantity = Column(Float, nullable=False)
    allocated_quantity = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)

    allocation = relationship("Allocation", back_populates="items")

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(50), default="All-Terrain Truck")
    capacity_kg = Column(Float, default=2000.0)
    status = Column(String(50), default="AVAILABLE")
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(50), nullable=True)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)

    deliveries = relationship("Delivery", back_populates="vehicle")

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    relief_id = Column(String(50), unique=True, index=True, nullable=False)
    allocation_id = Column(Integer, ForeignKey("allocations.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(50), nullable=True)
    origin_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    destination_location_name = Column(String(150), nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lon = Column(Float, nullable=False)
    status = Column(SQLEnum(ReliefStatus), default=ReliefStatus.ALLOCATED, nullable=False)
    dispatched_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    in_transit_at = Column(DateTime, nullable=True)
    estimated_delivery_at = Column(DateTime, nullable=True)
    proof_photo_url = Column(String(255), nullable=True)
    recipient_signature = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    allocation = relationship("Allocation", back_populates="delivery")
    vehicle = relationship("Vehicle", back_populates="deliveries")
    route = relationship("Route", back_populates="delivery", uselist=False)

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    waypoints_json = Column(Text, nullable=True)
    total_distance_km = Column(Float, default=10.0)
    estimated_time_mins = Column(Integer, default=30)
    avoids_flooded_bridges = Column(Boolean, default=True)

    delivery = relationship("Delivery", back_populates="route")

class ReliefCenter(Base):
    __tablename__ = "relief_centers"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("affected_zones.id"), nullable=False)
    name = Column(String(120), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=1000)
    current_occupancy = Column(Integer, default=450)
    contact_phone = Column(String(50), nullable=True)
    has_medical_post = Column(Boolean, default=True)

    zone = relationship("AffectedZone", back_populates="relief_centers")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True)
    actor_name = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    prev_hash = Column(String(64), nullable=True)
    curr_hash = Column(String(64), nullable=False)
class OfficialWarehouse(Base):
    __tablename__ = "official_warehouses"

    id = Column(Integer, primary_key=True, index=True)

    organization_name = Column(
        String(150),
        nullable=False
    )

    plant_code = Column(
        String(30),
        unique=True,
        index=True,
        nullable=False
    )

    warehouse_name = Column(
        String(120),
        nullable=False
    )

    district = Column(
        String(100),
        nullable=False
    )

    taluka = Column(
        String(100),
        nullable=True
    )

    address = Column(
        String(500),
        nullable=False
    )

    godown_count = Column(
        Integer,
        nullable=True
    )

    capacity_mt = Column(
        Float,
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    location_status = Column(
        String(50),
        default="PENDING_COORDINATE_VERIFICATION",
        nullable=False
    )

    inventory_status = Column(
        String(50),
        default="NOT_REPORTED",
        nullable=False
    )

    source = Column(
        String(255),
        nullable=False
    )

    source_verified_at = Column(
        DateTime,
        default=lambda: datetime.now(IST)
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(IST)
    )