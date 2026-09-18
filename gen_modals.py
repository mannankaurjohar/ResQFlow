from helper_writer import write_file

# 1. GisMap.tsx
gismap_code = """import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { GisOverviewData } from '../types';
import api from '../services/api';
import { useApp } from '../context/AppContext';
import { Layers } from 'lucide-react';

interface GisMapProps {
  height?: string;
  onSelectRequest?: (req: any) => void;
  highlightLocation?: string;
}

export const GisMap: React.FC<GisMapProps> = ({ height = '560px' }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupsRef = useRef<{ [key: string]: L.LayerGroup }>({});

  const [gisData, setGisData] = useState<GisOverviewData | null>(null);
  const [layers, setLayers] = useState({
    zones: true,
    requests: true,
    warehouses: true,
    reliefCenters: true,
    deliveries: true,
    blockedRoads: true
  });

  const { setActiveMatchModalRequest } = useApp();

  useEffect(() => {
    api.getGisOverview().then(data => setGisData(data)).catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [14.515, 75.315],
        zoom: 12,
        zoomControl: true
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO &copy; OpenStreetMap',
        maxZoom: 18,
        subdomains: 'abcd'
      }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupsRef.current = {
        zones: L.layerGroup().addTo(map),
        requests: L.layerGroup().addTo(map),
        warehouses: L.layerGroup().addTo(map),
        reliefCenters: L.layerGroup().addTo(map),
        deliveries: L.layerGroup().addTo(map),
        blockedRoads: L.layerGroup().addTo(map)
      };
    }
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !gisData) return;
    const { zones, requests, warehouses, relief_centers, deliveries, blocked_roads } = gisData;
    const groups = layerGroupsRef.current;

    if (groups.zones) {
      groups.zones.clearLayers();
      if (layers.zones) {
        zones.forEach(zone => {
          if (zone.polygon && zone.polygon.length > 0) {
            const isSevere = zone.severity_level === 'SEVERE' || zone.severity_level === 'CRITICAL';
            const color = isSevere ? '#DC2626' : '#EA580C';
            const poly = L.polygon(zone.polygon as [number, number][], {
              color: color,
              weight: 2,
              opacity: 0.85,
              fillColor: color,
              fillOpacity: isSevere ? 0.28 : 0.16,
              dashArray: isSevere ? '4, 4' : undefined
            });
            poly.bindPopup(`
              <div class="p-2 text-xs">
                <div class="font-bold text-sm text-navy mb-1">${zone.name}</div>
                <div class="mb-1">Water Level: <b>${zone.water_level_meters}m</b> (${zone.severity_level})</div>
                <div class="text-slate-dark">Population: <b>${zone.population.toLocaleString()}</b> across <b>${zone.households}</b> households.</div>
              </div>
            `);
            poly.addTo(groups.zones);
          }
        });
      }
    }

    if (groups.requests) {
      groups.requests.clearLayers();
      if (layers.requests) {
        requests.forEach(req => {
          const isCrit = req.priority_classification === 'CRITICAL' || req.priority_score >= 80;
          const isDelivered = req.status === 'DELIVERED';
          const markerColor = isDelivered ? '#059669' : isCrit ? '#DC2626' : '#EA580C';

          const iconHtml = `<div style="background-color: ${markerColor}; width: 26px; height: 26px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-size: 11px; font-weight: bold;">${isDelivered ? '✓' : Math.round(req.priority_score || 50)}</div>`;
          const customIcon = L.divIcon({ html: iconHtml, className: 'req-icon', iconSize: [26, 26], iconAnchor: [13, 13] });
          const marker = L.marker([req.lat, req.lon], { icon: customIcon });

          marker.bindPopup(`
            <div class="p-2.5 text-xs min-w-[210px]">
              <div class="font-bold text-sm text-navy uppercase">${req.location_name}</div>
              <div class="text-xs text-terracotta font-semibold mb-1">${req.priority_classification} (${Math.round(req.priority_score)}/100)</div>
              <div class="text-slate-dark mb-2">Affected: <b>${req.affected_people} people</b> &bull; Status: <b>${req.status}</b></div>
              <button onclick="window.__openMatchModal && window.__openMatchModal(${req.id})" class="bg-terracotta hover:bg-terracotta-hover text-white px-3 py-1 rounded text-xs font-semibold w-full">
                Match Resources
              </button>
            </div>
          `);
          marker.addTo(groups.requests);
        });
      }
    }

    if (groups.warehouses) {
      groups.warehouses.clearLayers();
      if (layers.warehouses) {
        warehouses.forEach(wh => {
          const iconHtml = `<div style="background-color: #0F1E36; width: 28px; height: 28px; border-radius: 6px; border: 2px solid #FDFBF7; display: flex; align-items: center; justify-content: center; font-size: 14px;">📦</div>`;
          const whIcon = L.divIcon({ html: iconHtml, className: 'wh-icon', iconSize: [28, 28], iconAnchor: [14, 14] });
          const marker = L.marker([wh.lat, wh.lon], { icon: whIcon });
          marker.bindPopup(`<div class="p-2 text-xs"><div class="font-bold text-navy">${wh.name}</div><div class="text-slate">Capacity: ${wh.capacity_sqm} m²</div></div>`);
          marker.addTo(groups.warehouses);
        });
      }
    }

    if (groups.deliveries) {
      groups.deliveries.clearLayers();
      if (layers.deliveries) {
        deliveries.forEach(del => {
          if (del.waypoints && del.waypoints.length > 1) {
            const latlngs = del.waypoints.map((wp: any) => [wp.lat, wp.lon] as [number, number]);
            const isDelivered = del.status === 'DELIVERED';
            L.polyline(latlngs, {
              color: isDelivered ? '#059669' : '#0284C7',
              weight: 3.5,
              opacity: 0.85,
              dashArray: isDelivered ? undefined : '6, 6'
            }).addTo(groups.deliveries);
          }
        });
      }
    }

    if (groups.blockedRoads) {
      groups.blockedRoads.clearLayers();
      if (layers.blockedRoads) {
        blocked_roads.forEach(road => {
          const warnIcon = L.divIcon({
            html: `<div style="background: #B91C1C; color: white; width: 22px; height: 22px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">⛔</div>`,
            className: 'road-icon',
            iconSize: [22, 22],
            iconAnchor: [11, 11]
          });
          L.marker([road.lat, road.lon], { icon: warnIcon })
            .bindPopup(`<div class="p-1.5 text-xs"><b class="text-red-700">${road.name}</b><div>${road.reason}</div></div>`)
            .addTo(groups.blockedRoads);
        });
      }
    }

    (window as any).__openMatchModal = (reqId: number) => {
      api.getRequestById(reqId).then(req => setActiveMatchModalRequest(req));
    };
  }, [gisData, layers]);

  return (
    <div className="relative rounded-xl overflow-hidden border border-slate/20 shadow-soft bg-ivory">
      <div ref={mapContainerRef} style={{ height, width: '100%' }} />
      <div className="absolute top-3 right-3 z-[1000] bg-ivory/95 backdrop-blur-sm border border-slate/30 p-2.5 rounded-lg shadow-card text-xs">
        <div className="flex items-center space-x-1.5 font-bold text-navy mb-2 pb-1 border-b border-slate/20">
          <Layers className="w-3.5 h-3.5 text-terracotta" />
          <span>GIS Layers</span>
        </div>
        <div className="space-y-1.5">
          <label className="flex items-center space-x-2 cursor-pointer text-slate-dark">
            <input type="checkbox" checked={layers.zones} onChange={e => setLayers({ ...layers, zones: e.target.checked })} className="rounded text-terracotta" />
            <span>Flood Inundation Zones</span>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer text-slate-dark">
            <input type="checkbox" checked={layers.requests} onChange={e => setLayers({ ...layers, requests: e.target.checked })} className="rounded text-terracotta" />
            <span>Community Needs</span>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer text-slate-dark">
            <input type="checkbox" checked={layers.warehouses} onChange={e => setLayers({ ...layers, warehouses: e.target.checked })} className="rounded text-terracotta" />
            <span>Depots & Warehouses</span>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer text-slate-dark">
            <input type="checkbox" checked={layers.deliveries} onChange={e => setLayers({ ...layers, deliveries: e.target.checked })} className="rounded text-terracotta" />
            <span>Active Convoys</span>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer text-slate-dark">
            <input type="checkbox" checked={layers.blockedRoads} onChange={e => setLayers({ ...layers, blockedRoads: e.target.checked })} className="rounded text-terracotta" />
            <span>Inundated Roads</span>
          </label>
        </div>
      </div>
    </div>
  );
};
"""
write_file("components/GisMap.tsx", gismap_code)

