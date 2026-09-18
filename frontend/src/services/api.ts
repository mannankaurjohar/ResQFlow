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

const API_BASE = 'http://resqflow-ai-backend.onrender.com/api';

const api = {
  // ============================================================
  // Demo users & auth
  // ============================================================

  async getDemoUsers(): Promise<User[]> {
    const res = await fetch(
      `${API_BASE}/auth/demo-users`
    );

    return res.json();
  },

  // ============================================================
  // Requests
  // ============================================================

  async parseNLP(
    text: string
  ): Promise<AIUnderstandingResponse> {
    const res = await fetch(
      `${API_BASE}/requests/parse-nlp`,
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
    }
  ): Promise<CommunityRequest[]> {

    let url =
      `${API_BASE}/requests`;

    const query =
      new URLSearchParams();

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
      url += `?${query.toString()}`;
    }

    const res =
      await fetch(url);

    return res.json();
  },

  async getRequestById(
    id: number
  ): Promise<CommunityRequest> {

    const res = await fetch(
      `${API_BASE}/requests/${id}`
    );

    return res.json();
  },

  async createRequest(
    data: any
  ): Promise<CommunityRequest> {

    const res = await fetch(
      `${API_BASE}/requests`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
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

  async getPriorityExplanation(
    requestId: number
  ): Promise<ExplainPriorityResponse> {

    const res = await fetch(
      `${API_BASE}/requests/${requestId}/priority`
    );

    return res.json();
  },

  async overridePriority(
    requestId: number,
    overrideScore: number,
    reason: string
  ): Promise<ExplainPriorityResponse> {

    const res = await fetch(
      `${API_BASE}/requests/${requestId}/override-priority`,
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
      `${API_BASE}/requests/${requestId}/verify`,
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

  // ============================================================
  // Allocations & Matching
  // ============================================================

  async getMatchRecommendation(
    requestId: number
  ): Promise<AIResourceMatchRecommendation> {

    const res = await fetch(
      `${API_BASE}/allocations/recommend/${requestId}`
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

  async approveAllocation(
    payload: {
      request_id: number;
      warehouse_id: number;
      relief_id?: string;
      items: any[];
      override_notes?: string;
    }
  ): Promise<any> {

    const res = await fetch(
      `${API_BASE}/allocations/approve`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify(
          payload
        )
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
      `${API_BASE}/deliveries`
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
      `${API_BASE}/deliveries/dispatch/${deliveryId}`,
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
    notes?: string
  ): Promise<any> {

    const res = await fetch(
      `${API_BASE}/deliveries/${deliveryId}/status`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify({
          status,
          notes
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
      `${API_BASE}/inventory`
    );

    return res.json();
  },

  async getInventoryAlerts(): Promise<any[]> {

    const res = await fetch(
      `${API_BASE}/inventory/alerts`
    );

    return res.json();
  },

  // ============================================================
  // Donations & Trace
  // ============================================================

  async traceRelief(
    identifier: string
  ): Promise<ReliefTraceResponse> {

    const res = await fetch(
      `${API_BASE}/donations/${encodeURIComponent(
        identifier
      )}/trace`
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

    const res = await fetch(
      `${API_BASE}/donations`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify(data)
      }
    );

    return res.json();
  },

  // ============================================================
  // GIS
  // ============================================================

  async getGisOverview(): Promise<GisOverviewData> {

    const res = await fetch(
      `${API_BASE}/gis/overview`
    );

    return res.json();
  },

  // ============================================================
  // Simulation
  // ============================================================

  async escalateSimulation(): Promise<any> {

    const res = await fetch(
      `${API_BASE}/simulation/escalate`,
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
      `${API_BASE}/simulation/reset`,
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
      `${API_BASE}/simulation/status`
    );

    return res.json();
  },

  // ============================================================
  // Analytics & Forecasts
  // ============================================================

  async getAnalytics(): Promise<AnalyticsData> {

    const res = await fetch(
      `${API_BASE}/analytics`
    );

    return res.json();
  },

  async getForecasts(): Promise<any> {

    const res = await fetch(
      `${API_BASE}/analytics/forecasts`
    );

    return res.json();
  },

  async getShortages(): Promise<any[]> {

    const res = await fetch(
      `${API_BASE}/analytics/shortages`
    );

    return res.json();
  },

  // ============================================================
  // Audit
  // ============================================================

  async getAuditLogs(): Promise<AuditLog[]> {

    const res = await fetch(
      `${API_BASE}/audit`
    );

    return res.json();
  },

  async verifyAuditIntegrity(): Promise<{
    total_records: number;
    is_chain_valid: boolean;
    message: string;
  }> {

    const res = await fetch(
      `${API_BASE}/audit/verify-integrity`
    );

    return res.json();
  }
};

export default api;
