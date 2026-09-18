from helper_writer import write_file

# 1. LandingPage.tsx
landing_code = """import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Waves, Radio, FileText, Search, ArrowRight, ShieldCheck,
  Cpu, MapPin, Truck, CheckCircle2, AlertTriangle, Eye, Compass
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { setActiveTab, setTraceIdInput, triggerEscalation, isEscalated } = useApp();
  const [searchInput, setSearchInput] = useState('RELIEF-2026-00482');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setTraceIdInput(searchInput.trim());
      setActiveTab('trace');
    }
  };

  return (
    <div className="space-y-16 pb-12">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 bg-gradient-to-b from-navy to-navy-900 text-ivory rounded-2xl shadow-elevated px-6 sm:px-12 mx-auto max-w-7xl mt-4 border border-navy-700">
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#D97450_1px,transparent_1px)] [background-size:24px_24px]"></div>
        
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-navy-800 border border-slate/30 px-3 py-1 rounded-full text-xs font-semibold text-slate-light mb-6">
            <span className="w-2 h-2 rounded-full bg-terracotta animate-pulse"></span>
            <span>Active Flood Response Coordination System</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-ivory font-sans leading-tight">
            RESQFLOW AI
          </h1>
          <p className="text-xl sm:text-2xl font-medium text-terracotta mt-2">
            From community needs to verified relief delivery.
          </p>

          <p className="text-base sm:text-lg text-slate-light mt-4 leading-relaxed font-normal">
            An AI-powered flood-relief coordination platform that identifies urgent community needs,
            intelligently connects them with available resources, and provides transparent end-to-end relief tracking.
          </p>

          {/* Primary Action Buttons */}
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              onClick={() => setActiveTab('command')}
              className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <Radio className="w-4 h-4" />
              <span>View Relief Operations</span>
            </button>
            <button
              onClick={() => setActiveTab('report')}
              className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <FileText className="w-4 h-4 text-terracotta" />
              <span>Report a Need</span>
            </button>
          </div>

          {/* Direct Relief Tracker Quick Bar */}
          <div className="mt-10 pt-8 border-t border-navy-800 max-w-xl">
            <div className="text-xs font-semibold text-slate-light uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5 text-terracotta" />
              <span>Transparent Relief Package Tracker</span>
            </div>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                placeholder="Enter Relief ID (e.g. RELIEF-2026-00482 or D-10284)"
                className="flex-1 bg-navy-800 border border-slate/40 text-ivory placeholder-slate rounded-lg px-4 py-2.5 text-xs sm:text-sm font-mono focus:outline-none focus:border-terracotta"
              />
              <button
                type="submit"
                className="bg-navy-700 hover:bg-terracotta text-ivory font-bold px-4 py-2.5 rounded-lg text-xs transition-colors shrink-0"
              >
                Track Journey
              </button>
            </form>
            <p className="text-[11px] text-slate mt-1.5">
              Public verification: Try demo signature ID <b>RELIEF-2026-00482</b> (500 Water Bottles &bull; Zone B)
            </p>
          </div>

        </div>
      </section>

      {/* Operational Impact Metrics */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate">People Assisted</div>
            <div className="text-3xl font-extrabold text-navy mt-1">35,420+</div>
            <div className="text-xs text-status-fulfilled font-medium mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Across 5 flood sectors
            </div>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate">Critical Fulfillment</div>
            <div className="text-3xl font-extrabold text-navy mt-1">94.2%</div>
            <div className="text-xs text-slate mt-1">Within 4 hours average</div>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate">Clean Water Moved</div>
            <div className="text-3xl font-extrabold text-terracotta mt-1">18,500 L</div>
            <div className="text-xs text-slate mt-1">Verified community handovers</div>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate">Ledger Integrity</div>
            <div className="text-3xl font-extrabold text-navy mt-1">100%</div>
            <div className="text-xs text-emerald-700 font-medium mt-1 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> SHA-256 Chained Hash
            </div>
          </div>
        </div>
      </section>

      {/* 5 Core Questions Answered Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
            Answering Five Questions Immediately
          </h2>
          <p className="text-slate text-sm mt-2">
            The system connects community needs directly with physical response capacity without delays or duplicate confusion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">1</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHO needs help?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Identifies stranded populations and vulnerable demographics (elderly, infants, pregnant mothers).
            </p>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">2</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHAT do they need?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Extracts precise quantities of drinking water, rations, first aid, baby care, or thermal shelter.
            </p>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-terracotta text-white flex items-center justify-center font-bold text-xs mb-3">3</div>
            <h3 className="font-bold text-sm text-navy mb-1">HOW URGENT is it?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Explainable AI priority engine calculates transparent 0-100 scores with audited factor points.
            </p>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">4</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHERE from?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Multi-objective AI matching analyzes warehouse proximity, batch expiry, and flooded road bypasses.
            </p>
          </div>
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs mb-3">5</div>
            <h3 className="font-bold text-sm text-navy mb-1">HAS IT REACHED?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              End-to-end transparent delivery tracking with verified digital handover signature & photo proof.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Flow */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="bg-ivory-100 border border-slate/20 rounded-2xl p-8 shadow-card">
          <div className="text-center max-w-xl mx-auto mb-8">
            <h3 className="text-xl font-bold text-navy">The End-to-End Humanitarian Pipeline</h3>
            <p className="text-xs text-slate mt-1">From community distress voice to sealed proof of delivery</p>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center">
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 1</div>
              <div className="font-semibold text-navy text-sm">Natural Need Report</div>
              <div className="text-[11px] text-slate mt-0.5">AI entity parsing</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 2</div>
              <div className="font-semibold text-navy text-sm">AI Prioritization</div>
              <div className="text-[11px] text-slate mt-0.5">Explainable points matrix</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 3</div>
              <div className="font-semibold text-navy text-sm">Resource Matching</div>
              <div className="text-[11px] text-slate mt-0.5">Depots & capacity</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 4</div>
              <div className="font-semibold text-navy text-sm">Human Approval</div>
              <div className="text-[11px] text-slate mt-0.5">Authority manifest lock</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 5</div>
              <div className="font-semibold text-navy text-sm">Delivery & Trace</div>
              <div className="text-[11px] text-slate mt-0.5">8-step transparent journey</div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
"""
write_file("pages/LandingPage.tsx", landing_code)