# 2. ExplainPriorityModal.tsx
explain_code = """import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { ExplainPriorityResponse } from '../types';
import api from '../services/api';
import { X, ShieldAlert, Sliders, Info, Edit3 } from 'lucide-react';

export const ExplainPriorityModal: React.FC = () => {
  const { activePriorityModalRequest, setActivePriorityModalRequest, showNotification } = useApp();
  const [explanation, setExplanation] = useState<ExplainPriorityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [overrideMode, setOverrideMode] = useState(false);
  const [overrideScore, setOverrideScore] = useState(85);
  const [overrideReason, setOverrideReason] = useState('');

  useEffect(() => {
    if (!activePriorityModalRequest) return;
    setLoading(true);
    api.getPriorityExplanation(activePriorityModalRequest.id)
      .then(data => {
        setExplanation(data);
        setOverrideScore(data.priority_score);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [activePriorityModalRequest]);

  if (!activePriorityModalRequest) return null;

  const handleOverride = async () => {
    if (!overrideReason.trim()) {
      showNotification('Please provide a documented justification for the authority override.', 'error');
      return;
    }
    try {
      const updated = await api.overridePriority(activePriorityModalRequest.id, overrideScore, overrideReason);
      setExplanation(updated);
      setOverrideMode(false);
      showNotification(`Priority successfully overridden to ${overrideScore}/100. Audited in tamper-evident ledger.`, 'success');
    } catch (err) {
      showNotification('Failed to record override', 'error');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
      <div className="bg-ivory rounded-xl border border-slate/20 shadow-elevated w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="bg-navy text-ivory px-6 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-terracotta" />
              <h3 className="font-bold text-base">Explainable AI Priority Engine</h3>
            </div>
            <p className="text-xs text-slate-light mt-0.5">
              Transparent multi-factor humanitarian scoring audit
            </p>
          </div>
          <button onClick={() => setActivePriorityModalRequest(null)} className="text-slate-light hover:text-ivory rounded p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {loading || !explanation ? (
            <div className="py-12 text-center text-slate">Calculating multi-factor decision matrix...</div>
          ) : (
            <div>
              <div className="flex items-center justify-between bg-ivory-100 border border-slate/20 rounded-lg p-4 mb-5">
                <div>
                  <div className="text-xs uppercase tracking-wider text-slate font-semibold">
                    Calculated Urgency Level
                  </div>
                  <div className="text-2xl font-extrabold text-navy flex items-center gap-2 mt-0.5">
                    <span>{explanation.priority_classification}</span>
                    <span className="text-sm font-bold text-terracotta bg-terracotta/10 border border-terracotta/20 px-2 py-0.5 rounded">
                      {explanation.priority_score} / 100
                    </span>
                  </div>
                  <div className="text-xs text-slate mt-1">
                    Request ID: <span className="font-mono font-medium text-navy">{explanation.tracking_code}</span> ({activePriorityModalRequest.location_name})
                  </div>
                </div>

                <div className="text-right">
                  {explanation.authority_override_score ? (
                    <div className="text-[11px] bg-amber-50 text-amber-900 border border-amber-300 px-2 py-1 rounded max-w-[170px]">
                      <b>Authority Override:</b> {explanation.authority_override_score} pts by {explanation.override_by || 'Command'}
                    </div>
                  ) : (
                    <button
                      onClick={() => setOverrideMode(!overrideMode)}
                      className="text-xs font-semibold text-terracotta hover:text-terracotta-hover flex items-center gap-1 border border-terracotta/30 bg-terracotta/5 px-2.5 py-1.5 rounded-md"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>Override Score</span>
                    </button>
                  )}
                </div>
              </div>

              <h4 className="text-xs font-bold uppercase tracking-wider text-navy mb-2.5 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-slate" />
                <span>Transparent Point Contributions</span>
              </h4>

              <div className="space-y-2 mb-5">
                {explanation.factors.map((f, idx) => (
                  <div key={idx} className="flex items-start justify-between bg-white border border-slate/15 rounded-md p-2.5 text-xs">
                    <div className="pr-3">
                      <div className="font-semibold text-navy">{f.factor}</div>
                      <div className="text-slate-dark text-[11px] mt-0.5">{f.reason}</div>
                    </div>
                    <span className="font-mono font-bold text-terracotta bg-terracotta/10 px-2 py-0.5 rounded shrink-0">
                      +{f.points} pts
                    </span>
                  </div>
                ))}
              </div>

              {overrideMode && (
                <div className="bg-amber-50/70 border border-amber-200 rounded-lg p-3.5 mb-4 text-xs">
                  <div className="font-bold text-amber-950 mb-2 flex items-center gap-1.5">
                    <Sliders className="w-4 h-4 text-amber-700" />
                    <span>Command Authority Override (Audited)</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 mb-2">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-dark mb-1">New Score (0-100)</label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={overrideScore}
                        onChange={e => setOverrideScore(Number(e.target.value))}
                        className="w-full bg-white border border-slate/30 rounded px-2.5 py-1 text-navy font-bold"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[11px] font-medium text-slate-dark mb-1">Mandatory Operational Justification</label>
                      <input
                        type="text"
                        placeholder="e.g. Field scouts report road collapse; immediate life hazard."
                        value={overrideReason}
                        onChange={e => setOverrideReason(e.target.value)}
                        className="w-full bg-white border border-slate/30 rounded px-2.5 py-1 text-navy"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 mt-2">
                    <button onClick={() => setOverrideMode(false)} className="px-2.5 py-1 text-slate hover:text-navy">Cancel</button>
                    <button onClick={handleOverride} className="bg-navy hover:bg-navy-800 text-white font-semibold px-3 py-1 rounded">Confirm & Sign Ledger</button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="bg-ivory-100 px-6 py-3 border-t border-slate/20 flex justify-end">
          <button onClick={() => setActivePriorityModalRequest(null)} className="bg-navy hover:bg-navy-800 text-white font-semibold text-xs px-4 py-2 rounded-md">
            Close Audit Card
          </button>
        </div>
      </div>
    </div>
  );
};
"""
write_file("components/ExplainPriorityModal.tsx", explain_code)

# 3. AiMatchingModal.tsx
matching_code = """import React, { useEffect, useState } from 'react';
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
"""
write_file("components/AiMatchingModal.tsx", matching_code)

print("Modals created successfully.")
