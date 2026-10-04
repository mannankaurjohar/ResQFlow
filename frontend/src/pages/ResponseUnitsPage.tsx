import React, { useEffect, useState } from 'react';
import {
  Plus,
  Users,
  MapPin,
 
  ShieldCheck,
  X,
  CheckCircle2,
} from 'lucide-react';
import type { User } from '../types';
import api from '../services/api';
type UnitStatus = 'AVAILABLE' | 'ASSIGNED' | 'BUSY';

type ApprovedRequest = {
  id: number;
  tracking_code?: string;
  location?: string;
  affected_people?: number;
  priority_classification?: string;
  priority_score?: number;
  status?: string;
};

type ResponseUnit = {
  id: number;
  name: string;
  type: string;
  location: string;
  members: number;
  operator: string;
  
  status: UnitStatus;
};

const UNIT_TYPES = [
  'Fire & Rescue',
  'Police / Emergency',
  'SDRF',
  'NDRF',
  'Aapda Mitra / Authorized Local Team',
  'Other Authorized Unit',
];
const UNIT_TYPE_ORGANIZATION_MAP: Record<string, number> = {
  NDRF: 1,
  SDRF: 2,
  'Fire & Rescue': 3,
  'Police / Emergency': 4,
  'Aapda Mitra / Authorized Local Team': 5,
  'Other Authorized Unit': 6,
};
const UNIT_OPERATOR_TYPES: Record<string, string[]> = {
  'Fire & Rescue': ['FIRE'],
  'Police / Emergency': ['POLICE'],
  'SDRF': ['SDRF'],
  'NDRF': ['NDRF'],
  'Aapda Mitra / Authorized Local Team': ['LOCAL'],
  'Other Authorized Unit': ['OTHER'],
};
const RESPONSE_UNITS_STORAGE_KEY = 'resqflow_response_units';

