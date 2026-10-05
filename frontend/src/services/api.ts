import {
  AIUnderstandingResponse,
  CommunityRequest,
  ExplainPriorityResponse,
  AIResourceMatchRecommendation,
  InventoryItem,
  ReliefTraceResponse,
  GisOverviewData,
  AnalyticsData,
  AuditLog,
  User
} from '../types';
export const API_BASE =
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000/api';
const getAuthToken = (): string | null => {
  return localStorage.getItem('resqflow_token');
};

const publicFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  return fetch(url, {
    ...options,
    headers
  });
};
const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();

  const headers = new Headers(options.headers);

  headers.set('Content-Type', 'application/json');

  if (token) {
    headers.set(
      'Authorization',
      `Bearer ${token}`
    );
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  if (response.status === 401) {
    localStorage.removeItem('resqflow_token');
    localStorage.removeItem('resqflow_user');
  }

  return response;
};
export interface MatchedFacility {
  osm_id: number;
  osm_type: string;
  name: string;
  facility_type: string;
  support_role: string;
  distance_km: number;
  address: string;
  phone: string;
  website: string;
  source: string;
  source_url: string;
  live_inventory: string;
  operational_status: string;
}

export interface AIFacilitySupportRecommendation {
  request_id: number;
  request_tracking_code: string;
  location_name: string;
  summary_rationale: string;
  facilities: MatchedFacility[];
}

export interface PublicFacility {
  osm_id: number;
  osm_type: string;
  name: string;
  facility_type: string;
  latitude: number;
  longitude: number;
  address: string;
  phone: string;
  website: string;
  source: string;
  source_url: string;
  live_inventory: string;
}

export interface OfficialWarehouse {
  id: number;
  organization_name: string;
  plant_code: string;
  warehouse_name: string;
  district: string;
  taluka: string | null;
  address: string;
  godown_count: number | null;
  capacity_mt: number | null;
  latitude: number | null;
  longitude: number | null;
  location_status: string;
  inventory_status: string;
  source: string;
  source_verified_at: string | null;
}


const api = {
  // ============================================================
  // Public Facilities
  // ============================================================
async createProcurementManifest(
  requestId: number
): Promise<any> {
  const res = await fetch(
    API_BASE +
      '/allocations/procurement-manifest/' +
      requestId,
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json'
      }
    }
  );

  if (!res.ok) {
    let message =
      'Failed to create procurement manifest';

    try {
      const data =
        await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(
                data.detail
              );
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
  async getPublicFacilities(
    params?: {
      region?: string;
      latitude?: number;
      longitude?: number;
      radius_m?: number;
      facility_type?: string;
    }
  ): Promise<PublicFacility[]> {
    const query = new URLSearchParams();

    if (params?.region) {
      query.append(
        'region',
        params.region
      );
    } else {
      query.append(
        'latitude',
        String(params?.latitude ?? 20.0059)
      );

      query.append(
        'longitude',
        String(params?.longitude ?? 73.7897)
      );

      query.append(
        'radius_m',
        String(params?.radius_m ?? 15000)
      );
    }

    query.append(
      'facility_type',
      params?.facility_type ?? 'all'
    );

    const res = await fetch(
      API_BASE +
        '/public-data/facilities?' +
        query.toString()
    );

    if (!res.ok) {
      throw new Error(
        'Failed to load public facility data'
      );
    }

    const data = await res.json();

    return data.facilities ?? [];
  },
async getOfficialWarehouses(
  district: string = 'Nashik'
): Promise<OfficialWarehouse[]> {
  const res = await fetch(
    API_BASE +
      '/official-warehouses?district=' +
      encodeURIComponent(district)
  );

  if (!res.ok) {
    throw new Error(
      'Failed to fetch official warehouses'
    );
  }

  const data = await res.json();

  return data.warehouses || [];
},
    // ============================================================
  // Authentication
  // ============================================================

  async login(
    username: string,
    password: string,
    role: string
  ) {
    const res = await fetch(
      API_BASE + '/auth/login',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password,
          role
        })
      }
    );

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data?.detail || 'Login failed'
      );
    }

    localStorage.setItem(
      'resqflow_token',
      data.access_token
    );

    localStorage.setItem(
  'resqflow_user',
  JSON.stringify(data.user)
);

