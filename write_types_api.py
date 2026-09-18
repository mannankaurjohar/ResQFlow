import os

SRC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "src")
TYPES_DIR = os.path.join(SRC_DIR, "types")
SERVICES_DIR = os.path.join(SRC_DIR, "services")
os.makedirs(TYPES_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)

# 1. types/index.ts
types_ts = """export type UserRole = 
  | 'AUTHORITY'
  | 'VOLUNTEER'
  | 'NGO_MANAGER'
  | 'WAREHOUSE_MANAGER'
  | 'DONOR'
  | 'COMMUNITY'
  | 'ADMIN';

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'SEVERE';

export type RequestStatus = 
  | 'PENDING'
  | 'VERIFIED'
  | 'ALLOCATED'
  | 'PARTIALLY_FULFILLED'
  | 'IN_TRANSIT'
  | 'DELIVERED'
  | 'FLAGGED_DUPLICATE'
  | 'REJECTED';

export type ReliefStatus = 
  | 'DONATED'
  | 'RECEIVED'
  | 'VERIFIED'
  | 'STORED'
  | 'ALLOCATED'
  | 'DISPATCHED'
  | 'IN_TRANSIT'
  | 'DELIVERED';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
}

export interface ExtractedItem {
  category: string;
  item_name: string;
  quantity: number;
  unit: string;
}

export interface AIUnderstandingResponse {
  raw_text: string;
  extracted_location: string;
  latitude?: number;
  longitude?: number;
  affected_people: number;
  affected_households: number;
  vulnerable_elderly: number;
  vulnerable_children: number;
  vulnerable_total: number;
  urgency: string;
  items: ExtractedItem[];
  confidence_score: number;
  reasoning: string;
}

export interface RequestItem {
  id: number;
  category: string;
  item_name: string;
  requested_quantity: number;
  unit: string;
  fulfilled_quantity: number;
}

export interface RequestVerification {
  id: number;
  is_duplicate: boolean;
  duplicate_of_id?: number;
  similarity_score: number;
  notes?: string;
  action_taken: string;
}

export interface CommunityRequest {
  id: number;
  tracking_code: string;
  zone_id?: number;
  reporter_name?: string;
  reporter_phone?: string;
  reporter_role?: string;
  location_name: string;
  latitude: number;
  longitude: number;
  affected_people: number;
  affected_households: number;
  vulnerable_elderly: number;
  vulnerable_children: number;
  vulnerable_infants: number;
  vulnerable_pregnant: number;
  urgency: SeverityLevel;
  raw_description: string;
  priority_score: number;
  priority_classification: SeverityLevel;
  authority_override_score?: number;
  override_reason?: string;
  status: RequestStatus;
  created_at: string;
  items: RequestItem[];
  verifications: RequestVerification[];
}

export interface PriorityFactor {
  factor: string;
  points: number;
  reason: string;
}

export interface ExplainPriorityResponse {
  request_id: number;
  tracking_code: string;
  priority_score: number;
  priority_classification: string;
  factors: PriorityFactor[];
  authority_override_score?: number;
  override_reason?: string;
  override_by?: string;
}

export interface MatchedWarehouseItem {
  warehouse_id: number;
  warehouse_name: string;
  distance_km: number;
  item_name: string;
  category: string;
  available_qty: number;
  recommended_qty: number;
  unit: string;
  expiry_date?: string;
}

export interface AIResourceMatchRecommendation {
  request_id: number;
  request_tracking_code: string;
  location_name: string;
  priority_classification: string;
  priority_score: number;
  is_partial: boolean;
  summary_rationale: string;
  recommendations: MatchedWarehouseItem[];
  remaining_shortages: Array<{
    category: string;
    item_name: string;
    requested: number;
    fulfilled: number;
    shortage: number;
    unit: string;
  }>;
}

export interface InventoryItem {
  id: number;
  warehouse_id: number;
  warehouse_name?: string;
  category: string;
  item_name: string;
  unit: string;
  total_quantity: number;
  reserved_quantity: number;
  allocated_quantity: number;
  available_quantity: number;
  min_threshold: number;
  status: string;
  updated_at: string;
  batches: Array<{
    id: number;
    batch_number: string;
    quantity: number;
    expiry_date?: string;
    received_date: string;
  }>;
}

export interface TimelineStep {
  step: string;
  label: string;
  status: 'COMPLETED' | 'CURRENT' | 'PENDING';
  timestamp?: string;
  actor?: string;
  details?: string;
}

export interface ReliefTraceResponse {
  relief_id: string;
  donation_id?: string;
  donor_name?: string;
  request_tracking_code?: string;
  destination_location: string;
  destination_zone: string;
  current_status: ReliefStatus;
  people_supported: number;
  items_summary: Array<{
    category: string;
    item_name: string;
    quantity: number;
    unit: string;
  }>;
  origin_warehouse?: string;
  assigned_vehicle?: string;
  driver_contact?: string;
  timeline: TimelineStep[];
  proof_of_delivery?: {
    delivered_at: string;
    recipient_signature: string;
    proof_photo_url: string;
    notes?: string;
  };
}

export interface GisOverviewData {
  zones: Array<{
    id: number;
    name: string;
    code: string;
    severity_level: string;
    water_level_meters: number;
    population: number;
    households: number;
    center: [number, number];
    polygon: Array<[number, number]>;
    is_isolated: boolean;
    critical_requests_count: number;
  }>;
  requests: Array<{
    id: number;
    tracking_code: string;
    location_name: string;
    lat: number;
    lon: number;
    affected_people: number;
    vulnerable_count: number;
    urgency: string;
    priority_score: number;
    priority_classification: string;
    status: string;
    items: string[];
  }>;
  warehouses: Array<{
    id: number;
    name: string;
    code: string;
    lat: number;
    lon: number;
    capacity_sqm: number;
    inventory: Array<{
      item_name: string;
      category: string;
      available: number;
      unit: string;
      status: string;
    }>;
  }>;
  relief_centers: Array<{
    id: number;
    name: string;
    lat: number;
    lon: number;
    capacity: number;
    occupancy: number;
    has_medical: boolean;
  }>;
  deliveries: Array<{
    id: number;
    relief_id: string;
    status: string;
    destination: string;
    dest_lat: number;
    dest_lon: number;
    vehicle: string;
    driver?: string;
    waypoints: Array<{ lat: number; lon: number; name: string }>;
  }>;
  blocked_roads: Array<{
    name: string;
    lat: number;
    lon: number;
    reason: string;
    status: string;
  }>;
}

export interface AnalyticsData {
  people_affected: number;
  people_assisted: number;
  total_requests: number;
  fulfilled_requests: number;
  critical_requests_pending: number;
  fulfillment_rate_pct: number;
  active_deliveries: number;
  average_response_time_mins: number;
  average_delivery_time_mins: number;
  supply_demand_gap: Array<{
    category: string;
    demand: number;
    available: number;
    gap: number;
    fulfillment_pct: number;
  }>;
  resources_distributed: Array<{
    item: string;
    quantity: number;
    unit: string;
  }>;
  simulation_escalated: boolean;
}

export interface AuditLog {
  id: number;
  actor_name: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  previous_state?: string;
  new_state?: string;
  reason?: string;
  timestamp: string;
  prev_hash?: string;
  curr_hash: string;
}
"""

