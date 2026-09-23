import React, { useEffect, useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { useApp } from '../context/AppContext';
import { GisMap } from '../components/GisMap';
import { StatusBadge } from '../components/StatusBadge';
import { CommunityRequest, AnalyticsData } from '../types';
import api, {
  API_BASE,
  PublicFacility,
  OfficialWarehouse
} from '../services/api';
import {
  Radio,
  ShieldAlert,
  Cpu,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowRight,
  Sliders,
  ExternalLink,
  RefreshCw,
  Box
} from 'lucide-react';
const getFacilityRole = (type: string) => {
  switch (type) {
    case 'Hospital':
      return 'Medical Support';

    case 'Clinic':
      return 'Medical Support';

    case 'Pharmacy':
      return 'Medical Supplies';

    case 'Shelter':
      return 'Evacuation / Relief';

    case 'School':
      return 'Potential Relief Site';

    case 'Community Centre':
      return 'Relief / Community Coordination';

    case 'Police Station':
      return 'Security / Coordination';

    case 'Fire Station':
      return 'Rescue / Emergency Response';

    default:
      return 'Emergency Support';
  }
};

export const AuthorityCommandPage: React.FC = () => {
  const {
    isEmergencyMode,
    isEscalated,
    triggerEscalation,
    triggerReset,
    setActivePriorityModalRequest,
    setActiveMatchModalRequest,
    showNotification
  } = useApp();

  const [requests, setRequests] = useState<CommunityRequest[]>([]);
  const [shortages, setShortages] = useState<any[]>([]);
  const [analytics, setAnalytics] =
    useState<AnalyticsData | null>(null);
  const [facilities, setFacilities] =
  useState<PublicFacility[]>([]);

const [officialWarehouses, setOfficialWarehouses] =
  useState<OfficialWarehouse[]>([]);

const [loading, setLoading] = useState(true);
  const [showFacilities, setShowFacilities] = useState(false);
  const [deliveries, setDeliveries] = useState<any[]>([]);
const [deliveryLoading, setDeliveryLoading] = useState(false);
const [deliveryActionId, setDeliveryActionId] = useState<number | null>(null);
const [showCompleteDelivery, setShowCompleteDelivery] = useState(false);
const [selectedDelivery, setSelectedDelivery] = useState<any>(null);

const [proofPhoto, setProofPhoto] = useState<File | null>(null);
const [proofPhotoUrl, setProofPhotoUrl] = useState('');
const [recipientSignature, setRecipientSignature] = useState('');
const [handoverNotes, setHandoverNotes] = useState('');
const signatureRef = useRef<SignatureCanvas | null>(null);

const loadAll = async () => {
  setLoading(true);

  // Start public facilities immediately.
  // This runs in parallel with the core Command Center data.
  const facilityPromise = api.getPublicFacilities({
    region: 'nashik',
    facility_type: 'all'
  });

  // Load core Command Center data.
  const coreResults = await Promise.allSettled([
    api.getRequests(),
    api.getShortages(),
    api.getAnalytics()
  ]);

  // Requests
  if (coreResults[0].status === 'fulfilled') {
    setRequests(coreResults[0].value);
  } else {
    console.error(
      'Failed to load requests:',
      coreResults[0].reason
    );
  }

  // Shortages
  if (coreResults[1].status === 'fulfilled') {
    setShortages(coreResults[1].value);
  } else {
    console.error(
      'Failed to load shortages:',
      coreResults[1].reason
    );
  }

  // Analytics
  if (coreResults[2].status === 'fulfilled') {
    setAnalytics(coreResults[2].value);
  } else {
    console.error(
      'Failed to load analytics:',
      coreResults[2].reason
    );
  }

  // Core Command Center is ready.
  setLoading(false);

  // Facilities continue loading independently.
  facilityPromise
    .then((facilityData) => {
      setFacilities(facilityData);

      console.log(
        'Public facilities loaded:',
        facilityData.length
      );
    })
    .catch((error) => {
      console.error(
        'Failed to load public facilities:',
        error
      );
    });

  // Load official MSWC warehouses independently.
  api.getOfficialWarehouses('Nashik')
    .then((warehouseData) => {
      setOfficialWarehouses(warehouseData);

      console.log(
        'Official warehouses loaded:',
        warehouseData.length
      );
    })
    .catch((error) => {
      console.error(
        'Failed to load official warehouses:',
        error
      );
    });

  // Load actual delivery operations independently.
  setDeliveryLoading(true);

  api.getDeliveries()
    .then((deliveryData) => {
      setDeliveries(deliveryData);

      console.log(
        'Deliveries loaded:',
        deliveryData.length
      );
    })
    .catch((error) => {
      console.error(
        'Failed to load deliveries:',
        error
      );
    })
    .finally(() => {
      setDeliveryLoading(false);
    });
};

    const facilityCounts = facilities.reduce(
    (counts, facility) => {
      const type = facility.facility_type || 'Unknown';
      counts[type] = (counts[type] || 0) + 1;
      return counts;
    },
    {} as Record<string, number>
  );

  const facilitySummary = [
    { type: 'Hospital', count: facilityCounts['Hospital'] || 0 },
    { type: 'Clinic', count: facilityCounts['Clinic'] || 0 },
    { type: 'Pharmacy', count: facilityCounts['Pharmacy'] || 0 },
    { type: 'Shelter', count: facilityCounts['Shelter'] || 0 },
    { type: 'Police Station', count: facilityCounts['Police Station'] || 0 },
    { type: 'Fire Station', count: facilityCounts['Fire Station'] || 0 },
    { type: 'School', count: facilityCounts['School'] || 0 },
    { type: 'Community Centre', count: facilityCounts['Community Centre'] || 0 }
  ];
const refreshDeliveries = async () => {
  try {
    const data = await api.getDeliveries();
    setDeliveries(data);
  } catch (error) {
    console.error(
      'Failed to refresh deliveries:',
      error
    );
  }
};

const handleDispatch = async (delivery: any) => {
  if (!delivery?.id || !delivery?.allocation_id) {
    showNotification(
      'Delivery or allocation information is missing.'
    );
    return;
  }

  try {
    setDeliveryActionId(delivery.id);

    await api.dispatchDelivery(
      delivery.id,
      delivery.allocation_id
    );

    showNotification(
      'Delivery dispatched successfully.'
    );

    await refreshDeliveries();
  } catch (error: any) {
    console.error(
      'Dispatch failed:',
      error
    );

    showNotification(
      error?.message ||
      'Unable to dispatch delivery.'
    );
  } finally {
    setDeliveryActionId(null);
  }
};

const handleInTransit = async (delivery: any) => {
  if (!delivery?.id) return;

  try {
    setDeliveryActionId(delivery.id);

    await api.updateDeliveryStatus(
      delivery.id,
      'IN_TRANSIT',
      'Relief vehicle departed from warehouse and is travelling to the community.'
    );

    showNotification(
      'Delivery marked as in transit.'
    );

    await refreshDeliveries();
  } catch (error: any) {
    console.error(
      'Status update failed:',
      error
    );

    showNotification(
      error?.message ||
      'Unable to update delivery status.'
    );
  } finally {
    setDeliveryActionId(null);
  }
};
const handleProofPhotoUpload = async (
  event: React.ChangeEvent<HTMLInputElement>
) => {
  const file = event.target.files?.[0];

  if (!file) return;

  if (!file.type.startsWith('image/')) {
    showNotification('Please select an image file.');
    return;
  }

  setProofPhoto(file);

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_BASE}/deliveries/upload-proof-photo`,
      {
        method: 'POST',
        body: formData
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => null);

      throw new Error(
        error?.detail || 'Photo upload failed.'
      );
    }

    const data = await response.json();

    setProofPhotoUrl(data.proof_photo_url);

    showNotification(
      'Handover photo uploaded successfully.'
    );

  } catch (error: any) {
    console.error(
      'Proof photo upload failed:',
      error
    );

    setProofPhoto(null);
    setProofPhotoUrl('');

    showNotification(
      error?.message ||
      'Unable to upload handover photo.'
    );
  }
};


const handleCompleteDelivery = async () => {
  if (!selectedDelivery?.id) {
    showNotification(
      'Delivery information is missing.'
    );
    return;
  }

  if (!proofPhotoUrl) {
    showNotification(
      'Handover photo is required.'
    );
    return;
  }

  if (
    !signatureRef.current ||
    signatureRef.current.isEmpty()
  ) {
    showNotification(
      'Recipient signature is required.'
    );
    return;
  }

  const signature =
    signatureRef.current.toDataURL('image/png');

  try {
    setDeliveryActionId(selectedDelivery.id);

    await api.updateDeliveryStatus(
      selectedDelivery.id,
      'DELIVERED',
      handoverNotes,
      proofPhotoUrl,
      signature
    );

    showNotification(
      'Delivery completed and handover verified.'
    );

    setShowCompleteDelivery(false);
    setSelectedDelivery(null);

    setProofPhoto(null);
    setProofPhotoUrl('');
    setRecipientSignature('');
    setHandoverNotes('');

    signatureRef.current.clear();

    await refreshDeliveries();

  } catch (error: any) {
    console.error(
      'Delivery completion failed:',
      error
    );

    showNotification(
      error?.message ||
      'Unable to complete delivery.'
    );

  } finally {
    setDeliveryActionId(null);
  }
};
  useEffect(() => {
    loadAll();
  }, [isEscalated]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 pb-12">

      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate/20 pb-4 pt-2">

        <div>
          <div className="flex items-center space-x-2">
            <Radio className="w-5 h-5 text-terracotta animate-pulse" />

            <h1 className="text-2xl font-extrabold text-navy font-sans tracking-tight">
              Flood Response Command Center
            </h1>
          </div>

          <p className="text-xs text-slate mt-0.5">
            Real-time emergency operations view &bull; Tungabhadra Basin Unified Coordination
          </p>
        </div>

        {/* =====================================================
            FLOOD SIMULATION STATUS
        ===================================================== */}

        {isEscalated && (
          <div className="
            border
            border-red-200
            bg-red-50
            rounded-xl
            p-4
            shadow-soft
          ">
            <div className="
              flex
              flex-col
              lg:flex-row
              lg:items-center
              lg:justify-between
              gap-4
            ">

              <div>
                <div className="
                  text-[11px]
                  uppercase
                  tracking-wider
                  font-bold
                  text-red-700
                ">
                  Flood Simulation Status
                </div>

                <div className="
                  text-lg
                  font-extrabold
                  text-navy
                  mt-1
                ">
                  Phase 2 — River Basin Breach & Rapid Surge
                </div>

                <div className="
                  text-xs
                  text-red-800
                  mt-1
                ">
                  Emergency conditions escalated by simulation engine
                </div>
              </div>

              <div className="
                grid
                grid-cols-3
                gap-3
              ">

                <div className="
                  bg-white
                  rounded-lg
                  border
                  border-red-100
                  px-4
                  py-3
                ">
                  <div className="
                    text-[10px]
                    uppercase
                    text-slate
                    font-semibold
                  ">
                    Zone B Water
                  </div>

                  <div className="
                    text-xl
                    font-extrabold
                    text-red-700
                  ">
                    3.2m
                  </div>
                </div>

                <div className="
                  bg-white
                  rounded-lg
                  border
                  border-red-100
                  px-4
                  py-3
                ">
                  <div className="
                    text-[10px]
                    uppercase
                    text-slate
                    font-semibold
                  ">
                    Rainfall
                  </div>

                  <div className="
                    text-xl
                    font-extrabold
                    text-red-700
                  ">
                    92.5
                  </div>

                  <div className="
                    text-[9px]
                    text-slate
                  ">
                    mm/hr
                  </div>
                </div>

                <div className="
                  bg-white
                  rounded-lg
                  border
                  border-red-100
                  px-4
                  py-3
                ">
                  <div className="
                    text-[10px]
                    uppercase
                    text-slate
                    font-semibold
                  ">
                    New Critical Need
                  </div>

                  <div className="
                    text-xl
                    font-extrabold
                    text-red-700
                  ">
                    420
                  </div>

                  <div className="
                    text-[9px]
                    text-slate
                  ">
                    people
                  </div>
                </div>

              </div>
            </div>
          </div>
        )}

        {/* Quick Simulation & Refresh Controls */}
        <div className="flex items-center space-x-2.5">

          <button
            onClick={triggerEscalation}
            disabled={isEscalated}
            className={`px-3 py-1.5 text-xs rounded-md font-bold transition-all shadow-sm ${
              isEscalated
                ? 'bg-red-100 text-red-800 border border-red-300 cursor-not-allowed'
                : 'bg-status-critical text-white hover:bg-red-700'
            }`}
          >
            {isEscalated
              ? '⚡ Flood Escalation Active'
              : 'Simulate Flood Escalation'}
          </button>

          <button
            onClick={() => {
              triggerReset();
              loadAll();
            }}
            className="p-1.5 text-slate hover:text-navy border border-slate/30 rounded-md bg-ivory"
            title="Reset simulation to baseline"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">
            People Affected
          </div>

          <div className="text-2xl font-extrabold text-navy mt-1">
            {analytics?.people_affected.toLocaleString() || '1,420'}
          </div>

          <div className="text-[10px] text-slate mt-0.5">
            Across inundated zones
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-critical uppercase tracking-wider">
            Critical Requests
          </div>

          <div className="text-2xl font-extrabold text-status-critical mt-1">
            {analytics?.critical_requests_pending || '4'}
          </div>

          <div className="text-[10px] text-red-600 font-medium mt-0.5">
            Requiring action
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">
            Pending Triage
          </div>

          <div className="text-2xl font-extrabold text-navy mt-1">
            {requests.filter(
              r => r.status === 'PENDING'
            ).length}
          </div>

          <div className="text-[10px] text-slate mt-0.5">
            Unallocated needs
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">
            Fulfillment Rate
          </div>

          <div className="text-2xl font-extrabold text-status-fulfilled mt-1">
            {analytics?.fulfillment_rate_pct || '84.6'}%
          </div>

          <div className="text-[10px] text-slate mt-0.5">
            Overall requests met
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-high uppercase tracking-wider">
            Critical Shortages
          </div>

          <div className="text-2xl font-extrabold text-status-high mt-1">
            {shortages.length}
          </div>

          <div className="text-[10px] text-orange-600 font-medium mt-0.5">
            Water & medical deficits
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-transit uppercase tracking-wider">
            Active Convoys
          </div>

          <div className="text-2xl font-extrabold text-status-transit mt-1">
            {analytics?.active_deliveries || '3'}
          </div>

          <div className="text-[10px] text-sky-700 font-medium mt-0.5">
            En route to shelters
          </div>
        </div>

      </div>

      {/* Main Area: Large GIS Leaflet Map */}
      <div className="space-y-2">

        <div className="flex items-center justify-between text-xs text-slate-dark px-1">
          <span className="font-bold text-navy uppercase tracking-wider">
            Interactive GIS Inundation & Logistics Map
          </span>

          <span>
            Click any village marker or flood polygon to inspect
          </span>
        </div>

        <GisMap height="520px" />

      </div>

            {/* Public Facility Intelligence */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

        <div className="flex items-center justify-between mb-4">

          <div>
            <h3 className="font-bold text-base text-navy">
              Nashik Public Facility Network
            </h3>

            <p className="text-xs text-slate mt-0.5">
              Real facilities mapped from OpenStreetMap
            </p>
          </div>

          <div className="text-right">
            <div className="text-2xl font-extrabold text-navy">
              {facilities.length}
            </div>

            <div className="text-[10px] text-slate uppercase tracking-wider font-semibold">
              Mapped facilities
            </div>
          </div>

        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">

          {facilitySummary.map(item => (

            <div
              key={item.type}
              className="bg-white border border-slate/15 rounded-lg px-3 py-2.5"
            >

              <div className="text-lg font-extrabold text-navy">
                {item.count}
              </div>

              <div className="text-[10px] text-slate font-semibold leading-tight">
                {item.type}
              </div>

            </div>

          ))}

        </div>

      </div>

      {/* Publicly Mapped Facilities */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

              <button
          type="button"
          onClick={() => setShowFacilities(prev => !prev)}
          className="w-full flex items-center justify-between mb-4 pb-2 border-b border-slate/15 text-left"
        >

          <div className="flex items-center gap-2">

            <span className="text-slate text-sm font-bold">
              {showFacilities ? '▼' : '▶'}
            </span>

            <div>
              <h3 className="font-bold text-base text-navy">
                Publicly Mapped Emergency Facilities
              </h3>

              <p className="text-xs text-slate">
                Nashik district facilities retrieved from OpenStreetMap
              </p>
            </div>

          </div>

          <span className="text-xs font-semibold text-slate bg-slate/10 px-2.5 py-1 rounded">
            {facilities.length} mapped
          </span>

        </button>

                {showFacilities && (
          facilities.length === 0 ? (

            <div className="text-sm text-slate py-4">
              No publicly mapped facilities found in Nashik district.
            </div>

          ) : (

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">

            {facilities.map((facility) => (

              <div
                key={`${facility.osm_type}-${facility.osm_id}`}
                className="bg-white border border-slate/20 rounded-lg p-4"
              >

                <div className="flex items-start justify-between gap-3">

                  <div>
                    <div className="font-bold text-navy">
                      {facility.name}
                    </div>

                    <div className="text-[11px] text-terracotta font-semibold mt-1">
  {facility.facility_type}
</div>

<div className="mt-2">
  <span className="text-[10px] font-semibold text-navy bg-navy/5 px-2 py-1 rounded">
    {getFacilityRole(facility.facility_type)}
  </span>
</div>
                  </div>

                  <span className="text-[9px] font-semibold text-slate bg-slate/10 px-2 py-1 rounded">
                    OSM
                  </span>

                </div>

                <div className="text-[11px] text-slate mt-3">
                  {facility.address}
                </div>

                <div className="text-[10px] text-slate mt-2 font-mono">
                  {facility.latitude.toFixed(5)}, {facility.longitude.toFixed(5)}
                </div>

                

                {facility.source_url && (
                  <a
                    href={facility.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] text-terracotta hover:underline mt-3"
                  >
                    View OpenStreetMap

                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}

              </div>

                        ))}

          </div>

          )
        )}

      </div>        
      {/* Official MSWC Warehouses */}
<div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

  <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">

    <div>
      <h3 className="font-bold text-base text-navy">
        Official MSWC Warehouses
      </h3>

      <p className="text-xs text-slate mt-0.5">
        Official warehouse records from Maharashtra State Warehousing Corporation
      </p>
    </div>

    <div className="text-right">
      <div className="text-2xl font-extrabold text-navy">
        {officialWarehouses.length}
      </div>

      <div className="text-[10px] text-slate uppercase tracking-wider font-semibold">
        Official warehouses
      </div>
    </div>

  </div>

  <div className="mb-4 rounded-lg border border-slate/15 bg-white px-4 py-3">

    <div className="text-xs font-semibold text-navy">
      Official source data
    </div>

    <div className="text-[11px] text-slate mt-1">
      Warehouse identity, address, godown count and storage capacity
      are sourced from MSWC. Live inventory and coordinates are not
      reported unless independently verified.
    </div>

  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">

    {officialWarehouses.map((warehouse) => (

      <div
        key={warehouse.id}
        className="bg-white border border-slate/20 rounded-lg p-4"
      >

        <div className="flex items-start justify-between gap-3">

          <div>
            <div className="font-bold text-navy">
              {warehouse.warehouse_name}
            </div>

            <div className="text-[11px] text-terracotta font-semibold mt-1">
              Plant Code: {warehouse.plant_code}
            </div>
          </div>

          <span className="text-[9px] font-semibold text-navy bg-navy/5 px-2 py-1 rounded">
            MSWC
          </span>

        </div>

        <div className="mt-3 space-y-2">

          <div className="flex justify-between text-[11px]">
            <span className="text-slate">
              Taluka
            </span>

            <span className="font-semibold text-navy">
              {warehouse.taluka || 'Not reported'}
            </span>
          </div>

          <div className="flex justify-between text-[11px]">
            <span className="text-slate">
              Capacity
            </span>

            <span className="font-semibold text-navy">
              {warehouse.capacity_mt != null
                ? `${warehouse.capacity_mt.toLocaleString()} MT`
                : 'Not reported'}
            </span>
          </div>

          <div className="flex justify-between text-[11px]">
            <span className="text-slate">
              Godowns
            </span>

            <span className="font-semibold text-navy">
              {warehouse.godown_count ?? 'Not reported'}
            </span>
          </div>

        </div>

        <div className="mt-3 pt-2 border-t border-slate/15">

          <div className="text-[10px] text-slate">
            Address
          </div>

          <div className="text-[11px] text-navy mt-1 leading-relaxed">
            {warehouse.address}
          </div>

        </div>

        <div className="mt-3 pt-2 border-t border-slate/15 space-y-1">

          <div className="flex justify-between text-[10px]">
            <span className="text-slate">
              Location
            </span>

            <span className="font-semibold text-terracotta">
              {warehouse.location_status ===
              'PENDING_COORDINATE_VERIFICATION'
                ? 'Pending verification'
                : 'Verified'}
            </span>
          </div>

          <div className="flex justify-between text-[10px]">
            <span className="text-slate">
              Inventory
            </span>

            <span className="font-semibold text-slate">
              {warehouse.inventory_status === 'NOT_REPORTED'
                ? 'Not reported'
                : warehouse.inventory_status}
            </span>
          </div>

        </div>

      </div>

    ))}

  </div>

</div>   
{/* ============================================================
    DELIVERY OPERATIONS
============================================================ */}

<div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

  <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">

    <div>
      <h3 className="font-bold text-base text-navy">
        Delivery Operations
      </h3>

      <p className="text-xs text-slate mt-0.5">
        Operational control for approved relief allocations
      </p>
    </div>

    <div className="flex items-center gap-2">

      <span className="text-xs font-semibold text-navy bg-navy/5 px-2.5 py-1 rounded">
        {deliveries.length} deliveries
      </span>

      <button
        type="button"
        onClick={refreshDeliveries}
        className="p-1.5 text-slate hover:text-navy border border-slate/20 rounded-md bg-white"
        title="Refresh deliveries"
      >
        <RefreshCw className="w-4 h-4" />
      </button>

    </div>

  </div>

  {deliveryLoading && deliveries.length === 0 ? (

    <div className="text-sm text-slate py-5">
      Loading delivery operations...
    </div>

  ) : deliveries.length === 0 ? (

    <div className="text-sm text-slate py-5">
      No delivery has been created yet. Approve a verified allocation
      to create the delivery record.
    </div>

  ) : (

    <div className="space-y-3">

      {deliveries.map((delivery) => {

        const status = String(
          delivery.status || ''
        ).toUpperCase();

        const isAllocated =
          status === 'ALLOCATED';

        const isDispatched =
          status === 'DISPATCHED';

        const isInTransit =
          status === 'IN_TRANSIT';

        const isDelivered =
          status === 'DELIVERED';

        const isWorking =
          deliveryActionId === delivery.id;

        return (

          <div
            key={delivery.id}
            className="bg-white border border-slate/20 rounded-xl p-4"
          >

            {/* Delivery Header */}

            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3">

              <div>

                <div className="flex items-center gap-2">

                  <span className="font-bold text-navy">
                    {delivery.relief_id}
                  </span>

                  <StatusBadge
                    status={status}
                    size="sm"
                  />

                </div>

                <div className="text-[11px] text-slate mt-1">
                  Delivery ID: #{delivery.id}
                  {' • '}
                  Allocation ID: #{delivery.allocation_id}
                </div>

              </div>

              <div className="text-right">

                <div className="text-[10px] uppercase tracking-wider text-slate font-semibold">
                  Destination
                </div>

                <div className="text-xs font-semibold text-navy mt-0.5">
                  {delivery.destination_location_name}
                </div>

              </div>

            </div>


            {/* Delivery Details */}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">

              <div className="bg-ivory border border-slate/15 rounded-lg p-3">

                <div className="text-[10px] uppercase tracking-wider text-slate font-semibold">
                  Origin
                </div>

                <div className="text-xs font-semibold text-navy mt-1">
                  Warehouse #{delivery.origin_warehouse_id}
                </div>

              </div>

              <div className="bg-ivory border border-slate/15 rounded-lg p-3">

                <div className="text-[10px] uppercase tracking-wider text-slate font-semibold">
                  Vehicle
                </div>

                <div className="text-xs font-semibold text-navy mt-1">
                  {delivery.vehicle_id
                    ? `Vehicle #${delivery.vehicle_id}`
                    : 'Not assigned'}
                </div>

              </div>

              

            </div>


            {/* Operational Timeline */}

            <div className="flex flex-wrap items-center gap-2 mt-4 text-[10px] font-semibold">

              <span
                className={
                  status === 'ALLOCATED' ||
                  status === 'DISPATCHED' ||
                  status === 'IN_TRANSIT' ||
                  status === 'DELIVERED'
                    ? 'text-status-fulfilled'
                    : 'text-slate'
                }
              >
                1. Allocated
              </span>

              <ArrowRight className="w-3 h-3 text-slate" />

              <span
                className={
                  status === 'DISPATCHED' ||
                  status === 'IN_TRANSIT' ||
                  status === 'DELIVERED'
                    ? 'text-status-fulfilled'
                    : 'text-slate'
                }
              >
                2. Dispatched
              </span>

              <ArrowRight className="w-3 h-3 text-slate" />

              <span
                className={
                  status === 'IN_TRANSIT' ||
                  status === 'DELIVERED'
                    ? 'text-status-fulfilled'
                    : 'text-slate'
                }
              >
                3. In Transit
              </span>

              <ArrowRight className="w-3 h-3 text-slate" />

              <span
                className={
                  status === 'DELIVERED'
                    ? 'text-status-fulfilled'
                    : 'text-slate'
                }
              >
                4. Delivered
              </span>

            </div>


            {/* Actions */}

            <div className="mt-4 pt-3 border-t border-slate/15 flex flex-wrap gap-2">

              {isAllocated && (

                <button
                  type="button"
                  disabled={isWorking}
                  onClick={() =>
                    handleDispatch(delivery)
                  }
                  className="bg-terracotta hover:bg-terracotta-hover disabled:opacity-50 text-white px-3 py-1.5 rounded-md text-xs font-semibold"
                >
                  {isWorking
                    ? 'Dispatching...'
                    : 'Dispatch Delivery'}
                </button>

              )}


              {isDispatched && (

                <button
                  type="button"
                  disabled={isWorking}
                  onClick={() =>
                    handleInTransit(delivery)
                  }
                  className="bg-navy hover:opacity-90 disabled:opacity-50 text-white px-3 py-1.5 rounded-md text-xs font-semibold"
                >
                  {isWorking
                    ? 'Updating...'
                    : 'Mark In Transit'}
                </button>

              )}


              {isInTransit && (

  <button
    type="button"
    disabled={isWorking}
    onClick={() => {
      setSelectedDelivery(delivery);
      setShowCompleteDelivery(true);
    }}
    className="bg-terracotta hover:bg-terracotta-hover disabled:opacity-50 text-white px-3 py-1.5 rounded-md text-xs font-semibold"
  >
    {isWorking
      ? 'Completing...'
      : 'Complete Delivery'}
  </button>

)}


              {isDelivered && (

                <div className="flex items-center gap-2 text-xs text-green-700 bg-green-50 border border-green-200 px-3 py-1.5 rounded-md">

                  <CheckCircle className="w-3.5 h-3.5" />

                  Delivery completed and recorded.

                </div>

              )}

            </div>

          </div>

        );
      })}

    </div>

  )}