localStorage.setItem(
  'resqflow_password_reset_required',
  String(data.password_reset_required ?? false)
);

return data;
  },

  async getCurrentUser(): Promise<User> {
    const res = await authenticatedFetch(
      API_BASE + '/auth/me'
    );

    if (!res.ok) {
      throw new Error('Not authenticated');
    }

    return res.json();
  },
    async createWorker(data: {
    full_name: string;
    phone?: string;
    role: string;
    email?: string;
    organization_id?: number;
    assigned_warehouse_id?: number;
    unit_type?: string;
  }) {
    const res = await authenticatedFetch(
      API_BASE + '/auth/workers',
      {
        method: 'POST',
        body: JSON.stringify(data)
      }
    );

    const result = await res.json();

    if (!res.ok) {
      throw new Error(
        result?.detail ||
        'Failed to create user account'
      );
    }

    return result;
  },

  async getWorkers(): Promise<User[]> {
    const res = await authenticatedFetch(
      API_BASE + '/auth/workers'
    );

    const result = await res.json();

    if (!res.ok) {
      throw new Error(
        result?.detail ||
        'Failed to load users'
      );
    }

    return result;
  },

  async resetWorkerPassword(
    userId: number
  ) {
    const res = await authenticatedFetch(
      API_BASE +
        `/auth/workers/${userId}/reset-password`,
      {
        method: 'POST'
      }
    );

    const result = await res.json();

    if (!res.ok) {
      throw new Error(
        result?.detail ||
        'Failed to reset password'
      );
    }

    return result;
  },
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<User> {
    const res = await authenticatedFetch(
      API_BASE + '/auth/change-password',
      {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      }
    );

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data?.detail ||
        'Failed to change password'
      );
    }

    localStorage.setItem(
      'resqflow_password_reset_required',
      'false'
    );

    localStorage.setItem(
      'resqflow_user',
      JSON.stringify(data)
    );

    return data;
  },
  logout() {
    localStorage.removeItem('resqflow_token');
    localStorage.removeItem('resqflow_user');
  },

  // ============================================================
  // Requests
  // ============================================================

  async parseNLP(
    text: string
  ): Promise<AIUnderstandingResponse> {
    const res = await fetch(
      API_BASE + '/requests/parse-nlp',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text
        })
      }
    );

    if (!res.ok) {
      throw new Error(
        'Failed to parse text'
      );
    }

    return res.json();
  },

  async getRequests(
    params?: {
      status?: string;
      urgency?: string;
      exclude_assigned?: boolean;
    }
  ): Promise<CommunityRequest[]> {
    let url =
      API_BASE + '/requests';

    const query =
      new URLSearchParams();

    if (params?.exclude_assigned) {
      query.set('exclude_assigned', 'true');
    }

    if (params?.status) {
      query.append(
        'status',
        params.status
      );
    }

    if (params?.urgency) {
      query.append(
        'urgency',
        params.urgency
      );
    }

    if (query.toString()) {
      url +=
        '?' +
        query.toString();
    }

    const res =
      await fetch(url);

    return res.json();
  },
  async getMyRequests(
  phone: string
): Promise<CommunityRequest[]> {
  const res = await fetch(
    API_BASE +
      '/requests/my-requests?phone=' +
      encodeURIComponent(phone)
  );

  if (!res.ok) {
    let message = 'Failed to load your requests';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
async assignResponseTask(
  unitId: number,
  requestId: number
) {
  const res = await authenticatedFetch(
  `${API_BASE}/response-units/${unitId}/assign`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_id: requestId,
      }),
    }
  );

  if (!res.ok) {
    let message = 'Failed to assign response task';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
  async getRequestById(
    id: number
  ): Promise<CommunityRequest> {
    const res = await fetch(
      API_BASE +
        '/requests/' +
        id
    );

    return res.json();
  },

  async submitInboundSms(payload: { sender?: string; message: string }): Promise<CommunityRequest> {
    const res = await fetch(API_BASE + '/requests/sms-inbound', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error('Failed to ingest SMS packet');
    }
    return res.json();
  },

  async createRequest(
    data: any
  ): Promise<CommunityRequest> {
    const res = await publicFetch(
  API_BASE + '/requests',
  {
    method: 'POST',
    body: JSON.stringify(data)
  }
);

    if (!res.ok) {
      let message =
        'Failed to create request';

      try {
        const errorData =
          await res.json();

        if (errorData?.detail) {
          message =
            typeof errorData.detail ===
            'string'
              ? errorData.detail
              : JSON.stringify(
                  errorData.detail
                );
        }
      } catch {
        // Keep default message
      }

      throw new Error(message);
    }

    return res.json();
  },
async communitySignup(data: {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  password: string;
}) {
  const res = await fetch(
    API_BASE + '/auth/community-signup',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }
  );

  const result = await res.json();

  if (!res.ok) {
    throw new Error(
      result?.detail || 'Failed to create account'
    );
  }

  return result;
},
  async getPriorityExplanation(
    requestId: number
  ): Promise<ExplainPriorityResponse> {
    const res = await fetch(
      API_BASE +
        '/requests/' +
        requestId +
        '/priority'
    );

    return res.json();
  },

  async overridePriority(
    requestId: number,
    overrideScore: number,
    reason: string
  ): Promise<ExplainPriorityResponse> {
    const res = await fetch(
      API_BASE +
        '/requests/' +
        requestId +
        '/override-priority',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify({
          override_score:
            overrideScore,
          override_reason:
            reason
        })
      }
    );

    return res.json();
  },

  async verifyRequest(
    requestId: number,
    action: string,
    notes?: string,
    duplicateOfId?: number
  ): Promise<CommunityRequest> {
    const res = await fetch(
      API_BASE +
        '/requests/' +
        requestId +
        '/verify',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify({
          action,
          notes,
          duplicate_of_id:
            duplicateOfId
        })
      }
    );

    return res.json();
  },
