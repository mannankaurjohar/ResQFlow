
import React, { useMemo, useState } from 'react';

type RequestStatus =
  | 'PENDING'
  | 'UNDER REVIEW'
  | 'APPROVED'
  | 'ASSIGNED'
  | 'ACCEPTED'
  | 'IN TRANSIT'
  | 'ON SCENE'
  | 'RESPONDING'
  | 'COMPLETED'
  | 'REJECTED';

type RequestType = 'EVACUATION' | 'SUPPLIES';

interface ResponseRequest {
  id: number;
  trackingCode: string;
  location: string;
  requestType: RequestType;
  affectedPeople: number;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: RequestStatus;
  description: string;
  assignedUnit?: string;
}

interface ResponseUnit {
  id: number;
  name: string;
  type: string;
  operator: string;
  members: number;
  status: 'AVAILABLE' | 'ASSIGNED' | 'BUSY';
}

const initialRequests: ResponseRequest[] = [
  {
    id: 1,
    trackingCode: 'RQ-1042',
    location: 'Panchavati, Nashik',
    requestType: 'EVACUATION',
    affectedPeople: 8,
    priority: 'CRITICAL',
    status: 'PENDING',
    description:
      'Flood water has entered the residential area. Elderly residents require evacuation.'
  },
  {
    id: 2,
    trackingCode: 'RQ-1043',
    location: 'Gangapur Road, Nashik',
    requestType: 'SUPPLIES',
    affectedPeople: 15,
    priority: 'HIGH',
    status: 'APPROVED',
    description:
      'Residents require drinking water and emergency food supplies.'
  },
  {
    id: 3,
    trackingCode: 'RQ-1044',
    location: 'Nashik Road',
    requestType: 'EVACUATION',
    affectedPeople: 5,
    priority: 'HIGH',
    status: 'ASSIGNED',
    description:
      'Five people are stranded inside a flooded residential building.',
    assignedUnit: 'Fire & Rescue Unit 01'
  },
  {
    id: 4,
    trackingCode: 'RQ-1045',
    location: 'Deolali Camp, Nashik',
    requestType: 'SUPPLIES',
    affectedPeople: 22,
    priority: 'MEDIUM',
    status: 'PENDING',
    description:
      'Relief supplies including drinking water and food packets are required.'
  }
];

const responseUnits: ResponseUnit[] = [
  {
    id: 1,
    name: 'Fire & Rescue Unit 01',
    type: 'Fire & Rescue',
    operator: 'Response Operator',
    members: 6,
    status: 'AVAILABLE'
  },
  {
    id: 2,
    name: 'SDRF Unit 02',
    type: 'SDRF',
    operator: 'Response Operator',
    members: 8,
    status: 'AVAILABLE'
  },
  {
    id: 3,
    name: 'NDRF Unit 01',
    type: 'NDRF',
    operator: 'Response Operator',
    members: 10,
    status: 'BUSY'
  },
  {
    id: 4,
    name: 'Police Emergency Unit 01',
    type: 'Police / Emergency',
    operator: 'Response Operator',
    members: 5,
    status: 'AVAILABLE'
  }
];

const priorityStyles: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700 border-red-200',
  HIGH: 'bg-orange-100 text-orange-700 border-orange-200',
  MEDIUM: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  LOW: 'bg-green-100 text-green-700 border-green-200'
};

const statusStyles: Record<string, string> = {
  PENDING: 'bg-slate-100 text-slate-700',
  'UNDER REVIEW': 'bg-blue-100 text-blue-700',
  APPROVED: 'bg-indigo-100 text-indigo-700',
  ASSIGNED: 'bg-purple-100 text-purple-700',
  ACCEPTED: 'bg-cyan-100 text-cyan-700',
  'IN TRANSIT': 'bg-blue-100 text-blue-700',
  'ON SCENE': 'bg-amber-100 text-amber-700',
  RESPONDING: 'bg-orange-100 text-orange-700',
  COMPLETED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700'
};

const statusLabel = (status: RequestStatus) => {
  return status.replace('_', ' ');
};

