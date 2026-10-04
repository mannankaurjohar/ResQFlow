import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole, SeverityLevel, RequestStatus, ReliefStatus

# Auth Schemas

class UserLogin(BaseModel):
    username: str
    password: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    organization_id: Optional[int] = None
    phone: Optional[str] = None
    is_active: bool

    # Used by the Admin Users page to determine
    # whether the worker is currently online.
    last_seen_at: Optional[datetime.datetime] = None

    # Warehouse Managers are assigned to one warehouse.
    assigned_warehouse_id: Optional[int] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    password_reset_required: bool = False


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# -------------------------------------------------
# Worker / Admin Schemas
# -------------------------------------------------

class WorkerCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    role: UserRole
    email: Optional[EmailStr] = None
    organization_id: Optional[int] = None
    assigned_warehouse_id: Optional[int] = None


class WorkerCreateResponse(BaseModel):
    user: UserResponse
    login_id: str
    temporary_password: str


class WorkerResetPasswordResponse(BaseModel):
    user: UserResponse
    login_id: str
    temporary_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


class HeartbeatResponse(BaseModel):
    status: str
    last_seen_at: datetime.datetime


class LogoutResponse(BaseModel):
    status: str


class WorkerAccessResponse(BaseModel):
    status: str
    user: UserResponse
# NLP AI Extraction Schemas
class ExtractedItem(BaseModel):
    category: str
    item_name: str
    quantity: float
    unit: str

class AIUnderstandingResponse(BaseModel):
    raw_text: str
    extracted_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    affected_people: int
    affected_households: int
    vulnerable_elderly: int
    vulnerable_children: int
    vulnerable_total: int
    urgency: str
    items: List[ExtractedItem]
    confidence_score: float
    reasoning: str

# Request Schemas
class RequestItemCreate(BaseModel):
    category: str
    item_name: str
    requested_quantity: float
    unit: str

class RequestItemResponse(BaseModel):
    id: int
    category: str
    item_name: str
    requested_quantity: float
    unit: str
    fulfilled_quantity: float

    class Config:
        from_attributes = True

class CommunityRequestCreate(BaseModel):
    reporter_name: Optional[str] = "Citizen"
    reporter_phone: Optional[str] = None
    reporter_role: Optional[str] = "Citizen"
    location_name: str
    zone_id: Optional[int] = None
    latitude: float
    longitude: float
    affected_people: int = 1
    affected_households: int = 1
    vulnerable_elderly: int = 0
    vulnerable_children: int = 0
    vulnerable_infants: int = 0
    vulnerable_pregnant: int = 0
    urgency: SeverityLevel = SeverityLevel.HIGH
    raw_description: str
    items: List[RequestItemCreate]

class VerificationResponse(BaseModel):
    id: int
    is_duplicate: bool
    duplicate_of_id: Optional[int] = None
    similarity_score: float
    notes: Optional[str] = None
    action_taken: str

    class Config:
        from_attributes = True

class PriorityFactor(BaseModel):
    factor: str
    points: float
    reason: str

class ExplainPriorityResponse(BaseModel):
    request_id: int
    tracking_code: str
    priority_score: float
    priority_classification: str
    factors: List[PriorityFactor]
    authority_override_score: Optional[float] = None
    override_reason: Optional[str] = None
    override_by: Optional[str] = None

class OverridePriorityRequest(BaseModel):
    override_score: float
    override_reason: str

class VerifyRequestInput(BaseModel):
    action: str # APPROVED, MERGED, REJECTED
    notes: Optional[str] = None
    duplicate_of_id: Optional[int] = None

class CommunityRequestResponse(BaseModel):
    id: int
    tracking_code: str
    zone_id: Optional[int] = None
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    reporter_role: Optional[str] = None
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    affected_people: int
    affected_households: int
    vulnerable_elderly: int
    vulnerable_children: int
    vulnerable_infants: int
    vulnerable_pregnant: int
    urgency: SeverityLevel
    raw_description: str
    priority_score: float
    priority_classification: SeverityLevel
    authority_override_score: Optional[float] = None
    override_reason: Optional[str] = None
    status: RequestStatus
    request_type: Optional[str] = "EVACUATION"
    communication_method: Optional[str] = "INTERNET"
    communication_status: Optional[str] = "RECEIVED"
    location_accuracy: Optional[float] = None
    medical_emergency: Optional[bool] = False
    medical_conditions_json: Optional[str] = None
    immediate_danger: Optional[str] = None
    danger_details_json: Optional[str] = None
    situation_flags_json: Optional[str] = None
    location_type: Optional[str] = None
    rescuer_access: Optional[str] = None
    access_problem_json: Optional[str] = None
    accessibility_json: Optional[str] = None
    photo_url: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at: datetime.datetime
    items: List[RequestItemResponse] = []
    verifications: List[VerificationResponse] = []

    class Config:
        from_attributes = True

