from helper_writer import write_file

# 1. CommunityReportPage.tsx
report_code = """import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { AIUnderstandingResponse, ExtractedItem } from '../types';
import api from '../services/api';
import {
  Sparkles, Send, CheckCircle2, AlertCircle, Edit2, MapPin, Users,
  ShieldAlert, RefreshCw, ArrowRight
} from 'lucide-react';

export const CommunityReportPage: React.FC = () => {
  const { showNotification, setActiveTab, setTraceIdInput } = useApp();

  const [nlText, setNlText] = useState(
    "Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children."
  );
  const [parsing, setParsing] = useState(false);
  const [aiUnderstanding, setAiUnderstanding] = useState<AIUnderstandingResponse | null>(null);

  // Form fields (populated by AI and user editable)
  const [locationName, setLocationName] = useState('Village A');
  const [affectedPeople, setAffectedPeople] = useState(350);
  const [affectedHouseholds, setAffectedHouseholds] = useState(85);
  const [vulnerableElderly, setVulnerableElderly] = useState(40);
  const [vulnerableChildren, setVulnerableChildren] = useState(25);
  const [urgency, setUrgency] = useState('CRITICAL');
  const [reporterName, setReporterName] = useState('Sarpanch Ramesh');
  const [reporterPhone, setReporterPhone] = useState('+91 94812 33491');
  const [items, setItems] = useState<ExtractedItem[]>([
    { category: 'Drinking Water', item_name: 'Clean Drinking Water', quantity: 2000, unit: 'Liters' },
    { category: 'Food', item_name: 'Ready-to-Eat Food Packets', quantity: 700, unit: 'Packets' },
    { category: 'Medicines', item_name: 'Emergency Medicine Kits', quantity: 35, unit: 'Kits' }
  ]);

  const [submittedCode, setSubmittedCode] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleParseNLP = async () => {
    if (!nlText.trim()) return;
    setParsing(true);
    try {
      const parsed = await api.parseNLP(nlText);
      setAiUnderstanding(parsed);
      setLocationName(parsed.extracted_location);
      setAffectedPeople(parsed.affected_people);
      setAffectedHouseholds(parsed.affected_households);
      setVulnerableElderly(parsed.vulnerable_elderly);
      setVulnerableChildren(parsed.vulnerable_children);
      setUrgency(parsed.urgency);
      if (parsed.items.length > 0) {
        setItems(parsed.items);
      }
      showNotification('AI parsed your description into structured relief requirements.', 'success');
    } catch (err) {
      showNotification('Failed to parse text with AI', 'error');
    } finally {
      setParsing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.createRequest({
        location_name: locationName,
        latitude: aiUnderstanding?.latitude || 14.5230,
        longitude: aiUnderstanding?.longitude || 75.3120,
        affected_people: Number(affectedPeople),
        affected_households: Number(affectedHouseholds),
        vulnerable_elderly: Number(vulnerableElderly),
        vulnerable_children: Number(vulnerableChildren),
        urgency: urgency,
        raw_description: nlText,
        reporter_name: reporterName,
        reporter_phone: reporterPhone,
        items: items.map(it => ({
          category: it.category,
          item_name: it.item_name,
          requested_quantity: Number(it.quantity),
          unit: it.unit
        }))
      });

      setSubmittedCode(res.tracking_code);
      showNotification(`Request ${res.tracking_code} submitted! Prioritized with score ${res.priority_score}/100.`, 'success');
    } catch (err) {
      showNotification('Failed to submit relief request', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (submittedCode) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="bg-ivory border border-slate/20 rounded-2xl p-8 shadow-elevated">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-status-fulfilled flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-extrabold text-navy">Relief Request Logged Successfully</h2>
          <p className="text-slate text-sm mt-2">
            Your emergency report has been routed to the State Emergency Operations Center and nearby depots.
          </p>

          <div className="my-6 p-4 bg-ivory-100 rounded-xl border border-slate/20 inline-block">
            <div className="text-xs uppercase tracking-wider text-slate font-semibold">Your Request Tracking Code</div>
            <div className="text-3xl font-mono font-extrabold text-terracotta mt-1">{submittedCode}</div>
          </div>

          <div className="flex justify-center gap-3">
            <button
              onClick={() => { setSubmittedCode(null); }}
              className="bg-ivory border border-slate/30 text-navy font-semibold px-4 py-2 rounded-lg text-xs hover:bg-slate/10"
            >
              Report Another Need
            </button>
            <button
              onClick={() => setActiveTab('command')}
              className="bg-navy hover:bg-navy-800 text-white font-semibold px-4 py-2 rounded-lg text-xs"
            >
              View Operations Map
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Page Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
          Report a Flood Relief Need
        </h1>
        <p className="text-xs sm:text-sm text-slate mt-1">
          Designed for high-stress emergency communication. Describe in your natural words or fill the structured form.
        </p>
      </div>

      {/* Step 1: Natural Language AI Description Field */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-bold text-navy flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-terracotta" />
            <span>Describe the Situation Naturally</span>
          </label>
          <span className="text-xs text-slate">AI extracts locations, population, & supplies</span>
        </div>

        <textarea
          rows={3}
          value={nlText}
          onChange={e => setNlText(e.target.value)}
          placeholder="e.g. Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children."
          className="w-full bg-white border border-slate/30 rounded-lg p-3 text-xs sm:text-sm text-navy focus:outline-none focus:border-terracotta shadow-inner"
        />

        <div className="mt-3 flex items-center justify-between">
          <div className="text-[11px] text-slate italic">
            Example: Mention village name, stranded count, vulnerable people, and critical supplies.
          </div>
          <button
            type="button"
            onClick={handleParseNLP}
            disabled={parsing}
            className="bg-navy hover:bg-navy-800 text-white font-semibold px-4 py-2 rounded-lg text-xs flex items-center space-x-1.5 shadow-sm transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5 text-terracotta" />
            <span>{parsing ? 'Parsing with AI...' : 'Parse with AI'}</span>
          </button>
        </div>

        {/* Live AI Understanding Box */}
        {aiUnderstanding && (
          <div className="mt-4 p-4 bg-terracotta-50 border border-terracotta/30 rounded-lg text-xs animate-in fade-in">
            <div className="font-bold text-navy flex items-center justify-between mb-1.5">
              <span className="text-terracotta uppercase tracking-wider text-[11px]">AI UNDERSTANDING</span>
              <span className="text-slate font-mono text-[10px]">Confidence: {Math.round(aiUnderstanding.confidence_score * 100)}%</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-dark">
              <div>Location: <b>{aiUnderstanding.extracted_location}</b></div>
              <div>Affected: <b>{aiUnderstanding.affected_people} people</b></div>
              <div>Vulnerable: <b>{aiUnderstanding.vulnerable_total} people</b></div>
              <div>Urgency: <b className="text-red-700">{aiUnderstanding.urgency}</b></div>
            </div>
            <div className="mt-2 text-[11px] text-slate border-t border-terracotta/20 pt-1.5">
              <b>Identified Supplies:</b> {aiUnderstanding.items.map(i => `${i.quantity} ${i.unit} ${i.category}`).join(', ')}
            </div>
          </div>
        )}
      </div>

      {/* Step 2: Editable Form Details */}
      <form onSubmit={handleSubmit} className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft space-y-6">
        <h3 className="font-bold text-base text-navy pb-2 border-b border-slate/15 flex items-center gap-2">
          <Edit2 className="w-4 h-4 text-terracotta" />
          <span>Confirm & Refine Request Details</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-dark mb-1">Affected Location / Village Name</label>
            <input
              type="text"
              value={locationName}
              onChange={e => setLocationName(e.target.value)}
              required
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-medium"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Assessed Urgency Level</label>
            <select
              value={urgency}
              onChange={e => setUrgency(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-semibold"
            >
              <option value="CRITICAL">CRITICAL (Immediate Life Threat)</option>
              <option value="HIGH">HIGH (Urgent Assistance Required)</option>
              <option value="MEDIUM">MEDIUM (Stable / Need Support)</option>
              <option value="LOW">LOW (Monitoring / Non-critical)</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Total Stranded / Affected People</label>
            <input
              type="number"
              value={affectedPeople}
              onChange={e => setAffectedPeople(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Households Affected</label>
            <input
              type="number"
              value={affectedHouseholds}
              onChange={e => setAffectedHouseholds(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Elderly Individuals (High Risk)</label>
            <input
              type="number"
              value={vulnerableElderly}
              onChange={e => setVulnerableElderly(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Children & Infants</label>
            <input
              type="number"
              value={vulnerableChildren}
              onChange={e => setVulnerableChildren(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Reporter / Coordinator Name</label>
            <input
              type="text"
              value={reporterName}
              onChange={e => setReporterName(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Contact Phone Number</label>
            <input
              type="text"
              value={reporterPhone}
              onChange={e => setReporterPhone(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>
        </div>

        {/* Items List */}
        <div>
          <label className="block font-bold text-navy text-xs mb-2">Requested Supplies</label>
          <div className="space-y-2">
            {items.map((it, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs">
                <input
                  type="text"
                  value={it.category}
                  readOnly
                  className="w-1/3 bg-ivory-100 border border-slate/20 rounded px-2.5 py-1.5 font-medium text-navy"
                />
                <input
                  type="text"
                  value={it.item_name}
                  onChange={e => {
                    const newItems = [...items];
                    newItems[idx].item_name = e.target.value;
                    setItems(newItems);
                  }}
                  className="flex-1 bg-white border border-slate/30 rounded px-2.5 py-1.5 text-navy"
                />
                <input
                  type="number"
                  value={it.quantity}
                  onChange={e => {
                    const newItems = [...items];
                    newItems[idx].quantity = Number(e.target.value);
                    setItems(newItems);
                  }}
                  className="w-24 bg-white border border-slate/30 rounded px-2.5 py-1.5 text-navy font-bold"
                />
                <span className="w-16 text-slate font-medium">{it.unit}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t border-slate/20 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-3 rounded-lg shadow-card text-xs sm:text-sm flex items-center space-x-2 transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>{submitting ? 'Submitting to Emergency Operations...' : 'Submit Emergency Request'}</span>
          </button>
        </div>
      </form>

    </div>
  );
};
"""
write_file("pages/CommunityReportPage.tsx", report_code)

