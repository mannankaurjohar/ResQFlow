import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
import {
  Search,
  CheckCircle2,
  Clock3,
  Truck,
  Navigation,
  MapPin,
  Users,
  AlertTriangle,
  Radio,
  ShieldCheck,
  Activity,
  XCircle,
} from 'lucide-react';

type TrackingData = {
  request: {
    id: number;
    tracking_code?: string;
    status?: string;
    location_name?: string;
    latitude?: number;
    longitude?: number;
    affected_people?: number;
    affected_households?: number;
    urgency?: string;
    priority_score?: number;
    priority_classification?: string;
    request_type?: string;
    medical_emergency?: boolean;
    immediate_danger?: boolean;
    raw_description?: string;
    created_at?: string;
  };
  response: {
    current_status: string;
    assignment_id?: number | null;
    assigned_at?: string | null;
    accepted_at?: string | null;
    completed_at?: string | null;
    field_remarks?: string | null;
    people_assisted?: number;
    people_rescued?: number;
    shelter_destination?: string | null;
  };
  response_unit?: {
    id: number;
    name: string;
    unit_type: string;
    location?: string;
    members?: number;
    status?: string;
  } | null;
  timeline: {
    status: string;
    label: string;
    state: 'COMPLETED' | 'CURRENT' | 'PENDING';
    created_at?: string | null;
  }[];
};

const formatDate = (value?: string | null) => {
  if (!value) return 'Not recorded';

  return new Date(value).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
};

const statusLabel = (status?: string) => {
  if (!status) return 'Unknown';

  return status
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, char => char.toUpperCase());
};

const timelineIcon = (status: string) => {
  switch (status) {
    case 'SUBMITTED':
      return <Radio className="w-4 h-4" />;
    case 'VERIFIED':
      return <ShieldCheck className="w-4 h-4" />;
    case 'APPROVED':
      return <CheckCircle2 className="w-4 h-4" />;
    case 'ASSIGNED':
      return <Users className="w-4 h-4" />;
    case 'ACCEPTED':
      return <CheckCircle2 className="w-4 h-4" />;
    case 'IN_TRANSIT':
      return <Truck className="w-4 h-4" />;
    case 'ON_SCENE':
      return <MapPin className="w-4 h-4" />;
    case 'RESPONDING':
      return <Activity className="w-4 h-4" />;
    case 'COMPLETED':
      return <CheckCircle2 className="w-4 h-4" />;
    default:
      return <Clock3 className="w-4 h-4" />;
  }
};