# Citizen Emergency Ingestion Schemas
class CitizenItemPayload(BaseModel):
    category: str = "Rescue"
    item_name: str
    requested_quantity: float = 1.0
    unit: str = "Units"

class CitizenEmergencyRequestCreate(BaseModel):
    idempotency_key: Optional[str] = None
    tracking_code: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    request_type: str = "EVACUATION" # EVACUATION, SUPPLIES
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy: Optional[float] = None
    location_name: Optional[str] = None
    affected_people: int = 1
    adults: Optional[int] = None
    children: Optional[int] = None
    elderly: Optional[int] = None
    mobility_assistance: Optional[int] = None
    situation_flags: List[str] = []
    situation_other: Optional[str] = None
    medical_emergency: bool = False
    medical_conditions: List[str] = []
    medical_other: Optional[str] = None
    immediate_danger: Optional[str] = "NOT_SURE" # YES, NO, NOT_SURE
    danger_details: List[str] = []
    danger_other: Optional[str] = None
    location_type: Optional[str] = None
    accessibility_requirements: List[str] = []
    rescuer_access: Optional[str] = "NOT_SURE"
    access_problems: List[str] = []
    access_other: Optional[str] = None
    additional_information: Optional[str] = None
    photo_url: Optional[str] = None
    communication_method: str = "INTERNET" # INTERNET, SMS, SATELLITE, OFFLINE
    communication_status: str = "SENT"
    items: Optional[List[CitizenItemPayload]] = None

class CitizenRequestSyncPayload(BaseModel):
    requests: List[CitizenEmergencyRequestCreate]

class CitizenSyncResponseItem(BaseModel):
    tracking_code: str
    status: str
    message: str
    received_at: datetime.datetime
    communication_method: str
    communication_status: str

class CitizenSyncResponse(BaseModel):
    synced_count: int
    results: List[CitizenSyncResponseItem]

# Inventory Schemas
class InventoryBatchResponse(BaseModel):
    id: int
    batch_number: str
    quantity: float
    expiry_date: Optional[datetime.datetime] = None
    

    class Config:
        from_attributes = True

class InventoryResponse(BaseModel):
    id: int
    warehouse_id: int
    warehouse_name: Optional[str] = None
    category: str
    item_name: str
    unit: str
    total_quantity: float
    reserved_quantity: float
    allocated_quantity: float
    available_quantity: float
    min_threshold: float
    status: str
    updated_at: datetime.datetime
    batches: List[InventoryBatchResponse] = []

    class Config:
        from_attributes = True


class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    capacity_sqm: float
    is_active: bool
    inventory: List[InventoryResponse] = []

    class Config:
        from_attributes = True
class InventoryReceiveRequest(BaseModel):
    warehouse_id: int
    category: str
    item_name: str
    unit: str
    quantity: float
    min_threshold: float = 100.0
    batch_number: str
    expiry_date: Optional[datetime.datetime] = None
    verification_source: Optional[str] = None


class InventoryVerifyRequest(BaseModel):
    verification_source: str

# Allocation & Matching Schemas
class MatchedWarehouseItem(BaseModel):
    warehouse_id: int
    warehouse_name: str
    distance_km: float
    item_name: str
    category: str
    available_qty: float
    recommended_qty: float
    unit: str
    expiry_date: Optional[str] = None

class AIResourceMatchRecommendation(BaseModel):
    request_id: int
    request_tracking_code: str
    location_name: str
    priority_classification: str
    priority_score: float
    is_partial: bool
    summary_rationale: str
    recommendations: List[MatchedWarehouseItem]
    remaining_shortages: List[Dict[str, Any]]

class MatchedFacility(BaseModel):
    osm_id: int
    osm_type: str
    name: str
    facility_type: str
    support_role: str
    distance_km: float
    address: str
    phone: str
    website: str
    source: str
    source_url: str
    live_inventory: str
    operational_status: str


class AIFacilitySupportRecommendation(BaseModel):
    request_id: int
    request_tracking_code: str
    location_name: str
    summary_rationale: str
    facilities: List[MatchedFacility]
    
class ApproveAllocationItem(BaseModel):
    category: str
    item_name: str
    allocated_quantity: float
    unit: str


class ApproveAllocationWarehouse(BaseModel):
    warehouse_id: int
    items: List[ApproveAllocationItem]


class ApproveAllocationRequest(BaseModel):
    request_id: int
    relief_id: Optional[str] = None
    items: List[ApproveAllocationWarehouse]
    override_notes: Optional[str] = None
class AllocationResponse(BaseModel):
    id: int
    request_id: int
    warehouse_id: int
    relief_id: str
    status: str
    ai_score: float
    ai_rationale: Optional[str] = None
    is_partial: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Delivery & Tracking Schemas