# 2. AuthorityCommandPage.tsx
command_code = """import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { GisMap } from '../components/GisMap';
import { StatusBadge } from '../components/StatusBadge';
import { CommunityRequest, AnalyticsData } from '../types';
import api from '../services/api';
import {
  Radio, ShieldAlert, Cpu, AlertTriangle, CheckCircle, Clock,
  ArrowRight, Sliders, ExternalLink, RefreshCw, Box
} from 'lucide-react';

export const AuthorityCommandPage: React.FC = () => {
  const {
    isEmergencyMode, isEscalated, triggerEscalation, triggerReset,
    setActivePriorityModalRequest, setActiveMatchModalRequest, showNotification
  } = useApp();

  const [requests, setRequests] = useState<CommunityRequest[]>([]);
  const [shortages, setShortages] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadAll = () => {
    setLoading(true);
    Promise.all([
      api.getRequests(),
      api.getShortages(),
      api.getAnalytics()
    ]).then(([reqData, shortData, analData]) => {
      setRequests(reqData);
      setShortages(shortData);
      setAnalytics(analData);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
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
            {isEscalated ? '⚡ Flood Escalation Active' : 'Simulate Flood Escalation'}
          </button>

          <button
            onClick={() => { triggerReset(); loadAll(); }}
            className="p-1.5 text-slate hover:text-navy border border-slate/30 rounded-md bg-ivory"
            title="Reset simulation to baseline"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Top Metric Cards (6 Operational KPIs) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">People Affected</div>
          <div className="text-2xl font-extrabold text-navy mt-1">
            {analytics?.people_affected.toLocaleString() || '1,420'}
          </div>
          <div className="text-[10px] text-slate mt-0.5">Across inundated zones</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-critical uppercase tracking-wider">Critical Requests</div>
          <div className="text-2xl font-extrabold text-status-critical mt-1">
            {analytics?.critical_requests_pending || '4'}
          </div>
          <div className="text-[10px] text-red-600 font-medium mt-0.5">Requiring action</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">Pending Triage</div>
          <div className="text-2xl font-extrabold text-navy mt-1">
            {requests.filter(r => r.status === 'PENDING').length}
          </div>
          <div className="text-[10px] text-slate mt-0.5">Unallocated needs</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-slate uppercase tracking-wider">Fulfillment Rate</div>
          <div className="text-2xl font-extrabold text-status-fulfilled mt-1">
            {analytics?.fulfillment_rate_pct || '84.6'}%
          </div>
          <div className="text-[10px] text-slate mt-0.5">Overall requests met</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-high uppercase tracking-wider">Critical Shortages</div>
          <div className="text-2xl font-extrabold text-status-high mt-1">
            {shortages.length}
          </div>
          <div className="text-[10px] text-orange-600 font-medium mt-0.5">Water & medical deficits</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-3.5 shadow-soft">
          <div className="text-[11px] font-semibold text-status-transit uppercase tracking-wider">Active Convoys</div>
          <div className="text-2xl font-extrabold text-status-transit mt-1">
            {analytics?.active_deliveries || '3'}
          </div>
          <div className="text-[10px] text-sky-700 font-medium mt-0.5">En route to shelters</div>
        </div>
      </div>

      {/* Main Area: Large GIS Leaflet Map */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-dark px-1">
          <span className="font-bold text-navy uppercase tracking-wider">
            Interactive GIS Inundation & Logistics Map
          </span>
          <span>Click any village marker or flood polygon to inspect</span>
        </div>
        <GisMap height="520px" />
      </div>

      {/* Two-Column Lower Section: Priority Queue & Shortage Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Priority Requests Queue (7 cols) */}
        <div className="lg:col-span-7 bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">
            <div>
              <h3 className="font-bold text-base text-navy">Priority Relief Requests</h3>
              <p className="text-xs text-slate">Ranked automatically by explainable AI scoring</p>
            </div>
            <span className="text-xs font-semibold text-terracotta bg-terracotta/10 px-2.5 py-1 rounded">
              {requests.length} Total Requests
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
                <tr>
                  <th className="py-2.5 px-3">Location / ID</th>
                  <th className="py-2.5 px-3">Affected</th>
                  <th className="py-2.5 px-3">AI Priority</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate/15">
                {requests.slice(0, 7).map(req => {
                  const isCrit = req.priority_classification === 'CRITICAL' || req.priority_score >= 80;
                  return (
                    <tr key={req.id} className={`hover:bg-ivory-50 transition-colors ${isCrit && req.status === 'PENDING' ? 'bg-red-50/40' : ''}`}>
                      <td className="py-3 px-3">
                        <div className="font-bold text-navy">{req.location_name}</div>
                        <div className="text-[10px] font-mono text-slate">{req.tracking_code}</div>
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-semibold text-slate-dark">{req.affected_people} people</div>
                        <div className="text-[10px] text-slate">
                          {(req.vulnerable_elderly || 0) + (req.vulnerable_children || 0)} vulnerable
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`font-mono font-bold px-1.5 py-0.5 rounded text-[11px] ${isCrit ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'}`}>
                            {Math.round(req.priority_score)}/100
                          </span>
                          <button
                            onClick={() => setActivePriorityModalRequest(req)}
                            className="text-[10px] text-slate hover:text-terracotta underline ml-1"
                          >
                            Explain
                          </button>
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <StatusBadge status={req.status} size="sm" />
                      </td>
                      <td className="py-3 px-3 text-right">
                        {req.status === 'PENDING' || req.status === 'VERIFIED' ? (
                          <button
                            onClick={() => setActiveMatchModalRequest(req)}
                            className="bg-terracotta hover:bg-terracotta-hover text-white px-2.5 py-1 rounded text-[11px] font-semibold transition-colors"
                          >
                            Match AI
                          </button>
                        ) : (
                          <span className="text-[11px] text-slate">Locked</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Shortage Radar & Emergency Supply Deficit (5 cols) */}
        <div className="lg:col-span-5 bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate/15">
            <div>
              <h3 className="font-bold text-base text-navy">Shortage Radar</h3>
              <p className="text-xs text-slate">Automatic detection of critical regional deficits</p>
            </div>
            <span className="text-xs font-bold text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
              DEFICITS
            </span>
          </div>

          <div className="space-y-3">
            {shortages.map(item => (
              <div key={item.id} className="bg-white border border-slate/20 rounded-lg p-3.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-navy">{item.sector}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-100 text-red-800">
                    SHORTAGE: -{item.shortage.toLocaleString()} {item.unit}
                  </span>
                </div>
                <div className="text-[11px] text-slate mt-0.5">
                  Category: <b>{item.category}</b> &bull; {item.zone}
                </div>
                <div className="mt-2 text-[11px] text-slate-dark border-t border-slate/15 pt-2">
                  <div className="font-semibold mb-1">Potential Sourcing Depots:</div>
                  <ul className="space-y-0.5">
                    {item.potential_sources.map((src: any, sIdx: number) => (
                      <li key={sIdx} className="flex justify-between text-[11px]">
                        <span>{src.name} ({src.distance_km} km):</span>
                        <b>{src.stock.toLocaleString()} {item.unit} avail</b>
                      </li>
                    ))}
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
"""
write_file("pages/AuthorityCommandPage.tsx", command_code)

print("LandingPage and AuthorityCommandPage written successfully.")