async approveEvacuation(
  requestId: number
): Promise<CommunityRequest> {
  const res = await authenticatedFetch(
    API_BASE +
      '/requests/' +
      requestId +
      '/approve-evacuation',
    {
      method: 'POST'
    }
  );

  const data = await res.json();

  if (!res.ok) {
    throw new Error(
      data?.detail ||
      'Failed to approve evacuation'
    );
  }

  return data;
},

  // ============================================================
  // Allocations & Matching
  // ============================================================

  async getMatchRecommendation(
    requestId: number
  ): Promise<AIResourceMatchRecommendation> {
    const res = await fetch(
      API_BASE +
        '/allocations/recommend/' +
        requestId
    );

    if (!res.ok) {
      const text =
        await res.text();

      throw new Error(
        text ||
        'Failed to get resource recommendation'
      );
    }

    return res.json();
  },

  async getFacilitySupportRecommendation(
    requestId: number
  ): Promise<AIFacilitySupportRecommendation> {
    const res = await fetch(
      API_BASE +
        '/allocations/facility-support/' +
        requestId
    );

    if (!res.ok) {
      const text =
        await res.text();

      throw new Error(
        text ||
        'Failed to get facility support recommendation'
      );
    }

    return res.json();
  },

  async approveAllocation(
  payload: {
    request_id: number;
    relief_id?: string;
    items: Array<{
      warehouse_id: number;
      items: Array<{
        category: string;
        item_name: string;
        allocated_quantity: number;
        unit: string;
      }>;
    }>;
    override_notes?: string;
  }
): Promise<any[]> {
  const token = localStorage.getItem('token');
    const res = await authenticatedFetch(
  API_BASE + '/allocations/approve',
  {
    method: 'POST',
    body: JSON.stringify(payload)
  }
);

    if (!res.ok) {
      let message =
        'Failed to approve allocation';

      try {
        const data =
          await res.json();

        if (data?.detail) {
          message =
            typeof data.detail ===
            'string'
              ? data.detail
              : JSON.stringify(
                  data.detail
                );
        }
      } catch {
        // Keep default message
      }

      throw new Error(message);
    }

    return res.json();
  },

  // ============================================================
  // Deliveries
  // ============================================================

  async getDeliveries(): Promise<any[]> {
    const res = await fetch(
      API_BASE + '/deliveries'
    );

    if (!res.ok) {
      throw new Error(
        'Failed to load deliveries'
      );
    }

    return res.json();
  },

  // IMPORTANT:
  // Backend requires allocation_id in the request body.
  async dispatchDelivery(
    deliveryId: number,
    allocationId: number
  ): Promise<any> {
    const res = await fetch(
      API_BASE +
        '/deliveries/dispatch/' +
        deliveryId,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify({
          allocation_id:
            allocationId
        })
      }
    );

    if (!res.ok) {
      let message =
        'Failed to dispatch delivery';

      try {
        const data =
          await res.json();

        if (data?.detail) {
          message =
            typeof data.detail ===
            'string'
              ? data.detail
              : JSON.stringify(
                  data.detail
                );
        }
      } catch {
        // Keep default message
      }

      throw new Error(message);
    }

    return res.json();
  },

 async updateDeliveryStatus(
  deliveryId: number,
  status: string,
  notes?: string,
  proofPhotoUrl?: string,
  recipientSignature?: string
): Promise<any> {
  const res = await fetch(
    API_BASE +
      '/deliveries/' +
      deliveryId +
      '/status',
    {
      method: 'PATCH',
      headers: {
        'Content-Type':
          'application/json'
      },
      body: JSON.stringify({
        status,
        notes,
        proof_photo_url: proofPhotoUrl,
        recipient_signature: recipientSignature
      })
    }
  );

  if (!res.ok) {
    let message =
      'Failed to update delivery status';

    try {
      const data =
        await res.json();

      if (data?.detail) {
        message =
          typeof data.detail ===
          'string'
            ? data.detail
            : JSON.stringify(
                data.detail
              );
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},

  // ============================================================
  // Inventory
  // ============================================================

  async getInventory(): Promise<InventoryItem[]> {
    const res = await fetch(
      API_BASE + '/inventory'
    );

    return res.json();
  },

  async getInventoryAlerts(): Promise<any[]> {
    const res = await fetch(
      API_BASE + '/inventory/alerts'
    );

    return res.json();
  },
async getFloodAlerts(): Promise<any[]> {
  const response = await fetch(`${API_BASE}/flood-alerts`);

  if (!response.ok) {
    throw new Error("Failed to fetch live flood alerts");
  }

  const data = await response.json();
  return data.alerts ?? [];
},
  // ============================================================
  // Donations & Trace
  // ============================================================

  async traceRelief(
    identifier: string
  ): Promise<ReliefTraceResponse> {
    const encodedIdentifier =
      encodeURIComponent(identifier);

    const res = await fetch(
      API_BASE +
        '/donations/' +
        encodedIdentifier +
        '/trace'
    );

    if (!res.ok) {
      let message =
        'Relief record not found';

      try {
        const data =
          await res.json();

        if (data?.detail) {
          message =
            typeof data.detail ===
            'string'
              ? data.detail
              : JSON.stringify(
                  data.detail
                );
        }
      } catch {
        // Keep default message
      }

      throw new Error(message);
    }

    return res.json();
  },

async createDonation(
  data: any
): Promise<any> {
  const res = await publicFetch(
    API_BASE + '/donations',
    {
      method: 'POST',
      body: JSON.stringify(data)
    }
  );

  if (!res.ok) {
    let message = 'Failed to register donation';

    try {
      const responseData = await res.json();

      if (responseData?.detail) {
        message =
          typeof responseData.detail === 'string'
            ? responseData.detail
            : JSON.stringify(responseData.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
  // ============================================================
  // GIS
  // ============================================================

  async getGisOverview(): Promise<GisOverviewData> {
    const res = await fetch(
      API_BASE + '/gis/overview'
    );

    return res.json();
  },

  // ============================================================
  // Simulation
  // ============================================================

  async escalateSimulation(): Promise<any> {
    const res = await fetch(
      API_BASE +
        '/simulation/escalate',
      {
        method: 'POST'
      }
    );

    if (!res.ok) {
      throw new Error(
        'Simulation escalation failed'
      );
    }

    return res.json();
  },

  async resetSimulation(): Promise<any> {
    const res = await fetch(
      API_BASE +
        '/simulation/reset',
      {
        method: 'POST'
      }
    );

    if (!res.ok) {
      throw new Error(
        'Simulation reset failed'
      );
    }

    return res.json();
  },

  async getSimulationStatus(): Promise<any> {
    const res = await fetch(
      API_BASE +
        '/simulation/status'
    );

    return res.json();
  },

  // ============================================================
  // Analytics & Forecasts
  // ============================================================

  async getAnalytics(): Promise<AnalyticsData> {
    const res = await fetch(
      API_BASE + '/analytics'
    );

    return res.json();
  },

  async getForecasts(): Promise<any> {
    const res = await fetch(
      API_BASE +
        '/analytics/forecasts'
    );

    return res.json();
  },

  async getShortages(): Promise<any[]> {
    const res = await fetch(
      API_BASE +
        '/analytics/shortages'
    );

    return res.json();
  },
async getAdminDashboard(): Promise<{
  total_users: number;
  active_users: number;
  total_roles: number;
  total_organizations: number;
  role_distribution: Record<string, number>;
}> {
  const res = await authenticatedFetch(
    API_BASE + '/admin/dashboard'
  );

  if (!res.ok) {
    let message = 'Failed to load admin dashboard';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
// ============================================================
// RESPONSE UNITS
// ============================================================

getResponseUnits: async (): Promise<any[]> => {
  const response = await authenticatedFetch(
    `${API_BASE}/response-units`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));

    throw new Error(
      error.detail || 'Failed to load response units'
    );
  }

  return response.json();
},

createResponseUnit: async (data: {
  name: string;
  unit_type: string;
  location: string;
  members: number;
  operator_id: number;
}): Promise<any> => {
  const response = await authenticatedFetch(
    `${API_BASE}/response-units`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));

    throw new Error(
      error.detail || 'Failed to create response unit'
    );
  }

  return response.json();
},

getAvailableResponseUnits: async (): Promise<any[]> => {
  const response = await authenticatedFetch(
    `${API_BASE}/response-units/available`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));

    throw new Error(
      error.detail || 'Failed to load available response units'
    );
  }

  return response.json();
},
  // ============================================================
  // Audit
  // ============================================================

  async getAuditLogs(): Promise<AuditLog[]> {
  const res = await authenticatedFetch(
    API_BASE + '/audit'
  );

  if (!res.ok) {
    let message = 'Failed to load audit logs';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
async trackResponseRequest(
  requestRef: string | number
): Promise<any> {
  const response = await authenticatedFetch(
    `${API_BASE}/response-units/track/${encodeURIComponent(String(requestRef).trim())}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));

    throw new Error(
      error.detail || "Unable to load response tracking"
    );
  }

  return response.json();
},
async getMyResponseTasks() {
  const res = await authenticatedFetch(
  `${API_BASE}/response-units/my-tasks`
);

  if (!res.ok) {
    let message = 'Failed to load response tasks';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
async updateResponseTaskStatus(
  assignmentId: number,
  payload: {
    status: string;
    field_remarks?: string;
    people_assisted?: number;
    people_rescued?: number;
    shelter_destination?: string;
  }
) {
  const res = await authenticatedFetch(
  `${API_BASE}/response-units/tasks/${assignmentId}/status`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }
  );

  if (!res.ok) {
    let message = 'Failed to update response task';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
  async verifyAuditIntegrity(): Promise<{
  total_records: number;
  is_chain_valid: boolean;
  broken_block_id: number | null;
  message: string;
}> {
  const res = await authenticatedFetch(
    API_BASE + '/audit/verify-integrity'
  );

  if (!res.ok) {
    let message = 'Failed to verify audit integrity';

    try {
      const data = await res.json();

      if (data?.detail) {
        message =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return res.json();
},
};

export default api;
 
 
 