class DispatchDeliveryRequest(BaseModel):
    allocation_id: int
    vehicle_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    notes: Optional[str] = None

class UpdateDeliveryStatusRequest(BaseModel):
    status: ReliefStatus
    proof_photo_url: Optional[str] = None
    recipient_signature: Optional[str] = None
    notes: Optional[str] = None

class DeliveryResponse(BaseModel):
    id: int
    relief_id: str
    allocation_id: int
    vehicle_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    origin_warehouse_id: int
    destination_location_name: str
    destination_lat: float
    destination_lon: float
    status: ReliefStatus
    dispatched_at: Optional[datetime.datetime] = None
    delivered_at: Optional[datetime.datetime] = None
    proof_photo_url: Optional[str] = None
    recipient_signature: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TimelineStep(BaseModel):
    step: str
    label: str
    status: str # COMPLETED, CURRENT, PENDING
    created_at: Optional[str] = None
    actor: Optional[str] = None
    details: Optional[str] = None

class ReliefTraceResponse(BaseModel):
    relief_id: str
    donation_id: Optional[str] = None
    donor_name: Optional[str] = None
    request_tracking_code: Optional[str] = None
    destination_location: str
    destination_zone: str
    current_status: ReliefStatus
    people_supported: int
    items_summary: List[Dict[str, Any]]
    origin_warehouse: Optional[str] = None
    assigned_vehicle: Optional[str] = None
    driver_contact: Optional[str] = None
    timeline: List[TimelineStep]
    proof_of_delivery: Optional[Dict[str, Any]] = None

# Donation Schemas
class DonationItemCreate(BaseModel):
    category: str
    item_name: str
    quantity: float
    unit: str

class DonationCreate(BaseModel):
    donor_name: str
    donor_email: Optional[str] = None
    target_zone_id: Optional[int] = None
    notes: Optional[str] = None
    items: List[DonationItemCreate]

class DonationResponse(BaseModel):
    id: int
    tracking_id: str
    relief_id: str
    donor_name: str
    status: ReliefStatus
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# GIS Schemas
class ZoneGISFeature(BaseModel):
    id: int
    name: str
    code: str
    severity_level: str
    water_level_meters: float
    population: int
    households: int
    center: List[float] # [lat, lon]
    polygon: List[List[float]] # GeoJSON polygon coordinates
    is_isolated: bool
    critical_requests_count: int
    shortages: Dict[str, float]

class MapOverviewResponse(BaseModel):
    zones: List[ZoneGISFeature]
    requests: List[Dict[str, Any]]
    warehouses: List[Dict[str, Any]]
    relief_centers: List[Dict[str, Any]]
    deliveries: List[Dict[str, Any]]
    blocked_roads: List[Dict[str, Any]]

# Demand Forecasting
class ForecastItem(BaseModel):
    category: str
    hours_6: float
    hours_12: float
    hours_24: float
    unit: str
    confidence: float

class DemandForecastResponse(BaseModel):
    forecast_scope: str # ALL_ZONES or Zone specific
    generated_at: str
    disclaimer: str
    forecasts: List[ForecastItem]

# Audit Schemas
class AuditLogResponse(BaseModel):
    id: int
    actor_name: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    prev_hash: Optional[str] = None
    curr_hash: str

    class Config:
        from_attributes = True

class AuditIntegrityCheckResponse(BaseModel):
    total_records: int
    is_chain_valid: bool
    broken_block_id: Optional[int] = None
    message: str
# ============================================================
# RESPONSE UNIT / FIELD RESPONSE SCHEMAS
# ============================================================


from datetime import datetime


class ResponseUnitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    unit_type: str = Field(..., min_length=1, max_length=80)
    location: Optional[str] = Field(default=None, max_length=150)
    members: int = Field(default=1, ge=1)
    operator_id: int


class ResponseUnitResponse(BaseModel):
    id: int
    name: str
    unit_type: str
    location: Optional[str] = None
    members: int
    operator_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResponseAssignmentCreate(BaseModel):
    request_id: int
    response_unit_id: int


class ResponseAssignmentResponse(BaseModel):
    id: int
    request_id: int
    response_unit_id: int
    assigned_by_id: int
    status: str
    assigned_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    field_remarks: Optional[str] = None
    people_assisted: int = 0
    people_rescued: int = 0
    shelter_destination: Optional[str] = None

    class Config:
        from_attributes = True


class ResponseAssignmentStatusUpdate(BaseModel):
    status: str


class ResponseAssignmentComplete(BaseModel):
    people_assisted: int = Field(default=0, ge=0)
    people_rescued: int = Field(default=0, ge=0)
    shelter_destination: Optional[str] = Field(
        default=None,
        max_length=150
    )
    field_remarks: Optional[str] = None