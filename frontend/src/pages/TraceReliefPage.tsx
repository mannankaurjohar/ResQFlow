import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { ReliefTraceResponse } from '../types';
import api from '../services/api';
import {
  Search, CheckCircle2, Clock, Truck, ShieldCheck, MapPin,
  HeartHandshake, FileCheck, PackageCheck, AlertCircle
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export const TraceReliefPage: React.FC = () => {
  const { traceIdInput, setTraceIdInput } = useApp();
  const [currentId, setCurrentId] = useState(traceIdInput || 'RELIEF-2026-00482');
  const [traceData, setTraceData] = useState<ReliefTraceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrace = (id: string) => {
    if (!id.trim()) return;
    setLoading(true);
    setError(null);
    api.traceRelief(id.trim())
      .then(data => setTraceData(data))
      .catch(err => {
        setError(`No tracking record found for '${id}'. Try 'RELIEF-2026-00482' or 'D-10284'.`);
        setTraceData(null);
      })
      .finally(() => setLoading(false));
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

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
          Transparent Relief Tracking
        </h1>
        <p className="text-xs sm:text-sm text-slate mt-1">
          Every contribution and allocation is publicly traceable from donor to verified community handover.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-4 shadow-soft">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={currentId}
              onChange={e => setCurrentId(e.target.value)}
              placeholder="Enter Relief Package ID (e.g. RELIEF-2026-00482 or D-10284)"
              className="w-full bg-white border border-slate/30 text-navy font-mono rounded-lg pl-10 pr-4 py-2.5 text-xs sm:text-sm focus:outline-none focus:border-terracotta"
            />
          </div>
          <button
            type="submit"
            className="bg-navy hover:bg-navy-800 text-white font-bold px-5 py-2.5 rounded-lg text-xs sm:text-sm transition-colors"
          >
            Trace
          </button>
        </form>

        <div className="mt-2 text-[11px] text-slate flex items-center gap-2">
          <span>Demo Signature Packages:</span>
          <button
            onClick={() => { setCurrentId('RELIEF-2026-00482'); fetchTrace('RELIEF-2026-00482'); }}
            className="text-terracotta underline font-mono"
          >
            RELIEF-2026-00482
          </button>
          <span>&bull;</span>
          <button
            onClick={() => { setCurrentId('D-10284'); fetchTrace('D-10284'); }}
            className="text-terracotta underline font-mono"
          >
            D-10284 (Anita & Vikram)
          </button>
        </div>
      </div>

      {loading && (
        <div className="py-16 text-center text-slate">Verifying cryptographic ledger and telemetry...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Trace Journey Card */}
      {traceData && (
        <div className="space-y-6">
          
          {/* Top Summary Banner */}
          <div className="bg-gradient-to-r from-navy to-navy-900 text-ivory rounded-xl p-6 shadow-elevated border border-navy-700">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="text-[11px] font-semibold text-slate-light uppercase tracking-wider">
                  Verified Relief Manifest
                </div>
                <div className="text-2xl sm:text-3xl font-extrabold text-ivory font-mono mt-0.5">
                  {traceData.relief_id}
                </div>
                <div className="text-xs text-slate-light mt-1 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-terracotta" />
                  <span>Destination: <b>{traceData.destination_location}</b> ({traceData.destination_zone})</span>
                </div>
              </div>

              <div className="text-left sm:text-right">
                <StatusBadge status={traceData.current_status} size="lg" />
                <div className="text-xs text-slate-light mt-2">
                  Impact: <b>~{traceData.people_supported} people supported</b>
                </div>
              </div>
            </div>

            {/* Item Manifest Pill Summary */}
            <div className="mt-5 pt-4 border-t border-navy-800 flex flex-wrap gap-2 text-xs">
              <span className="text-slate-light font-medium py-1">Cargo Manifest:</span>
              {traceData.items_summary.map((it, idx) => (
                <span key={idx} className="bg-navy-800 border border-slate/30 text-ivory px-2.5 py-1 rounded-md font-semibold">
                  {it.quantity.toLocaleString()} {it.unit} {it.item_name}
                </span>
              ))}
            </div>
          </div>

          {/* Signature 8-Step Visual Timeline */}
          <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
            <h3 className="font-bold text-base text-navy mb-6 flex items-center gap-2">
              <PackageCheck className="w-5 h-5 text-terracotta" />
              <span>Full Resource Journey (End-to-End Chain of Custody)</span>
            </h3>

            <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate/20">
              {traceData.timeline.map((step, idx) => {
                const isComp = step.status === 'COMPLETED';
                const isCurr = step.status === 'CURRENT';

                return (
                  <div key={idx} className="relative text-xs">
                    {/* Circle Node */}
                    <div className={`absolute -left-6 sm:-left-8 top-0.5 w-6 h-6 rounded-full flex items-center justify-center border-2 ${
                      isComp ? 'bg-status-fulfilled border-white text-white' :
                      isCurr ? 'bg-terracotta border-white text-white animate-pulse' :
                      'bg-stone-200 border-white text-slate'
                    }`}>
                      {isComp ? <CheckCircle2 className="w-3.5 h-3.5" /> : idx + 1}
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="font-bold text-sm text-navy flex items-center gap-2">
                        <span>{step.label}</span>
                        {isCurr && <span className="text-[10px] bg-terracotta text-white px-2 py-0.2 rounded font-semibold">ACTIVE STAGE</span>}
                      </div>
                      <div className="text-slate font-mono text-[11px]">{step.timestamp || 'Pending execution'}</div>
                    </div>

                    <div className="text-slate-dark mt-1 text-xs">
                      {step.details}
                    </div>

                    {step.actor && (
                      <div className="text-[11px] text-slate mt-0.5">
                        Custodian: <span className="font-medium text-navy">{step.actor}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Proof of Delivery / Handover Receipt */}
          {traceData.proof_of_delivery && (
            <div className="bg-white border border-slate/20 rounded-xl p-6 shadow-soft text-xs">
              <div className="flex items-center space-x-2 text-status-fulfilled font-bold mb-3">
                <ShieldCheck className="w-5 h-5 text-status-fulfilled" />
                <span className="text-sm uppercase tracking-wider">Verified Proof of Community Delivery</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="text-slate mb-1">Delivered Handover Signature:</div>
                  <div className="font-mono font-bold text-navy text-sm p-3 bg-ivory-100 rounded-lg border border-slate/20">
                    {traceData.proof_of_delivery.recipient_signature}
                  </div>
                  <div className="text-[11px] text-slate mt-2">
                    Verified on: {traceData.proof_of_delivery.delivered_at}
                  </div>
                  <div className="text-slate-dark text-xs mt-2">
                    {traceData.proof_of_delivery.notes}
                  </div>
                </div>

                <div>
                  <div className="text-slate mb-1">Field Photographic Evidence:</div>
                  <div className="rounded-lg overflow-hidden border border-slate/20 max-h-48">
                    <img
                      src={traceData.proof_of_delivery.proof_photo_url}
                      alt="Proof of Delivery Handover"
                      className="w-full h-40 object-cover"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
};