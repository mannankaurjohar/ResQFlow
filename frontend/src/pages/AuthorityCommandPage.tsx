import React, { useEffect, useState } from 'react';
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

          <div className="overflow-x-auto overflow-y-auto max-h-[430px]">
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
                {requests.map(req => {
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