</div>

      {/* Two-Column Lower Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Priority Requests Queue */}
        <div className="lg:col-span-7 bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">

            <div>
              <h3 className="font-bold text-base text-navy">
                Priority Relief Requests
              </h3>

              <p className="text-xs text-slate">
                Ranked automatically by explainable AI scoring
              </p>
            </div>

            <span className="text-xs font-semibold text-terracotta bg-terracotta/10 px-2.5 py-1 rounded">
              {requests.length} Total Requests
            </span>

          </div>

          <div className="overflow-x-auto overflow-y-auto max-h-[430px]">

            <table className="w-full text-left text-xs">

              <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">

                <tr>
                  <th className="py-2.5 px-3">
                    Location / ID
                  </th>

                  <th className="py-2.5 px-3">
                    Affected
                  </th>

                  <th className="py-2.5 px-3">
                    AI Priority
                  </th>

                  <th className="py-2.5 px-3">
                    Status
                  </th>

                  <th className="py-2.5 px-3 text-right">
                    Actions
                  </th>
                </tr>

              </thead>

              <tbody className="divide-y divide-slate/15">

                {requests
                  .filter(
                    req => req.status !== 'DELIVERED'
                  )
                  .map(req => {

                    const isCrit =
                      req.priority_classification === 'CRITICAL' ||
                      req.priority_score >= 80;

                    return (
                      <tr
                        key={req.id}
                        className={`hover:bg-ivory-50 transition-colors ${
                          isCrit &&
                          req.status === 'PENDING'
                            ? 'bg-red-50/40'
                            : ''
                        }`}
                      >

                        <td className="py-3 px-3">

                          <div className="font-bold text-navy">
                            {req.location_name}
                          </div>

                          <div className="text-[10px] font-mono text-slate">
                            {req.tracking_code}
                          </div>

                        </td>

                        <td className="py-3 px-3">

                          <div className="font-semibold text-slate-dark">
                            {req.affected_people} people
                          </div>

                          <div className="text-[10px] text-slate">
                            {(req.vulnerable_elderly || 0) +
                              (req.vulnerable_children || 0)} vulnerable
                          </div>

                        </td>

                        <td className="py-3 px-3">

                          <div className="flex items-center gap-1.5">

                            <span
                              className={`font-mono font-bold px-1.5 py-0.5 rounded text-[11px] ${
                                isCrit
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-orange-100 text-orange-800'
                              }`}
                            >
                              {Math.round(
                                req.priority_score
                              )}/100
                            </span>

                            <button
                              onClick={() =>
                                setActivePriorityModalRequest(req)
                              }
                              className="text-[10px] text-slate hover:text-terracotta underline ml-1"
                            >
                              Explain
                            </button>

                          </div>

                        </td>

                        <td className="py-3 px-3">
                          <StatusBadge
                            status={req.status}
                            size="sm"
                          />
                        </td>

                        <td className="py-3 px-3 text-right">

                          {req.status === 'PENDING' ||
                          req.status === 'VERIFIED' ? (

                            <button
                              onClick={() =>
                                setActiveMatchModalRequest(req)
                              }
                              className="bg-terracotta hover:bg-terracotta-hover text-white px-2.5 py-1 rounded text-[11px] font-semibold transition-colors"
                            >
                              Match AI
                            </button>

                          ) : (

                            <span className="text-[11px] text-slate">
                              Locked
                            </span>

                          )}

                        </td>

                      </tr>
                    );
                  })}

              </tbody>

            </table>

          </div>

        </div>
      {/* ============================================================
          COMPLETE DELIVERY MODAL
      ============================================================ */}

      {showCompleteDelivery && selectedDelivery && (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/50 backdrop-blur-sm px-4">

          <div className="w-full max-w-lg bg-ivory rounded-xl shadow-2xl border border-slate/20 overflow-hidden">

            <div className="px-5 py-4 border-b border-slate/15 flex items-center justify-between">

              <div>
                <h2 className="text-lg font-bold text-navy">
                  Complete Delivery
                </h2>

                <p className="text-xs text-slate mt-0.5">
                  Verify the community handover before completing this delivery.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setShowCompleteDelivery(false);
                  setSelectedDelivery(null);
                }}
                className="text-slate hover:text-navy text-lg"
              >
                ×
              </button>

            </div>

            <div className="p-5 space-y-5">

              {/* Delivery Info */}

              <div className="bg-white border border-slate/15 rounded-lg p-3">

                <div className="flex items-center justify-between">

                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-slate font-semibold">
                      Relief Package
                    </div>

                    <div className="text-sm font-bold text-navy mt-1">
                      {selectedDelivery.relief_id}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-[10px] uppercase tracking-wider text-slate font-semibold">
                      Delivery
                    </div>

                    <div className="text-sm font-bold text-navy mt-1">
                      #{selectedDelivery.id}
                    </div>
                  </div>

                </div>

              </div>


              {/* Handover Photo */}

              <div>

                <label className="block text-xs font-bold text-navy mb-2">
                  Handover Photo
                </label>

                <p className="text-[11px] text-slate mb-2">
                  Photo of the relief items being handed over.
                </p>

                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleProofPhotoUpload}
                  className="block w-full text-xs text-slate"
                />

                {proofPhoto && (

                  <div className="mt-2 text-[10px] text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-2">
                    ✓ {proofPhoto.name} uploaded
                  </div>

                )}

              </div>


              {/* Recipient Signature */}

              <div>

                <label className="block text-xs font-bold text-navy mb-2">
                  Recipient Signature
                </label>

                <p className="text-[11px] text-slate mb-2">
                  Signature of the person receiving the relief.
                </p>

                <div className="bg-white border border-slate/25 rounded-lg overflow-hidden">

                  <SignatureCanvas
                    ref={signatureRef}
                    penColor="#0F1E36"
                    onEnd={() => {
                      if (
                        signatureRef.current &&
                        !signatureRef.current.isEmpty()
                      ) {
                        setRecipientSignature(
                          signatureRef.current.toDataURL('image/png')
                        );
                      }
                    }}
                    canvasProps={{
                      width: 460,
                      height: 160,
                      className: "w-full h-40"
                    }}
                  />

                </div>

                <button
                  type="button"
                  onClick={() => {
                    signatureRef.current?.clear();
                    setRecipientSignature('');
                  }}
                  className="text-[11px] text-slate hover:text-navy underline mt-2"
                >
                  Clear Signature
                </button>

              </div>


              {/* Handover Notes */}

              <div>

                <label className="block text-xs font-bold text-navy mb-2">
                  Handover Notes
                  <span className="font-normal text-slate">
                    {' '}— optional
                  </span>
                </label>

                <textarea
                  value={handoverNotes}
                  onChange={(e) =>
                    setHandoverNotes(e.target.value)
                  }
                  rows={3}
                  placeholder="Optional handover notes"
                  className="w-full border border-slate/25 rounded-lg px-3 py-2 text-xs text-navy bg-white"
                />

              </div>


              {/* Buttons */}

              <div className="flex justify-end gap-2 pt-3 border-t border-slate/15">

                <button
                  type="button"
                  onClick={() => {
                    setShowCompleteDelivery(false);
                    setSelectedDelivery(null);
                    setProofPhoto(null);
                    setProofPhotoUrl('');
                    setRecipientSignature('');
                    setHandoverNotes('');
                    signatureRef.current?.clear();
                  }}
                  className="px-4 py-2 rounded-md text-xs font-semibold text-slate border border-slate/25 bg-white"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={handleCompleteDelivery}
                  disabled={
                    deliveryActionId === selectedDelivery.id ||
                    !proofPhotoUrl ||
                    !recipientSignature
                  }
                  className="px-4 py-2 rounded-md text-xs font-semibold text-white bg-terracotta hover:bg-terracotta-hover disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {deliveryActionId === selectedDelivery.id
                    ? 'Completing...'
                    : 'Confirm Delivery'}
                </button>

              </div>

            </div>

          </div>

        </div>

      )}
        {/* Shortage Radar */}
        <div className="lg:col-span-5 bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">

          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">

            <div>
              <h3 className="font-bold text-base text-navy">
                Shortage Radar
              </h3>

              <p className="text-xs text-slate">
                Automatic detection of critical regional deficits
              </p>
            </div>

            <span className="text-xs font-bold text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
              DEFICITS
            </span>

          </div>

          <div className="space-y-3">

            {shortages.map(item => (

              <div
                key={item.id}
                className="bg-white border border-slate/20 rounded-lg p-3.5 text-xs"
              >

                <div className="flex items-center justify-between">

                  <span className="font-bold text-sm text-navy">
                    {item.sector}
                  </span>

                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-100 text-red-800">
                    SHORTAGE: -{item.shortage.toLocaleString()} {item.unit}
                  </span>

                </div>

                <div className="text-[11px] text-slate mt-0.5">
                  Category: <b>{item.category}</b> &bull; {item.zone}
                </div>

                <div className="mt-2 text-[11px] text-slate-dark border-t border-slate/15 pt-2">

                  <div className="font-semibold mb-1">
                    Potential Sourcing Depots:
                  </div>

                  <ul className="space-y-0.5">

                    {item.potential_sources.map(
                      (src: any, sIdx: number) => (

                        <li
                          key={sIdx}
                          className="flex justify-between text-[11px]"
                        >

                          <span>
                            {src.name} ({src.distance_km} km):
                          </span>

                          <b>
                            {src.stock.toLocaleString()} {item.unit} avail
                          </b>

                        </li>
                      )
                    )}

                  </ul>

                </div>

              </div>
            ))}

          </div>

        </div>

      </div>

    </div>
  );
};