const ResponseUnitsPage: React.FC = () => {
  const [units, setUnits] = useState<ResponseUnit[]>(() => {
    try {
      const saved = localStorage.getItem(RESPONSE_UNITS_STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [approvedRequests, setApprovedRequests] = useState<ApprovedRequest[]>([]);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState<ResponseUnit | null>(null);
  const [selectedRequestId, setSelectedRequestId] = useState('');
  const [requestsLoading, setRequestsLoading] = useState(false);

  const [showCreateForm, setShowCreateForm] = useState(false);

  const [name, setName] = useState('');
  const [type, setType] = useState('');
  const [location, setLocation] = useState('');
  const [members, setMembers] = useState('');
  const [operatorId, setOperatorId] = useState('');
  const [operator, setOperator] = useState('');
  
  
const [operators, setOperators] = useState<User[]>([]);

useEffect(() => {
  localStorage.setItem(
    RESPONSE_UNITS_STORAGE_KEY,
    JSON.stringify(units)
  );
}, [units]);
  const resetForm = () => {
    setName('');
    setType('');
    setLocation('');
    setMembers('');
    setOperatorId('');
    setOperator('');
    
  };
useEffect(() => {
  const loadOperators = async () => {
    try {
      const workers = await api.getWorkers();

      const responseOperators = workers.filter(
        (user) =>
          String(user.role).toUpperCase() ===
          'RESPONSE_UNIT_OPERATOR'
      );

      setOperators(responseOperators);
    } catch (error) {
      console.error('GET WORKERS ERROR:', error);
    }
  };

  loadOperators();
}, []);


const loadApprovedRequests = async () => {
  try {
    setRequestsLoading(true);

    const requests = await api.getRequests({ exclude_assigned: true });

    const approved = (Array.isArray(requests) ? requests : []).filter(
      (request: any) => {
        const status = String(request.status || '').toUpperCase();

        return (
          (status === 'APPROVED' || status === 'ALLOCATED') &&
          !request.response_assignment_id &&
          !request.response_unit_id &&
          !request.assigned_unit_id &&
          !request.assignment_id
        );
      }
    );

    setApprovedRequests(approved);
  } catch (error) {
    console.error('GET APPROVED REQUESTS ERROR:', error);
    setApprovedRequests([]);
  } finally {
    setRequestsLoading(false);
  }
};
const openAssignModal = async (unit: ResponseUnit) => {
  setSelectedUnit(unit);
  setSelectedRequestId('');
  setShowAssignModal(true);
  await loadApprovedRequests();
};

const closeAssignModal = () => {
  setShowAssignModal(false);
  setSelectedUnit(null);
  setSelectedRequestId('');
};

const handleAssignTeam = async () => {
  if (!selectedUnit || !selectedRequestId) {
    alert('Please select an approved request.');
    return;
  }

  const selectedRequest = approvedRequests.find(
    (request) =>
      String(request.id) === selectedRequestId
  );

  try {
    await api.assignResponseTask(
      selectedUnit.id,
      Number(selectedRequestId)
    );

    setUnits((current) =>
      current.map((unit) =>
        unit.id === selectedUnit.id
          ? {
              ...unit,
              status: 'ASSIGNED',
            }
          : unit
      )
    );

    closeAssignModal();

    alert(
      `Team ${selectedUnit.name} assigned to ${
        selectedRequest?.tracking_code ||
        `Request #${selectedRequestId}`
      }.`
    );
  } catch (error) {
    console.error(
      'ASSIGN RESPONSE TASK ERROR:',
      error
    );

    alert(
      error instanceof Error
        ? error.message
        : 'Failed to assign response task.'
    );
  }
};

const filteredOperators = type
  ? operators.filter((user) => {
      const selectedType = String(type).trim().toUpperCase();

      const userUnitType = String(
        user.unit_type || ''
      ).trim().toUpperCase();

      // Match unit_type if available
      if (userUnitType === selectedType) {
        return true;
      }

      // Otherwise match organization
      const organizationId =
        UNIT_TYPE_ORGANIZATION_MAP[type];

      return (
        organizationId !== undefined &&
        Number(user.organization_id) === organizationId
      );
    })
  : [];
    
   
  const handleCreateUnit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !name.trim() ||
      !type ||
      !location.trim() ||
      !members ||
      !operatorId
    ) {
      alert('Please fill in all required fields.');
      return;
    }

    try {
      const createdUnit = await api.createResponseUnit({
        name: name.trim(),
        unit_type: type,
        location: location.trim(),
        members: Number(members),
        operator_id: Number(operatorId),
      });

      const newUnit: ResponseUnit = {
        id: createdUnit.id,
        name: createdUnit.name,
        type: createdUnit.unit_type,
        location: createdUnit.location || '',
        members: createdUnit.members,
        operator: String(createdUnit.operator_id),
        status: createdUnit.status,
      };

      setUnits((current) => [...current, newUnit]);

      resetForm();
      setShowCreateForm(false);

      alert(`Response team "${createdUnit.name}" created successfully.`);
    } catch (error) {
      console.error('CREATE RESPONSE UNIT ERROR:', error);

      alert(
        error instanceof Error
          ? error.message
          : 'Failed to create response team.'
      );
    }
  };
  const getStatusStyle = (status: UnitStatus) => {
    if (status === 'AVAILABLE') {
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }

    if (status === 'BUSY') {
      return 'bg-amber-50 text-amber-700 border-amber-200';
    }

    return 'bg-blue-50 text-blue-700 border-blue-200';
  };

  return (
    <div className="max-w-[1500px] mx-auto px-3 sm:px-5 py-4">

      {/* HEADER */}
      <div className="bg-navy text-ivory rounded-xl shadow-lg overflow-hidden">

        <div className="px-5 py-5 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">

          <div className="flex items-center gap-3">

            <div className="w-12 h-12 rounded-xl bg-terracotta/20 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-terracotta" />
            </div>

            <div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
                RESPONSE UNITS
              </h1>

              <p className="text-xs sm:text-sm text-slate-light mt-1">
                Manage and deploy authorized emergency response teams
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={() => setShowCreateForm(true)}
            className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-terracotta hover:bg-terracotta/90 text-white text-sm font-bold transition"
          >
            <Plus className="w-4 h-4" />
            Create Response Unit
          </button>

        </div>

        {/* SUMMARY */}
        <div className="grid grid-cols-2 sm:grid-cols-3 border-t border-white/10">

          <div className="px-5 py-4 border-r border-white/10">
            <p className="text-[9px] uppercase tracking-wider text-slate-light">
              Total Units
            </p>

            <p className="text-2xl font-bold mt-1">
              {units.length}
            </p>
          </div>

          <div className="px-5 py-4 border-r border-white/10">
            <p className="text-[9px] uppercase tracking-wider text-slate-light">
              Available
            </p>

            <p className="text-2xl font-bold mt-1 text-emerald-300">
              {units.filter((unit) => unit.status === 'AVAILABLE').length}
            </p>
          </div>

          <div className="px-5 py-4 hidden sm:block">
            <p className="text-[9px] uppercase tracking-wider text-slate-light">
              Busy
            </p>

            <p className="text-2xl font-bold mt-1 text-amber-300">
              {units.filter(
  (unit) => unit.status === 'ASSIGNED' || unit.status === 'BUSY'
).length}
            </p>
          </div>

        </div>

      </div>

      {/* CREATE FORM */}
      {showCreateForm && (
        <div className="mt-5 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

          <div className="px-5 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">

            <div>
              <h2 className="text-base font-bold text-navy">
                Create Response Unit
              </h2>

              <p className="text-xs text-slate-500 mt-1">
                New units are automatically marked as available.
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                resetForm();
                setShowCreateForm(false);
              }}
              className="p-2 rounded-lg hover:bg-slate-200 transition"
            >
              <X className="w-5 h-5 text-slate-600" />
            </button>

          </div>

          <form
            onSubmit={handleCreateUnit}
            className="p-5 space-y-5"
          >

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* UNIT NAME */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Unit Name *
                </label>

                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Nashik Rescue Unit 01"
                  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
                />
              </div>

              {/* UNIT TYPE */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Unit Type *
                </label>

                <select
                  value={type}
                  onChange={(e) => {
  setType(e.target.value);

  setOperatorId('');
  setOperator('');

}}
                  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta bg-white"
                >
                  <option value="">Select unit type</option>

                  {UNIT_TYPES.map((unitType) => (
                    <option key={unitType} value={unitType}>
                      {unitType}
                    </option>
                  ))}
                </select>
              </div>

              {/* LOCATION */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Base Location *
                </label>

                <div className="relative">
                  <MapPin className="absolute left-3 top-3 w-4 h-4 text-slate-400" />

                  <input
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Nashik Fire Station"
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
                  />
                </div>
              </div>

              {/* TEAM SIZE */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Team Size *
                </label>

                <div className="relative">
                  <Users className="absolute left-3 top-3 w-4 h-4 text-slate-400" />

                  <input
                    type="number"
                    min="1"
                    value={members}
                    onChange={(e) => setMembers(e.target.value)}
                    placeholder="Number of members"
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
                  />
                </div>
              </div>

              {/* OPERATOR */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Response Unit Operator *
                </label>

               <select
  value={operatorId}
  onChange={(e) => {
    const selected = operators.find(
      (user) => String(user.id) === e.target.value
    );

    setOperatorId(e.target.value);
    setOperator(selected?.full_name || '');
 
  }}
  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
>
  <option value="">Select response unit operator</option>

{filteredOperators.map((user) => (
    <option key={user.id} value={user.id}>
      {user.full_name}
    </option>
  ))}
</select>
              </div>

              
         

            </div>

            {/* STATUS NOTE */}
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 flex items-start gap-3">

              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />

              <div>
                <p className="text-sm font-bold text-emerald-800">
                  Availability is automatic
                </p>

                <p className="text-xs text-emerald-700 mt-0.5">
                  This unit will start as AVAILABLE. Assignment and completion
                  will automatically update its operational status.
                </p>
              </div>

            </div>

            {/* ACTIONS */}
            <div className="flex flex-col sm:flex-row justify-end gap-3 pt-2">

              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setShowCreateForm(false);
                }}
                className="px-5 py-2.5 rounded-lg border border-slate-200 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                Cancel
              </button>

              <button
                type="submit"
                className="px-5 py-2.5 rounded-lg bg-terracotta hover:bg-terracotta/90 text-white text-sm font-bold transition"
              >
                Create Response Unit
              </button>

            </div>

          </form>
        </div>
      )}

      {/* UNIT LIST */}
      <div className="mt-5 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="text-base font-bold text-navy">
            Registered Response Units
          </h2>

          <p className="text-xs text-slate-500 mt-1">
            Only available units can be assigned to active incidents.
          </p>
        </div>

        {units.length === 0 ? (

          <div className="px-5 py-16 text-center">

            <div className="w-14 h-14 mx-auto rounded-full bg-slate-100 flex items-center justify-center">
              <ShieldCheck className="w-7 h-7 text-slate-400" />
            </div>

            <h3 className="mt-4 text-sm font-bold text-navy">
              No response units registered
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Create a response unit to make it available for emergency deployment.
            </p>

            <button
              type="button"
              onClick={() => setShowCreateForm(true)}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-terracotta text-white text-xs font-bold hover:bg-terracotta/90 transition"
            >
              <Plus className="w-4 h-4" />
              Create Response Unit
            </button>

          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full text-sm">

              <thead className="bg-slate-50 border-b border-slate-200">

                <tr>
                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Unit
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Type
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Location
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Members
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Operator
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Status
                  </th>

                  <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wide text-slate-500">
                    Action
                  </th>
                </tr>

              </thead>

              <tbody>

                {units.map((unit) => (

                  <tr
                    key={unit.id}
                    className="border-b border-slate-100 hover:bg-slate-50"
                  >

                    <td className="px-4 py-4">
                      <div className="font-bold text-navy">
                        {unit.name}
                      </div>

                     
                    </td>

                    <td className="px-4 py-4 text-slate-700">
                      {unit.type}
                    </td>

                    <td className="px-4 py-4">
                      <div className="flex items-center gap-1.5 text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {unit.location}
                      </div>
                    </td>

                    <td className="px-4 py-4">
                      <div className="flex items-center gap-1.5">
                        <Users className="w-3.5 h-3.5 text-slate-400" />
                        {unit.members}
                      </div>
                    </td>

                    <td className="px-4 py-4">
                      <div className="font-medium text-slate-700">
                        {unit.operator}
                      </div>

                      <div className="text-[11px] text-slate-500 mt-1">
                       
                      </div>
                    </td>

                    <td className="px-4 py-4">

                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold ${getStatusStyle(unit.status)}`}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current" />
                        {unit.status}
                      </span>

                    </td>

                    <td className="px-4 py-4">
                      {unit.status === 'AVAILABLE' ? (
                        <button
                          type="button"
                          onClick={() => openAssignModal(unit)}
                          className="px-3 py-1.5 rounded-md bg-terracotta hover:bg-terracotta/90 text-white text-xs font-semibold transition"
                        >
                          Assign Team
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400">
                          Not available
                        </span>
                      )}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

      {showAssignModal && selectedUnit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/50 backdrop-blur-sm px-4">
          <div className="w-full max-w-lg bg-ivory rounded-xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-navy">Assign Response Team</h2>
                <p className="text-xs text-slate-500 mt-1">Select one approved request for this available team.</p>
              </div>
              <button type="button" onClick={closeAssignModal} className="p-2 rounded-lg hover:bg-slate-100 transition">
                <X className="w-5 h-5 text-slate-600" />
              </button>
            </div>

            <div className="p-5 space-y-4">
              <div className="bg-white border border-slate-200 rounded-lg p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Response Team</p>
                <p className="text-sm font-bold text-navy mt-1">{selectedUnit.name}</p>
                <p className="text-xs text-slate-500 mt-1">{selectedUnit.type} â€¢ {selectedUnit.members} members â€¢ {selectedUnit.operator}</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Approved Request *</label>
                {requestsLoading ? (
                  <div className="rounded-lg border border-slate-200 bg-white px-3 py-3 text-xs text-slate-500">Loading approved requests...</div>
                ) : approvedRequests.length === 0 ? (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-3 text-xs text-amber-800">No approved requests are currently available for assignment.</div>
                ) : (
                  <select value={selectedRequestId} onChange={(e) => setSelectedRequestId(e.target.value)} className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta bg-white">
                    <option value="">Select approved request</option>
                    {approvedRequests.map((request) => (
                      <option key={request.id} value={request.id}>
                        {request.tracking_code || `Request #${request.id}`}{request.location ? ` â€” ${request.location}` : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
                <p className="text-xs text-blue-800">Once assigned, this team will no longer be available for another request.</p>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={closeAssignModal} className="px-5 py-2.5 rounded-lg border border-slate-200 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition">Cancel</button>
                <button type="button" disabled={!selectedRequestId || requestsLoading || approvedRequests.length === 0} onClick={handleAssignTeam} className="px-5 py-2.5 rounded-lg bg-terracotta hover:bg-terracotta/90 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold transition">Assign Team</button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ResponseUnitsPage;




