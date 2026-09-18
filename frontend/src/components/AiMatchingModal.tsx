import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { AIResourceMatchRecommendation } from '../types';
import api from '../services/api';
import { X, Cpu, CheckCircle, AlertTriangle, ShieldCheck, MapPin } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export const AiMatchingModal: React.FC = () => {
  const { activeMatchModalRequest, setActiveMatchModalRequest, showNotification, setActiveTab, setTraceIdInput } = useApp();
  const [recommendation, setRecommendation] = useState<AIResourceMatchRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!activeMatchModalRequest) return;
    setLoading(true);
    api.getMatchRecommendation(activeMatchModalRequest.id)
      .then(data => setRecommendation(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [activeMatchModalRequest]);

  if (!activeMatchModalRequest) return null;

  const handleApproveAllocation = async () => {
    if (!recommendation || recommendation.recommendations.length === 0) {
      showNotification('No matching inventory available to allocate', 'error');
      return;
    }

    setSubmitting(true);
    try {
      const topRec = recommendation.recommendations[0];
      const itemsToAllocate = recommendation.recommendations.map(r => ({
        category: r.category,
        item_name: r.item_name,
        allocated_quantity: r.recommended_qty,
        unit: r.unit
      }));

      const alloc = await api.approveAllocation({
        request_id: activeMatchModalRequest.id,
        warehouse_id: topRec.warehouse_id,
        items: itemsToAllocate,
        override_notes: `Human Authority Approved AI Recommendation: Allocated from ${topRec.warehouse_name}.`
      });

      showNotification(`Relief Allocation locked! Manifest ${alloc.relief_id} issued for dispatch.`, 'success');
      setActiveMatchModalRequest(null);
      setTraceIdInput(alloc.relief_id);
      setActiveTab('trace');
    } catch (err) {
      showNotification('Failed to approve allocation', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
      <div className="bg-ivory rounded-xl border border-slate/20 shadow-elevated w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="bg-navy text-ivory px-6 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-terracotta" />
              <h3 className="font-bold text-base">AI Resource Matching & Allocation Engine</h3>
            </div>
            <p className="text-xs text-slate-light mt-0.5">
              Optimizing Community Need ↔ Inventory ↔ Depots ↔ Road Accessibility
            </p>
          </div>
          <button onClick={() => setActiveMatchModalRequest(null)} className="text-slate-light hover:text-ivory rounded p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {loading || !recommendation ? (
            <div className="py-12 text-center text-slate">Scanning warehouse network and route accessibility...</div>
          ) : (
            <div>
              <div className="flex items-center justify-between bg-ivory-100 border border-slate/20 rounded-lg p-3.5 mb-4 text-xs">
                <div>
                  <div className="font-bold text-sm text-navy flex items-center gap-1.5">
                    <MapPin className="w-4 h-4 text-terracotta" />
                    <span>{activeMatchModalRequest.location_name}</span>
                    <span className="font-normal text-slate">({activeMatchModalRequest.tracking_code})</span>
                  </div>
                  <div className="text-slate-dark mt-0.5">
                    <b>{activeMatchModalRequest.affected_people} people</b> stranded &bull; Requires water, rations, medicines
                  </div>
                </div>
                <div className="text-right">
                  <StatusBadge status={recommendation.priority_classification} />
                  <div className="text-[11px] text-slate mt-1 font-mono">{recommendation.priority_score} / 100 Score</div>
                </div>
              </div>

              <div className="bg-navy-900 text-ivory rounded-lg p-4 mb-4 text-xs">
                <div className="flex items-center space-x-2 text-terracotta font-semibold mb-1 uppercase tracking-wider text-[11px]">
                  <span>AI Recommendation Rationale (Explainable)</span>
                </div>
                <p className="text-slate-light leading-relaxed">
                  {recommendation.summary_rationale}
                </p>
              </div>

              <h4 className="text-xs font-bold uppercase tracking-wider text-navy mb-2">
                Recommended Source & Quantity
              </h4>

              <div className="space-y-2 mb-4">
                {recommendation.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-center justify-between bg-white border border-slate/20 rounded-lg p-3 text-xs">
                    <div>
                      <div className="font-bold text-navy text-sm">{rec.item_name}</div>
                      <div className="text-slate flex items-center gap-2 mt-0.5">
                        <span>Depot: <b>{rec.warehouse_name}</b></span>
                        <span>&bull;</span>
                        <span className="text-terracotta font-medium">{rec.distance_km} km away</span>
                        {rec.expiry_date && <span>&bull; Batch Expiry: {rec.expiry_date}</span>}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-extrabold text-navy">
                        {rec.recommended_qty.toLocaleString()} {rec.unit}
                      </div>
                      <div className="text-[10px] text-slate">Available: {rec.available_qty.toLocaleString()} {rec.unit}</div>
                    </div>
                  </div>
                ))}
              </div>

              {recommendation.is_partial && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 text-xs flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-amber-900">Partial Fulfillment Mode Active:</span>
                    <p className="text-amber-800 text-[11px] mt-0.5">
                      Depot supplies are insufficient to satisfy 100% of demand. Deficit flagged for procurement.
                    </p>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-2 text-[11px] text-slate-dark bg-stone-100 p-2.5 rounded border border-stone-200">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  <b>Human-in-the-Loop Safeguard:</b> Approval locks inventory, assigns convoy transport, and records a cryptographic audit entry.
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="bg-ivory-100 px-6 py-3 border-t border-slate/20 flex items-center justify-between">
          <button onClick={() => setActiveMatchModalRequest(null)} className="text-xs font-semibold text-slate hover:text-navy">Cancel</button>
          <button
            onClick={handleApproveAllocation}
            disabled={submitting || !recommendation || recommendation.recommendations.length === 0}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-sm flex items-center space-x-1.5 transition-colors disabled:opacity-50"
          >
            <CheckCircle className="w-4 h-4" />
            <span>{submitting ? 'Locking Allocation...' : 'Approve Allocation & Issue Manifest'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