# 2. TraceReliefPage.tsx
trace_code = """import React, { useEffect, useState } from 'react';
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
"""
write_file("pages/TraceReliefPage.tsx", trace_code)

# 3. NgoWarehousePage.tsx
wh_code = """import React, { useEffect, useState } from 'react';
import { InventoryItem } from '../types';
import api from '../services/api';
import { Warehouse, AlertTriangle, Clock, CheckCircle2, ShieldAlert, Package, RefreshCw } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export const NgoWarehousePage: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getInventory(),
      api.getInventoryAlerts()
    ]).then(([invData, alertData]) => {
      setInventory(invData);
      setAlerts(alertData);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate/20 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
            <Warehouse className="w-7 h-7 text-terracotta" />
            <span>Warehouses & NGO Inventory Hub</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate mt-1">
            Real-time batch visibility, FEFO expiration tracking, and multi-depot stock coordination
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Alerts Row: Low Stock & Expiring Batches */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-bold text-navy uppercase tracking-wider flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-status-critical" />
            <span>Critical Inventory Alerts & Batch Expirations</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.map((al, idx) => (
              <div key={idx} className="bg-amber-50/70 border border-amber-200 rounded-lg p-3 text-xs flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-navy">{al.warehouse} &bull; {al.item}</div>
                  <div className="text-slate-dark text-[11px] mt-0.5">{al.message}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inventory Grid Table */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-3">Depot Stock Levels & Allocations</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
              <tr>
                <th className="py-2.5 px-3">Depot</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Item Name</th>
                <th className="py-2.5 px-3">Total In Stock</th>
                <th className="py-2.5 px-3">Allocated</th>
                <th className="py-2.5 px-3">Available</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/15">
              {inventory.map(item => (
                <tr key={item.id} className="hover:bg-ivory-50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-navy">{item.warehouse_name}</td>
                  <td className="py-3 px-3 text-slate">{item.category}</td>
                  <td className="py-3 px-3 font-bold text-navy">{item.item_name}</td>
                  <td className="py-3 px-3 font-mono">{item.total_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3 font-mono text-terracotta">{item.allocated_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3 font-mono font-bold text-status-fulfilled">{item.available_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3">
                    <StatusBadge status={item.status} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
"""
write_file("pages/NgoWarehousePage.tsx", wh_code)

print("CommunityReportPage, TraceReliefPage, NgoWarehousePage written successfully.")