with open(os.path.join(TYPES_DIR, "index.ts"), "w", encoding="utf-8") as f:
    f.write(types_ts)

# 2. services/api.ts
api_ts = """import axios from 'axios';
import {
  AIUnderstandingResponse, CommunityRequest, ExplainPriorityResponse,
  AIResourceMatchRecommendation, InventoryItem, ReliefTraceResponse,
  GisOverviewData, AnalyticsData, AuditLog, User
} from '../types';

const API_BASE = 'http://localhost:8000/api';

const api = {
  // Demo users & auth
  async getDemoUsers(): Promise<User[]> {
    const res = await fetch(`${API_BASE}/auth/demo-users`);
    return res.json();
  },

  // Requests
  async parseNLP(text: string): Promise<AIUnderstandingResponse> {
    const res = await fetch(`${API_BASE}/requests/parse-nlp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error('Failed to parse text');
    return res.json();
  },

  async getRequests(params?: { status?: string; urgency?: string }): Promise<CommunityRequest[]> {
    let url = `${API_BASE}/requests`;
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.urgency) query.append('urgency', params.urgency);
    if (query.toString()) url += `?${query.toString()}`;
    const res = await fetch(url);
    return res.json();
  },

  async getRequestById(id: number): Promise<CommunityRequest> {
    const res = await fetch(`${API_BASE}/requests/${id}`);
    return res.json();
  },

  async createRequest(data: any): Promise<CommunityRequest> {
    const res = await fetch(`${API_BASE}/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create request');
    return res.json();
  },

  async getPriorityExplanation(requestId: number): Promise<ExplainPriorityResponse> {
    const res = await fetch(`${API_BASE}/requests/${requestId}/priority`);
    return res.json();
  },

  async overridePriority(requestId: number, overrideScore: number, reason: string): Promise<ExplainPriorityResponse> {
    const res = await fetch(`${API_BASE}/requests/${requestId}/override-priority`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ override_score: overrideScore, override_reason: reason })
    });
    return res.json();
  },

  async verifyRequest(requestId: number, action: string, notes?: string, duplicateOfId?: number): Promise<CommunityRequest> {
    const res = await fetch(`${API_BASE}/requests/${requestId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, notes, duplicate_of_id: duplicateOfId })
    });
    return res.json();
  },

  // Allocations & Matching
  async getMatchRecommendation(requestId: number): Promise<AIResourceMatchRecommendation> {
    const res = await fetch(`${API_BASE}/allocations/recommend/${requestId}`);
    return res.json();
  },

  async approveAllocation(payload: {
    request_id: number;
    warehouse_id: number;
    relief_id?: string;
    items: any[];
    override_notes?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/allocations/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to approve allocation');
    return res.json();
  },

  // Deliveries
  async getDeliveries(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/deliveries`);
    return res.json();
  },

  async dispatchDelivery(deliveryId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/deliveries/dispatch/${deliveryId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    return res.json();
  },

  async updateDeliveryStatus(deliveryId: number, status: string, notes?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/deliveries/${deliveryId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, notes })
    });
    return res.json();
  },

  // Inventory
  async getInventory(): Promise<InventoryItem[]> {
    const res = await fetch(`${API_BASE}/inventory`);
    return res.json();
  },

  async getInventoryAlerts(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/inventory/alerts`);
    return res.json();
  },

  // Donations & Trace
  async traceRelief(identifier: string): Promise<ReliefTraceResponse> {
    const res = await fetch(`${API_BASE}/donations/${encodeURIComponent(identifier)}/trace`);
    if (!res.ok) throw new Error('Relief record not found');
    return res.json();
  },

  async createDonation(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/donations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // GIS
  async getGisOverview(): Promise<GisOverviewData> {
    const res = await fetch(`${API_BASE}/gis/overview`);
    return res.json();
  },

  // Simulation
  async escalateSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/escalate`, { method: 'POST' });
    return res.json();
  },

  async resetSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' });
    return res.json();
  },

  async getSimulationStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/status`);
    return res.json();
  },

  // Analytics & Forecasts
  async getAnalytics(): Promise<AnalyticsData> {
    const res = await fetch(`${API_BASE}/analytics`);
    return res.json();
  },

  async getForecasts(): Promise<any> {
    const res = await fetch(`${API_BASE}/analytics/forecasts`);
    return res.json();
  },

  async getShortages(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/analytics/shortages`);
    return res.json();
  },

  // Audit
  async getAuditLogs(): Promise<AuditLog[]> {
    const res = await fetch(`${API_BASE}/audit`);
    return res.json();
  },

  async verifyAuditIntegrity(): Promise<{ total_records: number; is_chain_valid: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/audit/verify-integrity`);
    return res.json();
  }
};

export default api;
"""

with open(os.path.join(SERVICES_DIR, "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)

print("types/index.ts and services/api.ts written successfully.")
