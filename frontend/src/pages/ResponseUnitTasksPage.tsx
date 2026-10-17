import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  MapPin,
  Navigation,
  Package,
  Phone,
  ShieldCheck,
  Users,
  X,
} from 'lucide-react';
import api from '../services/api';

type TaskStatus =
  | 'ASSIGNED'
  | 'ACCEPTED'
  | 'IN_TRANSIT'
  | 'ON_SCENE'
  | 'RESPONDING'
  | 'COMPLETED';

type ResponseTask = {
  assignment: {
    id: number;
    status: TaskStatus;
    assigned_at: string;
    accepted_at?: string | null;
    completed_at?: string | null;
    field_remarks?: string | null;
    people_assisted?: number;
    people_rescued?: number;
    shelter_destination?: string | null;
  };
  request: {
    id: number;
    tracking_code: string;
    reporter_name?: string | null;
    reporter_phone?: string | null;
    location_name: string;
    latitude?: number | null;
    longitude?: number | null;
    affected_people: number;
    affected_households: number;
    vulnerable_elderly: number;
    vulnerable_children: number;
    vulnerable_infants: number;
    vulnerable_pregnant: number;
    urgency: string;
    priority_score?: number | null;
    priority_classification?: string | null;
    raw_description: string;
    request_type?: string | null;
    medical_emergency?: boolean | null;
    immediate_danger?: string | null;
    danger_details_json?: string | null;
    situation_flags_json?: string | null;
    location_type?: string | null;
    rescuer_access?: string | null;
    access_problem_json?: string | null;
    accessibility_json?: string | null;
    photo_url?: string | null;
    created_at?: string | null;
    items?: Array<{
      id: number;
      category: string;
      item_name: string;
      requested_quantity: number;
      unit: string;
      fulfilled_quantity?: number;
    }>;
  };
  response_unit: {
    id: number;
    name: string;
    unit_type: string;
    location?: string | null;
    members: number;
  };
};

const STATUS_LABELS: Record<TaskStatus, string> = {
  ASSIGNED: 'Assigned',
  ACCEPTED: 'Accepted',
  IN_TRANSIT: 'In Transit',
  ON_SCENE: 'On Scene',
  RESPONDING: 'Responding',
  COMPLETED: 'Completed',
};

const NEXT_STATUS: Partial<Record<TaskStatus, TaskStatus>> = {
  ASSIGNED: 'ACCEPTED',
  ACCEPTED: 'IN_TRANSIT',
  IN_TRANSIT: 'ON_SCENE',
  ON_SCENE: 'RESPONDING',
  RESPONDING: 'COMPLETED',
};

const NEXT_BUTTON_LABELS: Partial<Record<TaskStatus, string>> = {
  ASSIGNED: 'Accept Task',
  ACCEPTED: 'Start Transit',
  IN_TRANSIT: 'Mark On Scene',
  ON_SCENE: 'Start Response',
  RESPONDING: 'Complete Task',
};

function getUrgencyClasses(urgency: string) {
  const value = urgency.toUpperCase();

  if (value === 'CRITICAL') {
    return 'bg-red-50 text-red-700 border-red-200';
  }

  if (value === 'HIGH') {
    return 'bg-orange-50 text-orange-700 border-orange-200';
  }

  if (value === 'MEDIUM') {
    return 'bg-amber-50 text-amber-700 border-amber-200';
  }

  return 'bg-slate-50 text-slate-700 border-slate-200';
}

function getStatusClasses(status: TaskStatus) {
  switch (status) {
    case 'ASSIGNED':
      return 'bg-amber-50 text-amber-700 border-amber-200';

    case 'ACCEPTED':
      return 'bg-blue-50 text-blue-700 border-blue-200';

    case 'IN_TRANSIT':
      return 'bg-indigo-50 text-indigo-700 border-indigo-200';

    case 'ON_SCENE':
      return 'bg-purple-50 text-purple-700 border-purple-200';

    case 'RESPONDING':
      return 'bg-orange-50 text-orange-700 border-orange-200';

    case 'COMPLETED':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';

    default:
      return 'bg-slate-50 text-slate-700 border-slate-200';
  }
}