export const TraceReliefPage: React.FC = () => {
  const { traceIdInput, setTraceIdInput } = useApp();

  const [currentId, setCurrentId] = useState(
    traceIdInput || ''
  );

  const [traceData, setTraceData] =
    useState<TrackingData | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrace = async (id: string) => {
    const value = id.trim();

    if (!value) {
      setTraceData(null);
      setError('Enter a real Request ID or Tracking Code.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await api.trackResponseRequest(value);

      setTraceData(data);
      setTraceIdInput(value);
    } catch (err: any) {
      console.error('Response tracking error:', err);

      setTraceData(null);

      setError(
        err?.message ||
        `No community request found for '${value}'.`
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (traceIdInput) {
      setCurrentId(traceIdInput);
      fetchTrace(traceIdInput);
    }
  }, [traceIdInput]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTrace(currentId);
  };

  const clearSearch = () => {
    setCurrentId('');
    setTraceData(null);
    setError(null);
    setTraceIdInput('');
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
          Response Tracking
        </h1>

        <p className="text-xs sm:text-sm text-slate mt-1">
          Track a real community request through verification,
          response-unit deployment, field response, and completion.
        </p>
      </div>

      {/* Search */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-4 shadow-soft">
        <form
          onSubmit={handleSearch}
          className="flex flex-col sm:flex-row gap-2"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate absolute left-3.5 top-3.5" />

            <input
              type="text"
              value={currentId}
              onChange={e => setCurrentId(e.target.value)}
              placeholder="Enter real Request ID or Tracking Code"
              className="w-full bg-white border border-slate/30 text-navy font-mono rounded-lg pl-10 pr-4 py-2.5 text-xs sm:text-sm focus:outline-none focus:border-terracotta"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-navy hover:bg-navy-800 disabled:opacity-60 text-white font-bold px-5 py-2.5 rounded-lg text-xs sm:text-sm transition-colors"
          >
            {loading ? 'Loading...' : 'Track Request'}
          </button>

          {traceData && (
            <button
              type="button"
              onClick={clearSearch}
              className="border border-slate/30 text-navy font-semibold px-4 py-2.5 rounded-lg text-xs sm:text-sm hover:bg-white"
            >
              Clear
            </button>
          )}
        </form>

        <div className="mt-2 text-[11px] text-slate">
          Uses the actual Community Request record and its response assignment.
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white border border-slate/20 rounded-xl p-10 text-center">
          <Activity className="w-7 h-7 text-terracotta mx-auto mb-3 animate-pulse" />
          <div className="text-sm font-semibold text-navy">
            Loading live response status...
          </div>
          <div className="text-xs text-slate mt-1">
            Reading the request and response-unit assignment.
          </div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-xs text-red-700 flex items-center gap-2">
          <XCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {traceData && !loading && (
        <div className="space-y-6">

          {/* Request Summary */}
          <div className="bg-gradient-to-r from-navy to-navy-900 text-ivory rounded-xl p-6 shadow-elevated">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">

              <div>
                <div className="text-[10px] font-semibold text-slate-light uppercase tracking-wider">
                  Community Request
                </div>

                <div className="text-2xl sm:text-3xl font-extrabold font-mono mt-1">
                  #{traceData.request.id}
                </div>

                {traceData.request.tracking_code && (
                  <div className="text-xs text-slate-light font-mono mt-1">
                    Tracking Code: {traceData.request.tracking_code}
                  </div>
                )}

                <div className="flex items-center gap-1.5 mt-4 text-xs">
                  <MapPin className="w-4 h-4 text-terracotta" />
                  <span>
                    {traceData.request.location_name || 'Location not recorded'}
                  </span>
                </div>
              </div>

              <div className="lg:text-right">
                <div className="text-[10px] uppercase tracking-wider text-slate-light">
                  Current Response Status
                </div>

                <div className="text-xl font-extrabold text-ivory mt-1">
                  {statusLabel(traceData.response.current_status)}
                </div>

                <div className="text-xs text-slate-light mt-2">
                  Request status: {statusLabel(traceData.request.status)}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-navy-700">

              <div>
                <div className="text-[10px] text-slate-light uppercase">
                  Affected People
                </div>
                <div className="font-bold mt-1">
                  {traceData.request.affected_people ?? 0}
                </div>
              </div>

              <div>
                <div className="text-[10px] text-slate-light uppercase">
                  Households
                </div>
                <div className="font-bold mt-1">
                  {traceData.request.affected_households ?? 0}
                </div>
              </div>

              <div>
                <div className="text-[10px] text-slate-light uppercase">
                  Urgency
                </div>
                <div className="font-bold mt-1">
                  {statusLabel(traceData.request.urgency)}
                </div>
              </div>

              <div>
                <div className="text-[10px] text-slate-light uppercase">
                  Priority
                </div>
                <div className="font-bold mt-1">
                  {traceData.request.priority_classification
                    ? statusLabel(traceData.request.priority_classification)
                    : traceData.request.priority_score ?? '—'}
                </div>
              </div>
            </div>
          </div>

          {/* Danger / Emergency flags */}
          {(traceData.request.immediate_danger ||
            traceData.request.medical_emergency) && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-center gap-2 text-red-700 font-bold text-sm">
                <AlertTriangle className="w-4 h-4" />
                Emergency indicators
              </div>

              <div className="flex flex-wrap gap-2 mt-3 text-xs">
                {traceData.request.immediate_danger && (
                  <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full font-semibold">
                    Immediate danger
                  </span>
                )}

                {traceData.request.medical_emergency && (
                  <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full font-semibold">
                    Medical emergency
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Response Unit */}
          <div className="bg-white border border-slate/20 rounded-xl p-6 shadow-soft">

            <div className="flex items-center gap-2 mb-5">
              <Truck className="w-5 h-5 text-terracotta" />
              <h2 className="font-bold text-base text-navy">
                Assigned Response Unit
              </h2>
            </div>

            {traceData.response_unit ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

                <div>
                  <div className="text-[10px] uppercase text-slate">
                    Unit
                  </div>
                  <div className="font-bold text-navy mt-1">
                    {traceData.response_unit.name}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase text-slate">
                    Unit Type
                  </div>
                  <div className="font-bold text-navy mt-1">
                    {traceData.response_unit.unit_type}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase text-slate">
                    Team Members
                  </div>
                  <div className="font-bold text-navy mt-1">
                    {traceData.response_unit.members ?? '—'}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase text-slate">
                    Unit Status
                  </div>
                  <div className="font-bold text-navy mt-1">
                    {statusLabel(traceData.response_unit.status)}
                  </div>
                </div>

              </div>
            ) : (
              <div className="bg-ivory rounded-lg p-4 text-sm text-slate">
                No response unit has been assigned to this request yet.
              </div>
            )}
          </div>

          {/* Real Response Timeline */}
          <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">

            <div className="flex items-center gap-2 mb-6">
              <Navigation className="w-5 h-5 text-terracotta" />
              <h2 className="font-bold text-base text-navy">
                Response Journey
              </h2>
            </div>

            <div className="relative pl-7 sm:pl-9 space-y-7">

              <div className="absolute left-3 sm:left-4 top-2 bottom-2 w-0.5 bg-slate/20" />

              {traceData.timeline.map((step, index) => {

                const completed = step.state === 'COMPLETED';
                const current = step.state === 'CURRENT';

                return (
                  <div
                    key={step.status}
                    className="relative"
                  >
                    <div
                      className={`absolute -left-7 sm:-left-9 top-0.5 w-6 h-6 rounded-full flex items-center justify-center border-2 ${
                        completed
                          ? 'bg-status-fulfilled border-white text-white'
                          : current
                            ? 'bg-terracotta border-white text-white animate-pulse'
                            : 'bg-stone-200 border-white text-slate'
                      }`}
                    >
                      {completed
                        ? <CheckCircle2 className="w-3.5 h-3.5" />
                        : current
                          ? timelineIcon(step.status)
                          : index + 1}
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">

                      <div className="font-bold text-sm text-navy flex items-center gap-2">
                        {step.label}

                        {current && (
                          <span className="text-[9px] bg-terracotta text-white px-2 py-0.5 rounded font-bold">
                            CURRENT
                          </span>
                        )}
                      </div>

                      <div className="text-[10px] text-slate font-mono">
                        {step.created_at
                          ? formatDate(step.created_at)
                          : 'Not recorded'}
                      </div>
                    </div>

                    <div className="text-xs text-slate mt-1">
                      {completed
                        ? `${step.label} has been reached.`
                        : current
                          ? `Current response stage: ${step.label}.`
                          : `Awaiting ${step.label.toLowerCase()}.`}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Field Completion */}
          {traceData.response.current_status === 'COMPLETED' && (
            <div className="bg-white border border-status-fulfilled/30 rounded-xl p-6 shadow-soft">

              <div className="flex items-center gap-2 text-status-fulfilled font-bold mb-5">
                <CheckCircle2 className="w-5 h-5" />
                <span>Response Completed</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

                <div className="bg-ivory rounded-lg p-4">
                  <div className="text-[10px] uppercase text-slate">
                    People Assisted
                  </div>
                  <div className="text-xl font-extrabold text-navy mt-1">
                    {traceData.response.people_assisted ?? 0}
                  </div>
                </div>

                <div className="bg-ivory rounded-lg p-4">
                  <div className="text-[10px] uppercase text-slate">
                    People Rescued
                  </div>
                  <div className="text-xl font-extrabold text-navy mt-1">
                    {traceData.response.people_rescued ?? 0}
                  </div>
                </div>

                <div className="bg-ivory rounded-lg p-4">
                  <div className="text-[10px] uppercase text-slate">
                    Shelter Destination
                  </div>
                  <div className="font-bold text-navy mt-1">
                    {traceData.response.shelter_destination || 'Not recorded'}
                  </div>
                </div>

              </div>

              {traceData.response.field_remarks && (
                <div className="mt-4">
                  <div className="text-[10px] uppercase text-slate mb-1">
                    Field Remarks
                  </div>

                  <div className="bg-ivory rounded-lg p-4 text-sm text-navy">
                    {traceData.response.field_remarks}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Request Details */}
          <div className="bg-white border border-slate/20 rounded-xl p-6 shadow-soft">

            <h2 className="font-bold text-base text-navy mb-5">
              Request Details
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">

              <div>
                <div className="text-slate mb-1">
                  Request Type
                </div>
                <div className="font-semibold text-navy">
                  {traceData.request.request_type || 'Not recorded'}
                </div>
              </div>

              <div>
                <div className="text-slate mb-1">
                  Submitted
                </div>
                <div className="font-semibold text-navy">
                  {formatDate(traceData.request.created_at)}
                </div>
              </div>

              <div className="sm:col-span-2">
                <div className="text-slate mb-1">
                  Description
                </div>
                <div className="font-semibold text-navy">
                  {traceData.request.raw_description || 'No description recorded.'}
                </div>
              </div>

            </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default TraceReliefPage;