export default function ResponseAssignmentPage() {
  const [requests, setRequests] =
    useState<ResponseRequest[]>(initialRequests);

  const [selectedRequest, setSelectedRequest] =
    useState<ResponseRequest | null>(null);

  const [selectedUnitId, setSelectedUnitId] =
    useState<number | null>(null);

  const [search, setSearch] = useState('');

  const [filter, setFilter] =
    useState<'ALL' | 'PENDING' | 'APPROVED' | 'ACTIVE' | 'COMPLETED'>(
      'ALL'
    );

  const [showDetails, setShowDetails] = useState(false);

  const [notification, setNotification] =
    useState<string | null>(null);

  const showNotification = (message: string) => {
    setNotification(message);

    setTimeout(() => {
      setNotification(null);
    }, 3000);
  };

  const filteredRequests = useMemo(() => {
    let result = [...requests];

    if (filter === 'PENDING') {
      result = result.filter(
        (request) => request.status === 'PENDING'
      );
    }

    if (filter === 'APPROVED') {
      result = result.filter(
        (request) => request.status === 'APPROVED'
      );
    }

    if (filter === 'ACTIVE') {
      result = result.filter((request) =>
        [
          'ASSIGNED',
          'ACCEPTED',
          'IN TRANSIT',
          'ON SCENE',
          'RESPONDING'
        ].includes(request.status)
      );
    }

    if (filter === 'COMPLETED') {
      result = result.filter(
        (request) => request.status === 'COMPLETED'
      );
    }

    if (search.trim()) {
      const query = search.toLowerCase();

      result = result.filter(
        (request) =>
          request.trackingCode
            .toLowerCase()
            .includes(query) ||
          request.location
            .toLowerCase()
            .includes(query) ||
          request.requestType
            .toLowerCase()
            .includes(query)
      );
    }

    return result;
  }, [requests, filter, search]);

  const availableUnits = responseUnits.filter(
    (unit) => unit.status === 'AVAILABLE'
  );

  const handleReview = (request: ResponseRequest) => {
    setSelectedRequest({
      ...request,
      status:
        request.status === 'PENDING'
          ? 'UNDER REVIEW'
          : request.status
    });

    setSelectedUnitId(null);
    setShowDetails(true);
  };

  const handleApprove = () => {
    if (!selectedRequest) return;

    setRequests((current) =>
      current.map((request) =>
        request.id === selectedRequest.id
          ? {
              ...request,
              status: 'APPROVED'
            }
          : request
      )
    );

    setSelectedRequest({
      ...selectedRequest,
      status: 'APPROVED'
    });

    showNotification(
      `${selectedRequest.trackingCode} approved for response assignment.`
    );
  };

  const handleReject = () => {
    if (!selectedRequest) return;

    setRequests((current) =>
      current.map((request) =>
        request.id === selectedRequest.id
          ? {
              ...request,
              status: 'REJECTED'
            }
          : request
      )
    );

    setSelectedRequest({
      ...selectedRequest,
      status: 'REJECTED'
    });

    showNotification(
      `${selectedRequest.trackingCode} has been rejected.`
    );
  };

  const handleAssign = () => {
    if (!selectedRequest || !selectedUnitId) {
      showNotification('Select an available response unit first.');
      return;
    }

    const unit = responseUnits.find(
      (item) => item.id === selectedUnitId
    );

    if (!unit) return;

    setRequests((current) =>
      current.map((request) =>
        request.id === selectedRequest.id
          ? {
              ...request,
              status: 'ASSIGNED',
              assignedUnit: unit.name
            }
          : request
      )
    );

    setSelectedRequest({
      ...selectedRequest,
      status: 'ASSIGNED',
      assignedUnit: unit.name
    });

    setSelectedUnitId(null);

    showNotification(
      `${unit.name} assigned to ${selectedRequest.trackingCode}.`
    );
  };

  const closeDetails = () => {
    setShowDetails(false);
    setSelectedRequest(null);
    setSelectedUnitId(null);
  };

  const pendingCount = requests.filter(
    (request) => request.status === 'PENDING'
  ).length;

  const approvedCount = requests.filter(
    (request) => request.status === 'APPROVED'
  ).length;

  const activeCount = requests.filter((request) =>
    [
      'ASSIGNED',
      'ACCEPTED',
      'IN TRANSIT',
      'ON SCENE',
      'RESPONDING'
    ].includes(request.status)
  ).length;

  const completedCount = requests.filter(
    (request) => request.status === 'COMPLETED'
  ).length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Notification */}
      {notification && (
        <div className="fixed right-6 top-6 z-[100] rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white shadow-xl">
          {notification}
        </div>
      )}

      <div className="mx-auto max-w-[1500px] px-6 py-7">
        {/* Header */}
        <div className="mb-7 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-500">
              <span>Operations</span>
              <span>/</span>
              <span className="text-slate-900">
                Response Assignment
              </span>
            </div>

            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Response Assignment
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Review approved incidents, assign available response
              units, and monitor active field responses.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Available Units
              </div>

              <div className="mt-1 text-xl font-bold text-green-600">
                {availableUnits.length}
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Active Responses
              </div>

              <div className="mt-1 text-xl font-bold text-blue-600">
                {activeCount}
              </div>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="mb-7 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <button
            onClick={() => setFilter('PENDING')}
            className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">
                Awaiting Review
              </span>

              <span className="rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                PENDING
              </span>
            </div>

            <div className="mt-3 text-3xl font-bold text-slate-900">
              {pendingCount}
            </div>
          </button>

          <button
            onClick={() => setFilter('APPROVED')}
            className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">
                Awaiting Assignment
              </span>

              <span className="rounded-lg bg-indigo-50 px-2 py-1 text-xs font-semibold text-indigo-600">
                APPROVED
              </span>
            </div>

            <div className="mt-3 text-3xl font-bold text-indigo-600">
              {approvedCount}
            </div>
          </button>

          <button
            onClick={() => setFilter('ACTIVE')}
            className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">
                Active Responses
              </span>

              <span className="rounded-lg bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-600">
                ACTIVE
              </span>
            </div>

            <div className="mt-3 text-3xl font-bold text-blue-600">
              {activeCount}
            </div>
          </button>

          <button
            onClick={() => setFilter('COMPLETED')}
            className="rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">
                Completed
              </span>

              <span className="rounded-lg bg-green-50 px-2 py-1 text-xs font-semibold text-green-600">
                DONE
              </span>
            </div>

            <div className="mt-3 text-3xl font-bold text-green-600">
              {completedCount}
            </div>
          </button>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
          {/* Request Queue */}
          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            {/* Toolbar */}
            <div className="border-b border-slate-200 px-5 py-4">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <h2 className="font-semibold text-slate-900">
                    Response Queue
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Incidents requiring coordinator action.
                  </p>
                </div>

                <div className="flex flex-col gap-3 sm:flex-row">
                  <div className="relative">
                    <input
                      type="text"
                      value={search}
                      onChange={(e) =>
                        setSearch(e.target.value)
                      }
                      placeholder="Search request..."
                      className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm outline-none transition focus:border-blue-400 focus:bg-white sm:w-64"
                    />
                  </div>

                  <select
                    value={filter}
                    onChange={(e) =>
                      setFilter(
                        e.target.value as
                          | 'ALL'
                          | 'PENDING'
                          | 'APPROVED'
                          | 'ACTIVE'
                          | 'COMPLETED'
                      )
                    }
                    className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium outline-none"
                  >
                    <option value="ALL">
                      All Requests
                    </option>
                    <option value="PENDING">
                      Awaiting Review
                    </option>
                    <option value="APPROVED">
                      Awaiting Assignment
                    </option>
                    <option value="ACTIVE">
                      Active Responses
                    </option>
                    <option value="COMPLETED">
                      Completed
                    </option>
                  </select>
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full min-w-[850px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/70">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Incident
                    </th>

                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Type
                    </th>

                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Affected
                    </th>

                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Priority
                    </th>

                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Status
                    </th>

                    <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-400">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {filteredRequests.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-5 py-14 text-center"
                      >
                        <div className="text-sm font-medium text-slate-600">
                          No requests found
                        </div>

                        <div className="mt-1 text-xs text-slate-400">
                          Try changing the filter or search term.
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredRequests.map((request) => (
                      <tr
                        key={request.id}
                        className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50/60"
                      >
                        <td className="px-5 py-4">
                          <div className="font-semibold text-slate-900">
                            {request.trackingCode}
                          </div>

                          <div className="mt-1 text-xs text-slate-500">
                            {request.location}
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <span className="text-sm font-medium text-slate-700">
                            {request.requestType}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <span className="text-sm font-semibold text-slate-800">
                            {request.affectedPeople}
                          </span>

                          <span className="ml-1 text-xs text-slate-400">
                            people
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex rounded-lg border px-2.5 py-1 text-xs font-bold ${priorityStyles[request.priority]}`}
                          >
                            {request.priority}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex rounded-lg px-2.5 py-1 text-xs font-semibold ${statusStyles[request.status]}`}
                          >
                            {statusLabel(request.status)}
                          </span>

                          {request.assignedUnit && (
                            <div className="mt-1 text-xs text-slate-400">
                              {request.assignedUnit}
                            </div>
                          )}
                        </td>

                        <td className="px-5 py-4 text-right">
                          <button
                            onClick={() =>
                              handleReview(request)
                            }
                            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
                          >
                            {request.status === 'PENDING'
                              ? 'Review'
                              : request.status === 'APPROVED'
                              ? 'Assign Team'
                              : 'View'}
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Active Response Panel */}
          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-5 py-4">
              <h2 className="font-semibold text-slate-900">
                Active Responses
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Current field operations.
              </p>
            </div>

            <div className="divide-y divide-slate-100">
              {requests
                .filter((request) =>
                  [
                    'ASSIGNED',
                    'ACCEPTED',
                    'IN TRANSIT',
                    'ON SCENE',
                    'RESPONDING'
                  ].includes(request.status)
                )
                .map((request) => (
                  <button
                    key={request.id}
                    onClick={() =>
                      handleReview(request)
                    }
                    className="w-full px-5 py-4 text-left transition hover:bg-slate-50"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-sm font-semibold text-slate-900">
                          {request.trackingCode}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                          {request.location}
                        </div>
                      </div>

                      <span
                        className={`rounded-lg px-2 py-1 text-[10px] font-bold ${statusStyles[request.status]}`}
                      >
                        {statusLabel(request.status)}
                      </span>
                    </div>

                    {request.assignedUnit && (
                      <div className="mt-3 rounded-lg bg-slate-50 px-3 py-2">
                        <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                          Assigned Unit
                        </div>

                        <div className="mt-1 text-xs font-semibold text-slate-700">
                          {request.assignedUnit}
                        </div>
                      </div>
                    )}
                  </button>
                ))}

              {activeCount === 0 && (
                <div className="px-5 py-12 text-center">
                  <div className="text-sm font-medium text-slate-600">
                    No active responses
                  </div>

                  <div className="mt-1 text-xs text-slate-400">
                    Assigned field operations will appear here.
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>

      {/* Details / Assignment Modal */}
      {showDetails && selectedRequest && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-slate-200 px-6 py-5">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-bold text-slate-900">
                    {selectedRequest.trackingCode}
                  </h2>

                  <span
                    className={`rounded-lg border px-2.5 py-1 text-xs font-bold ${priorityStyles[selectedRequest.priority]}`}
                  >
                    {selectedRequest.priority}
                  </span>
                </div>

                <p className="mt-1 text-sm text-slate-500">
                  {selectedRequest.location}
                </p>
              </div>

              <button
                onClick={closeDetails}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            {/* Request Information */}
            <div className="grid gap-4 px-6 py-5 sm:grid-cols-3">
              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Request Type
                </div>

                <div className="mt-1 text-sm font-semibold text-slate-800">
                  {selectedRequest.requestType}
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Affected People
                </div>

                <div className="mt-1 text-sm font-semibold text-slate-800">
                  {selectedRequest.affectedPeople}
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Current Status
                </div>

                <div className="mt-1">
                  <span
                    className={`inline-flex rounded-lg px-2 py-1 text-xs font-semibold ${statusStyles[selectedRequest.status]}`}
                  >
                    {statusLabel(selectedRequest.status)}
                  </span>
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="px-6 pb-5">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Incident Description
              </div>

              <div className="mt-2 rounded-xl border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700">
                {selectedRequest.description}
              </div>
            </div>

            {/* Approval Actions */}
            {selectedRequest.status === 'UNDER REVIEW' && (
              <div className="mx-6 mb-5 rounded-xl border border-blue-100 bg-blue-50 p-4">
                <div className="text-sm font-semibold text-blue-900">
                  Coordinator Review
                </div>

                <p className="mt-1 text-xs leading-5 text-blue-700">
                  Review the incident details before approving it
                  for response assignment.
                </p>

                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleApprove}
                    className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
                  >
                    Approve Request
                  </button>

                  <button
                    onClick={handleReject}
                    className="rounded-lg border border-red-200 bg-white px-4 py-2.5 text-sm font-semibold text-red-600 transition hover:bg-red-50"
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}

            {/* Assignment Section */}
            {selectedRequest.status === 'APPROVED' && (
              <div className="mx-6 mb-6 rounded-xl border border-indigo-100 bg-indigo-50/60 p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-indigo-900">
                      Assign Response Unit
                    </div>

                    <p className="mt-1 text-xs text-indigo-700">
                      Only currently available units can be assigned.
                    </p>
                  </div>

                  <span className="rounded-lg bg-green-100 px-2.5 py-1 text-xs font-bold text-green-700">
                    {availableUnits.length} AVAILABLE
                  </span>
                </div>

                {availableUnits.length === 0 ? (
                  <div className="mt-4 rounded-xl border border-orange-200 bg-orange-50 p-4 text-sm text-orange-700">
                    No response units are currently available.
                    The request will remain approved until a unit
                    becomes available.
                  </div>
                ) : (
                  <div className="mt-4 space-y-3">
                    {availableUnits.map((unit) => (
                      <button
                        key={unit.id}
                        onClick={() =>
                          setSelectedUnitId(unit.id)
                        }
                        className={`w-full rounded-xl border p-4 text-left transition ${
                          selectedUnitId === unit.id
                            ? 'border-indigo-500 bg-white ring-2 ring-indigo-100'
                            : 'border-slate-200 bg-white hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-semibold text-slate-900">
                              {unit.name}
                            </div>

                            <div className="mt-1 text-xs text-slate-500">
                              {unit.type} · {unit.members}{' '}
                              members
                            </div>
                          </div>

                          <span className="rounded-lg bg-green-100 px-2 py-1 text-[10px] font-bold text-green-700">
                            AVAILABLE
                          </span>
                        </div>

                        <div className="mt-3 text-xs text-slate-500">
                          Operator:{' '}
                          <span className="font-medium text-slate-700">
                            {unit.operator}
                          </span>
                        </div>
                      </button>
                    ))}

                    <button
                      onClick={handleAssign}
                      disabled={!selectedUnitId}
                      className="mt-2 w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                    >
                      Assign Selected Unit
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Assigned Information */}
            {selectedRequest.status === 'ASSIGNED' &&
              selectedRequest.assignedUnit && (
                <div className="mx-6 mb-6 rounded-xl border border-purple-100 bg-purple-50 p-5">
                  <div className="text-sm font-semibold text-purple-900">
                    Response Unit Assigned
                  </div>

                  <div className="mt-3 rounded-xl bg-white p-4">
                    <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Assigned Team
                    </div>

                    <div className="mt-1 text-sm font-bold text-slate-900">
                      {selectedRequest.assignedUnit}
                    </div>

                    <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
                      <span className="h-2 w-2 rounded-full bg-amber-400" />
                      Awaiting operator acceptance
                    </div>
                  </div>
                </div>
              )}

            {/* Active Response */}
            {[
              'ACCEPTED',
              'IN TRANSIT',
              'ON SCENE',
              'RESPONDING'
            ].includes(selectedRequest.status) && (
              <div className="mx-6 mb-6 rounded-xl border border-blue-100 bg-blue-50 p-5">
                <div className="text-sm font-semibold text-blue-900">
                  Active Field Response
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-500">
                      Response progress
                    </span>

                    <span className="text-xs font-bold text-blue-700">
                      {statusLabel(selectedRequest.status)}
                    </span>
                  </div>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className="h-full rounded-full bg-blue-600"
                      style={{
                        width:
                          selectedRequest.status === 'ACCEPTED'
                            ? '25%'
                            : selectedRequest.status ===
                              'IN TRANSIT'
                            ? '50%'
                            : selectedRequest.status ===
                              'ON SCENE'
                            ? '75%'
                            : '90%'
                      }}
                    />
                  </div>
                </div>

                {selectedRequest.assignedUnit && (
                  <div className="mt-4 text-xs text-slate-600">
                    Assigned unit:{' '}
                    <span className="font-semibold text-slate-800">
                      {selectedRequest.assignedUnit}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Footer */}
            <div className="flex justify-end border-t border-slate-200 px-6 py-4">
              <button
                onClick={closeDetails}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