function formatDate(value?: string | null) {
  if (!value) return '—';

  return new Date(value).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}
function parseJsonArray(jsonStr?: string | null): string[] {
  if (!jsonStr) return [];
  try {
    const parsed = JSON.parse(jsonStr);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}
export default function ResponseUnitTasksPage() {
  const [tasks, setTasks] = useState<ResponseTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const [completionTask, setCompletionTask] =
    useState<ResponseTask | null>(null);

  const [fieldRemarks, setFieldRemarks] = useState('');
  const [peopleAssisted, setPeopleAssisted] = useState(0);
  const [peopleRescued, setPeopleRescued] = useState(0);
  const [shelterDestination, setShelterDestination] =
    useState('');

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError('');

      const result =
        await api.getMyResponseTasks();

      setTasks(
        Array.isArray(result)
          ? result
          : []
      );
    } catch (err) {
      console.error(
        'GET RESPONSE TASKS ERROR:',
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load response tasks.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const summary = useMemo(() => {
    return {
      assigned: tasks.filter(
        (task) =>
          task.assignment.status === 'ASSIGNED'
      ).length,

      active: tasks.filter((task) =>
        [
          'ACCEPTED',
          'IN_TRANSIT',
          'ON_SCENE',
          'RESPONDING',
        ].includes(task.assignment.status)
      ).length,

      completed: tasks.filter(
        (task) =>
          task.assignment.status === 'COMPLETED'
      ).length,
    };
  }, [tasks]);

  const updateStatus = async (
    task: ResponseTask,
    nextStatus: TaskStatus,
    completionData?: {
      field_remarks: string;
      people_assisted: number;
      people_rescued: number;
      shelter_destination: string;
    }
  ) => {
    try {
      setUpdatingId(task.assignment.id);

      await api.updateResponseTaskStatus(
        task.assignment.id,
        {
          status: nextStatus,
          ...(completionData || {}),
        }
      );

      await loadTasks();
    } catch (err) {
      console.error(
        'UPDATE RESPONSE TASK ERROR:',
        err
      );

      alert(
        err instanceof Error
          ? err.message
          : 'Failed to update task status.'
      );
    } finally {
      setUpdatingId(null);
    }
  };

  const handleNextStatus = async (
    task: ResponseTask
  ) => {
    const currentStatus =
      task.assignment.status;

    const nextStatus =
      NEXT_STATUS[currentStatus];

    if (!nextStatus) return;

    if (nextStatus === 'COMPLETED') {
      setCompletionTask(task);
      setFieldRemarks('');
      setPeopleAssisted(0);
      setPeopleRescued(0);
      setShelterDestination('');
      return;
    }

    await updateStatus(
      task,
      nextStatus
    );
  };

  const handleComplete = async () => {
    if (!completionTask) return;

    await updateStatus(
      completionTask,
      'COMPLETED',
      {
        field_remarks:
          fieldRemarks.trim(),
        people_assisted:
          peopleAssisted,
        people_rescued:
          peopleRescued,
        shelter_destination:
          shelterDestination.trim(),
      }
    );

    setCompletionTask(null);
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="bg-navy text-ivory rounded-xl shadow-lg overflow-hidden">
        <div className="px-5 py-5 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-terracotta/20 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-terracotta" />
            </div>

            <div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
                RESPONSE TASKS
              </h1>

              <p className="text-xs sm:text-sm text-slate-light mt-1">
                View and manage your assigned emergency response tasks
              </p>
            </div>
          </div>

          <button
            onClick={loadTasks}
            disabled={loading}
            className="px-4 py-2.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 text-sm font-semibold transition disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh Tasks'}
          </button>
        </div>

        <div className="grid grid-cols-3 border-t border-white/10">
          <div className="px-4 py-4">
            <p className="text-xs text-slate-light">
              Assigned
            </p>
            <p className="text-2xl font-bold mt-1">
              {summary.assigned}
            </p>
          </div>

          <div className="px-4 py-4 border-l border-white/10">
            <p className="text-xs text-slate-light">
              Active
            </p>
            <p className="text-2xl font-bold mt-1">
              {summary.active}
            </p>
          </div>

          <div className="px-4 py-4 border-l border-white/10">
            <p className="text-xs text-slate-light">
              Completed
            </p>
            <p className="text-2xl font-bold mt-1">
              {summary.completed}
            </p>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center text-slate-500">
          Loading assigned tasks...
        </div>
      )}

      {/* Empty */}
      {!loading && !error && tasks.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-10 text-center">
          <div className="w-14 h-14 mx-auto rounded-full bg-slate-100 flex items-center justify-center">
            <ShieldCheck className="w-7 h-7 text-slate-400" />
          </div>

          <h2 className="mt-4 text-lg font-bold text-navy">
            No tasks assigned
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            New assignments from the Emergency Coordinator will appear here.
          </p>
        </div>
      )}

      {/* Tasks */}
      {!loading && tasks.length > 0 && (
        <div className="space-y-4">
          {tasks.map((task) => {
            const request = task.request;
            const assignment =
              task.assignment;

            const isUpdating =
              updatingId ===
              assignment.id;

            const nextStatus =
              NEXT_STATUS[
                assignment.status
              ];

            return (
              <div
                key={assignment.id}
                className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
              >
                {/* Task header */}
                <div className="px-5 py-4 border-b border-slate-200 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-navy">
                        {request.tracking_code}
                      </span>

                      <span
                        className={`px-2.5 py-1 rounded-full border text-xs font-semibold ${getStatusClasses(
                          assignment.status
                        )}`}
                      >
                        {
                          STATUS_LABELS[
                            assignment.status
                          ]
                        }
                      </span>

                      <span
                        className={`px-2.5 py-1 rounded-full border text-xs font-semibold ${getUrgencyClasses(
                          request.urgency
                        )}`}
                      >
                        {request.urgency}
                      </span>
                    </div>

                    <p className="text-xs text-slate-500 mt-1">
                      Assigned{' '}
                      {formatDate(
                        assignment.assigned_at
                      )}
                    </p>
                  </div>

                  {nextStatus && (
                    <button
                      onClick={() =>
                        handleNextStatus(
                          task
                        )
                      }
                      disabled={isUpdating}
                      className="px-4 py-2.5 rounded-lg bg-terracotta text-white text-sm font-semibold hover:opacity-90 transition disabled:opacity-50"
                    >
                      {isUpdating
                        ? 'Updating...'
                        : NEXT_BUTTON_LABELS[
                            assignment.status
                          ]}
                    </button>
                  )}
                </div>

                {/* Main content */}
                <div className="p-5">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                    {/* Location */}
                    <div className="lg:col-span-2">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
                          <MapPin className="w-5 h-5 text-terracotta" />
                        </div>

                        <div>
                          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                            Location
                          </p>

                          <p className="text-base font-semibold text-navy mt-1">
                            {request.location_name}
                          </p>

                          {request.latitude != null &&
                            request.longitude != null && (
                              <p className="text-xs text-slate-500 mt-1">
                                {request.latitude.toFixed(
                                  6
                                )}
                                ,{' '}
                                {request.longitude.toFixed(
                                  6
                                )}
                              </p>
                            )}
                        </div>
                      </div>

                      {/* Reporter Contact Info */}
                      {(request.reporter_name || request.reporter_phone) && (
                        <div className="mt-4 flex flex-wrap items-center gap-4 bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs">
                          {request.reporter_name && (
                            <div>
                              <span className="text-slate-500 font-semibold uppercase tracking-wider">Reported By: </span>
                              <span className="font-bold text-navy">{request.reporter_name}</span>
                            </div>
                          )}
                          {request.reporter_phone && (
                            <div className="flex items-center gap-1.5">
                              <Phone className="w-3.5 h-3.5 text-terracotta" />
                              <a
                                href={`tel:${request.reporter_phone}`}
                                className="font-bold text-terracotta hover:underline"
                              >
                                {request.reporter_phone}
                              </a>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Description */}
                      <div className="mt-5">
                        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                          Situation
                        </p>

                        <p className="text-sm text-slate-700 leading-relaxed mt-2">
                          {request.raw_description}
                        </p>
                      </div>
                    </div>

                    {/* People */}
                    <div className="bg-slate-50 rounded-xl p-4">
                      <div className="flex items-center gap-2">
                        <Users className="w-5 h-5 text-navy" />

                        <p className="font-semibold text-navy">
                          People Affected
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-3 mt-4">
                        <div>
                          <p className="text-xs text-slate-500">
                            People
                          </p>
                          <p className="text-lg font-bold text-navy">
                            {request.affected_people}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-slate-500">
                            Households
                          </p>
                          <p className="text-lg font-bold text-navy">
                            {request.affected_households}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Supplies Needed / Requested Items */}
                  {request.items && request.items.length > 0 && (
                    <div className="mt-5 border border-slate-200 rounded-xl overflow-hidden">
                      <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Package className="w-4 h-4 text-terracotta" />
                          <h4 className="text-xs font-bold uppercase tracking-wider text-navy">
                            Supplies Needed ({request.items.length})
                          </h4>
                        </div>
                        <span className="text-[11px] font-semibold text-slate-500">
                          {request.request_type === 'EVACUATION' ? 'Relief & Rescue Service' : 'Supply Request'}
                        </span>
                      </div>

                      <div className="divide-y divide-slate-100">
                        {request.items.map((item) => (
                          <div
                            key={item.id}
                            className="px-4 py-2.5 flex items-center justify-between text-sm"
                          >
                            <div>
                              <p className="font-semibold text-navy">
                                {item.item_name}
                              </p>
                              <p className="text-xs text-slate-500">
                                Category: {item.category}
                              </p>
                            </div>
                            <span className="px-3 py-1 rounded-full bg-terracotta/10 text-terracotta font-bold text-xs border border-terracotta/20">
                              {item.requested_quantity} {item.unit}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Vulnerable people */}
                  {(request.vulnerable_elderly > 0 ||
                    request.vulnerable_children > 0 ||
                    request.vulnerable_infants > 0 ||
                    request.vulnerable_pregnant > 0) && (
                    <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-4">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-600" />

                        <p className="font-semibold text-amber-800">
                          Vulnerable People
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-4 mt-3 text-sm text-amber-900">
                        {request.vulnerable_children >
                          0 && (
                          <span>
                            Children:{' '}
                            <strong>
                              {
                                request.vulnerable_children
                              }
                            </strong>
                          </span>
                        )}

                        {request.vulnerable_infants >
                          0 && (
                          <span>
                            Infants:{' '}
                            <strong>
                              {
                                request.vulnerable_infants
                              }
                            </strong>
                          </span>
                        )}

                        {request.vulnerable_elderly >
                          0 && (
                          <span>
                            Elderly:{' '}
                            <strong>
                              {
                                request.vulnerable_elderly
                              }
                            </strong>
                          </span>
                        )}

                        {request.vulnerable_pregnant >
                          0 && (
                          <span>
                            Pregnant:{' '}
                            <strong>
                              {
                                request.vulnerable_pregnant
                              }
                            </strong>
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  {/* Situation & Access Details */}
                  {(request.immediate_danger ||
                    parseJsonArray(request.situation_flags_json).length > 0 ||
                    parseJsonArray(request.danger_details_json).length > 0) && (
                    <div className="mt-4 bg-red-50/60 border border-red-200 rounded-xl p-4 text-xs">
                      <div className="flex items-center gap-2 text-red-800 font-semibold mb-2">
                        <AlertTriangle className="w-4 h-4 text-red-600" />
                        <span>Danger & Hazard Details</span>
                      </div>

                      {request.immediate_danger && (
                        <p className="text-red-900 mb-1.5">
                          <strong>Immediate Danger:</strong> {request.immediate_danger}
                        </p>
                      )}

                      {parseJsonArray(request.situation_flags_json).length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {parseJsonArray(request.situation_flags_json).map((flag, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded bg-red-100 text-red-800 font-medium text-[11px] border border-red-200"
                            >
                              {flag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  {/* Unit */}
                  <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4" />
                      {task.response_unit.name}
                    </span>

                    <span>
                      {task.response_unit.unit_type}
                    </span>

                    <span className="flex items-center gap-1.5">
                      <Users className="w-4 h-4" />
                      {task.response_unit.members}{' '}
                      members
                    </span>
                  </div>

                  {/* Completed info */}
                  {assignment.status ===
                    'COMPLETED' && (
                    <div className="mt-5 bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />

                        <p className="font-semibold text-emerald-800">
                          Task Completed
                        </p>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3 text-sm">
                        <div>
                          <p className="text-xs text-emerald-700">
                            People Assisted
                          </p>
                          <p className="font-bold text-emerald-900">
                            {assignment.people_assisted ||
                              0}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-emerald-700">
                            People Rescued
                          </p>
                          <p className="font-bold text-emerald-900">
                            {assignment.people_rescued ||
                              0}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-emerald-700">
                            Shelter
                          </p>
                          <p className="font-bold text-emerald-900">
                            {assignment.shelter_destination ||
                              '—'}
                          </p>
                        </div>
                      </div>

                      {assignment.field_remarks && (
                        <p className="text-sm text-emerald-900 mt-3">
                          <strong>Remarks:</strong>{' '}
                          {assignment.field_remarks}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Completion modal */}
      {completionTask && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="font-bold text-navy">
                  Complete Response Task
                </h2>

                <p className="text-xs text-slate-500 mt-1">
                  {completionTask.request.tracking_code}
                </p>
              </div>

              <button
                onClick={() =>
                  setCompletionTask(null)
                }
                className="w-9 h-9 rounded-lg hover:bg-slate-100 flex items-center justify-center"
              >
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Field Remarks
                </label>

                <textarea
                  value={fieldRemarks}
                  onChange={(e) =>
                    setFieldRemarks(
                      e.target.value
                    )
                  }
                  rows={3}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-terracotta/30"
                  placeholder="Describe the response outcome..."
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                    People Assisted
                  </label>

                  <input
                    type="number"
                    min="0"
                    value={peopleAssisted}
                    onChange={(e) =>
                      setPeopleAssisted(
                        Number(e.target.value)
                      )
                    }
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                    People Rescued
                  </label>

                  <input
                    type="number"
                    min="0"
                    value={peopleRescued}
                    onChange={(e) =>
                      setPeopleRescued(
                        Number(e.target.value)
                      )
                    }
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Shelter Destination
                </label>

                <input
                  type="text"
                  value={shelterDestination}
                  onChange={(e) =>
                    setShelterDestination(
                      e.target.value
                    )
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="Shelter name or destination"
                />
              </div>

              <button
                onClick={handleComplete}
                disabled={
                  updatingId ===
                  completionTask.assignment.id
                }
                className="w-full py-3 rounded-lg bg-terracotta text-white font-semibold hover:opacity-90 transition disabled:opacity-50"
              >
                {updatingId ===
                completionTask.assignment.id
                  ? 'Completing...'
                  : 'Complete Task'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}