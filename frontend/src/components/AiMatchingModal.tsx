import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  AIResourceMatchRecommendation
} from '../types';
import api from '../services/api';
import {
  X,
  Cpu,
  CheckCircle,
  AlertTriangle,
  ShieldCheck,
  MapPin,
  Package,
  Truck,
  FileText
} from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import type {
  AIFacilitySupportRecommendation
} from '../services/api';

export const AiMatchingModal: React.FC = () => {
  const {
    activeMatchModalRequest,
    setActiveMatchModalRequest,
    showNotification,
    setActiveTab,
    setTraceIdInput
  } = useApp();

  const [
    recommendation,
    setRecommendation
  ] = useState<AIResourceMatchRecommendation | null>(
    null
  );

  const [
    facilityRecommendation,
    setFacilityRecommendation
  ] = useState<AIFacilitySupportRecommendation | null>(
    null
  );

  const [
    loading,
    setLoading
  ] = useState(false);

  const [
    submitting,
    setSubmitting
  ] = useState(false);

  const [
    procurementManifest,
    setProcurementManifest
  ] = useState<any | null>(null);

  useEffect(() => {
    if (!activeMatchModalRequest) {
      return;
    }

    setRecommendation(null);
    setFacilityRecommendation(null);
    setProcurementManifest(null);
    setLoading(true);

    Promise.all([
      api.getMatchRecommendation(
        activeMatchModalRequest.id
      ),
      api.getFacilitySupportRecommendation(
        activeMatchModalRequest.id
      )
    ])
      .then(
        ([
          resourceData,
          facilityData
        ]) => {
          setRecommendation(
            resourceData
          );

          setFacilityRecommendation(
            facilityData
          );
        }
      )
      .catch(error => {
        console.error(
          'AI matching error:',
          error
        );

        showNotification(
          'Unable to load AI matching recommendations',
          'error'
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, [
    activeMatchModalRequest,
    showNotification
  ]);

  if (!activeMatchModalRequest) {
    return null;
  }

  const hasInventory =
    !!recommendation &&
    recommendation.recommendations.length > 0;

  const hasShortage =
    !!recommendation &&
    recommendation.remaining_shortages.length > 0;

  const totalRecommendedItems =
    recommendation?.recommendations.length ?? 0;

  const handleApproveAllocation = async () => {
    if (
      !recommendation ||
      recommendation.recommendations.length === 0
    ) {
      showNotification(
        'No verified depot inventory is available for allocation. Create a procurement manifest instead.',
        'error'
      );

      return;
    }

    setSubmitting(true);

    try {
      const firstRecommendation =
        recommendation.recommendations[0];

      const itemsToAllocate =
        recommendation.recommendations.map(
          item => ({
            category: item.category,
            item_name: item.item_name,
            allocated_quantity:
              item.recommended_qty,
            unit: item.unit
          })
        );

      const allocation =
        await api.approveAllocation({
          request_id:
            activeMatchModalRequest.id,

          warehouse_id:
            firstRecommendation.warehouse_id,

          items: itemsToAllocate,

          override_notes:
            'Human Authority approved AI resource recommendation. Inventory locked for manifest generation.'
        });

      showNotification(
        'Allocation approved. Manifest ' +
          allocation.relief_id +
          ' generated. Dispatch requires a separate logistics action.',
        'success'
      );

      setActiveMatchModalRequest(
        null
      );

      setTraceIdInput(
        allocation.relief_id
      );

      setActiveTab('trace');
    } catch (error) {
      console.error(
        'Allocation approval failed:',
        error
      );

      const message =
        error instanceof Error
          ? error.message
          : 'Failed to approve allocation';

      showNotification(
        message,
        'error'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateProcurementManifest =
    async () => {
      if (!recommendation) {
        return;
      }

      if (
        recommendation.remaining_shortages.length ===
        0
      ) {
        showNotification(
          'There are no outstanding procurement requirements.',
          'error'
        );

        return;
      }

      setSubmitting(true);

      try {
        const manifest =
          await api.createProcurementManifest(
            activeMatchModalRequest.id
          );

        setProcurementManifest(
          manifest
        );

        showNotification(
          'Procurement manifest created for the unmet requirements.',
          'success'
        );
      } catch (error) {
        console.error(
          'Procurement manifest error:',
          error
        );

        const message =
          error instanceof Error
            ? error.message
            : 'Failed to create procurement manifest';

        showNotification(
          message,
          'error'
        );
      } finally {
        setSubmitting(false);
      }
    };

  const getFacilityRole = (
    type: string
  ) => {
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
      <div className="bg-ivory rounded-xl border border-slate/20 shadow-elevated w-full max-w-3xl max-h-[92vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150">

        {/* HEADER */}
        <div className="bg-navy text-ivory px-6 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-terracotta" />

              <h3 className="font-bold text-base">
                AI Resource Matching & Allocation Engine
              </h3>
            </div>

            <p className="text-xs text-slate-light mt-0.5">
              Optimizing Community Need ↔ Inventory ↔ Depots ↔ Road Accessibility
            </p>
          </div>

          <button
            onClick={() =>
              setActiveMatchModalRequest(null)
            }
            className="text-slate-light hover:text-ivory rounded p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* BODY */}
        <div className="p-6 overflow-y-auto max-h-[calc(92vh-130px)]">

          {loading || !recommendation ? (
            <div className="py-12 text-center text-slate">
              <div className="flex justify-center mb-3">
                <Cpu className="w-7 h-7 animate-pulse text-terracotta" />
              </div>

              Scanning verified inventory,
              public facilities and support options...
            </div>
          ) : (
            <div>

              {/* REQUEST SUMMARY */}
              <div className="flex items-center justify-between bg-ivory-100 border border-slate/20 rounded-lg p-3.5 mb-4 text-xs">
                <div className="min-w-0">
                  <div className="font-bold text-sm text-navy flex items-center gap-1.5">
                    <MapPin className="w-4 h-4 text-terracotta shrink-0" />

                    <span className="truncate">
                      {activeMatchModalRequest.location_name}
                    </span>

                    <span className="font-normal text-slate shrink-0">
                      ({activeMatchModalRequest.tracking_code})
                    </span>
                  </div>

                  <div className="text-slate-dark mt-0.5">
                    <b>
                      {activeMatchModalRequest.affected_people}
                    </b>{' '}
                    people affected •
                    Water, food and medical support required
                  </div>
                </div>

                <div className="text-right shrink-0 ml-3">
                  <StatusBadge
                    status={
                      recommendation.priority_classification
                    }
                  />

                  <div className="text-[11px] text-slate mt-1 font-mono">
                    {recommendation.priority_score} / 100
                  </div>
                </div>
              </div>

              {/* AI RATIONALE */}
              <div className="bg-navy-900 text-ivory rounded-lg p-4 mb-4 text-xs">
                <div className="flex items-center space-x-2 text-terracotta font-semibold mb-1 uppercase tracking-wider text-[11px]">
                  <Cpu className="w-3.5 h-3.5" />

                  <span>
                    AI Recommendation Rationale
                  </span>
                </div>

                <p className="text-slate-light leading-relaxed">
                  {recommendation.summary_rationale}
                </p>
              </div>

              {/* INVENTORY */}
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-navy">
                  Verified Inventory Matching
                </h4>

                <span className="text-[10px] text-slate">
                  {totalRecommendedItems}{' '}
                  source item
                  {totalRecommendedItems === 1
                    ? ''
                    : 's'}
                </span>
              </div>

              {hasInventory ? (
                <div className="space-y-2 mb-4">
                  {recommendation.recommendations.map(
                    (rec, index) => (
                      <div
                        key={
                          String(
                            rec.warehouse_id
                          ) +
                          '-' +
                          String(index)
                        }
                        className="flex items-center justify-between bg-white border border-slate/20 rounded-lg p-3 text-xs"
                      >
                        <div className="min-w-0">
                          <div className="font-bold text-navy text-sm">
                            {rec.item_name}
                          </div>

                          <div className="text-slate flex flex-wrap items-center gap-2 mt-0.5">
                            <span>
                              Depot:{' '}
                              <b>
                                {rec.warehouse_name}
                              </b>
                            </span>

                            <span>•</span>

                            <span className="text-terracotta font-medium">
                              {rec.distance_km} km
                            </span>

                            {rec.expiry_date && (
                              <>
                                <span>•</span>

                                <span>
                                  Expiry:{' '}
                                  {rec.expiry_date}
                                </span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="text-right shrink-0 ml-4">
                          <div className="text-sm font-extrabold text-navy">
                            {rec.recommended_qty.toLocaleString()}{' '}
                            {rec.unit}
                          </div>

                          <div className="text-[10px] text-slate">
                            Available:{' '}
                            {rec.available_qty.toLocaleString()}{' '}
                            {rec.unit}
                          </div>
                        </div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <div className="bg-slate/5 border border-slate/20 rounded-lg p-4 mb-4">
                  <div className="flex items-start gap-3">
                    <Package className="w-5 h-5 text-slate shrink-0 mt-0.5" />

                    <div>
                      <div className="font-bold text-navy text-sm">
                        No verified depot inventory available
                      </div>

                      <p className="text-xs text-slate mt-1 leading-relaxed">
                        The system found no matching verified stock.
                        ResQFlow will not invent inventory or claim that
                        a depot has supplies that have not been reported.
                      </p>

                      <div className="text-[10px] text-slate mt-2">
                        Inventory status: <b>Not reported / unavailable</b>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* SHORTAGES */}
              {hasShortage && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-amber-700" />

                    <span className="font-bold text-amber-900 text-xs uppercase tracking-wide">
                      Procurement Requirements
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    {recommendation.remaining_shortages.map(
                      (shortage, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between text-xs"
                        >
                          <span className="text-amber-900">
                            {shortage.item_name}
                          </span>

                          <span className="font-bold text-amber-900">
                            {Number(
                              shortage.shortage
                            ).toLocaleString()}{' '}
                            {shortage.unit}
                          </span>
                        </div>
                      )
                    )}
                  </div>

                  <p className="text-[10px] text-amber-800 mt-2">
                    These quantities require verified external procurement
                    or a future inventory update.
                  </p>
                </div>
              )}

              {/* FACILITY SUPPORT */}
              {facilityRecommendation && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-navy">
                      Nearby Facility Support
                    </h4>

                    <span className="text-[10px] text-slate">
                      OpenStreetMap
                    </span>
                  </div>

                  <div className="bg-white border border-slate/20 rounded-lg p-3 mb-2">
                    <p className="text-[11px] text-slate-dark leading-relaxed">
                      {
                        facilityRecommendation.summary_rationale
                      }
                    </p>
                  </div>

                  <div className="space-y-2">
                    {facilityRecommendation.facilities
                      .slice(0, 5)
                      .map(facility => (
                        <div
                          key={
                            facility.osm_type +
                            '-' +
                            facility.osm_id
                          }
                          className="flex items-center justify-between bg-white border border-slate/20 rounded-lg p-3 text-xs"
                        >
                          <div className="min-w-0">
                            <div className="font-bold text-navy text-sm truncate">
                              {facility.name}
                            </div>

                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-terracotta font-semibold">
                                {facility.facility_type}
                              </span>

                              <span className="text-slate">
                                •
                              </span>

                              <span className="text-slate">
                                {getFacilityRole(
                                  facility.facility_type
                                )}
                              </span>
                            </div>

                            <div className="text-[10px] text-slate mt-1 truncate">
                              {facility.address}
                            </div>
                          </div>

                          <div className="text-right shrink-0 ml-3">
                            <div className="font-bold text-navy">
                              {facility.distance_km} km
                            </div>

                            <div className="text-[10px] text-slate">
                              Distance
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* PROCUREMENT MANIFEST */}
              {procurementManifest && (
                <div className="bg-white border-2 border-terracotta/30 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-terracotta" />

                      <div>
                        <div className="font-bold text-navy text-sm">
                          Procurement Manifest
                        </div>

                        <div className="text-[10px] text-slate">
                          {procurementManifest.manifest_id}
                        </div>
                      </div>
                    </div>

                    <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-1 rounded">
                      PROCUREMENT REQUIRED
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs mb-3">
                    <div>
                      <div className="text-[10px] text-slate">
                        Destination
                      </div>

                      <div className="font-semibold text-navy">
                        {procurementManifest.location_name}
                      </div>
                    </div>

                    <div>
                      <div className="text-[10px] text-slate">
                        Request
                      </div>

                      <div className="font-semibold text-navy">
                        {procurementManifest.request_tracking_code}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    {procurementManifest.items?.map(
                      (item: any, index: number) => (
                        <div
                          key={index}
                          className="flex justify-between bg-ivory-100 rounded p-2"
                        >
                          <span>
                            {item.item_name}
                          </span>

                          <b>
                            {Number(
                              item.quantity
                            ).toLocaleString()}{' '}
                            {item.unit}
                          </b>
                        </div>
                      )
                    )}
                  </div>

                  <div className="mt-3 text-[10px] text-slate leading-relaxed">
                    No warehouse inventory was deducted.
                    No vehicle was dispatched.
                    This manifest represents a verified procurement requirement.
                  </div>
                </div>
              )}

              {/* SAFEGUARD */}
              <div className="flex items-start space-x-2 text-[11px] text-slate-dark bg-stone-100 p-2.5 rounded border border-stone-200">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />

                <span>
                  <b>
                    Human-in-the-Loop Safeguard:
                  </b>{' '}
                  Authority approval locks only verified
                  inventory. Dispatch and vehicle movement
                  require a separate logistics action.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* FOOTER */}
        <div className="bg-ivory-100 px-6 py-3 border-t border-slate/20 flex items-center justify-between">
          <button
            onClick={() =>
              setActiveMatchModalRequest(null)
            }
            className="text-xs font-semibold text-slate hover:text-navy"
          >
            Cancel
          </button>

          <div className="flex items-center gap-2">
            {hasShortage &&
              !procurementManifest && (
                <button
                  onClick={
                    handleCreateProcurementManifest
                  }
                  disabled={
                    submitting ||
                    loading
                  }
                  className="bg-white border border-terracotta text-terracotta hover:bg-terracotta/5 font-bold text-xs px-4 py-2.5 rounded-lg flex items-center space-x-1.5 transition-colors disabled:opacity-50"
                >
                  <FileText className="w-4 h-4" />

                  <span>
                    {submitting
                      ? 'Creating...'
                      : 'Create Procurement Manifest'}
                  </span>
                </button>
              )}

            {hasInventory && (
              <button
                onClick={
                  handleApproveAllocation
                }
                disabled={
                  submitting ||
                  loading ||
                  !recommendation ||
                  recommendation.recommendations.length ===
                    0
                }
                className="bg-terracotta hover:bg-terracotta-hover text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-sm flex items-center space-x-1.5 transition-colors disabled:opacity-50"
              >
                <CheckCircle className="w-4 h-4" />

                <span>
                  {submitting
                    ? 'Locking Allocation...'
                    : 'Approve Allocation & Issue Manifest'}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};