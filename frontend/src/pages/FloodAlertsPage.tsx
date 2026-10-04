import React, { useEffect, useMemo, useRef, useState } from 'react';
import L from 'leaflet';
import {
  AlertTriangle,
  MapPin,
  RefreshCw,
  Search,
  Waves,
  Activity,
  Filter
} from 'lucide-react';
import api from '../services/api';
import 'leaflet/dist/leaflet.css';

interface FloodAlert {
  station: string;
  river: string;
  district: string;
  state: string;
  latitude: string;
  longitude: string;
  condition: string;
  alert_level: string;
  current_level: string;
  warning_level: string;
  danger_level: string;
  forecast_date: string;
  forecast_level: string;
  source: string;
}

const FloodAlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<FloodAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [conditionFilter, setConditionFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markersLayer = useRef<L.LayerGroup | null>(null);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError('');

      const data = await api.getFloodAlerts();
      setAlerts(data || []);
    } catch (err) {
      setError('Unable to load live CWC flood data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();

    const interval = setInterval(
      loadAlerts,
      5 * 60 * 1000
    );

    return () => clearInterval(interval);
  }, []);

  /* ================= MAP ================= */

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    const map = L.map(mapRef.current, {
      zoomControl: true,
      minZoom: 4,
      maxZoom: 12
    }).setView([22.5, 79], 5);

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: '&copy; OpenStreetMap contributors'
      }
    ).addTo(map);

    markersLayer.current = L.layerGroup().addTo(map);
    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  const filteredAlerts = useMemo(() => {
  return alerts.filter((alert) => {
    // Show only active CWC alert levels.
    // GREEN / Normal stations are intentionally excluded.
    const isActiveAlert =
      alert.alert_level === 'RED' ||
      alert.alert_level === 'ORANGE' ||
      alert.alert_level === 'YELLOW';

    if (!isActiveAlert) {
      return false;
    }

    const matchesState =
      stateFilter === 'ALL' ||
      alert.state?.toUpperCase() === stateFilter;

    const matchesCondition =
      conditionFilter === 'ALL' ||
      alert.alert_level === conditionFilter;

    const query = search.toLowerCase();

    const matchesSearch =
      !query ||
      alert.station?.toLowerCase().includes(query) ||
      alert.district?.toLowerCase().includes(query) ||
      alert.state?.toLowerCase().includes(query) ||
      alert.river?.toLowerCase().includes(query);

    return (
      matchesState &&
      matchesCondition &&
      matchesSearch
    );
  });
}, [
  alerts,
  stateFilter,
  conditionFilter,
  search
]);

  useEffect(() => {
    if (!mapInstance.current || !markersLayer.current) return;

    markersLayer.current.clearLayers();

    filteredAlerts.forEach((alert) => {
      const lat = Number(alert.latitude);
      const lng = Number(alert.longitude);

      if (
        !Number.isFinite(lat) ||
        !Number.isFinite(lng)
      ) {
        return;
      }

      let color = '#eab308';

      if (alert.alert_level === 'RED') {
        color = '#dc2626';
      } else if (alert.alert_level === 'ORANGE') {
        color = '#f97316';
      }

      const icon = L.divIcon({
        className: '',
        html: `
          <div style="
            width:18px;
            height:18px;
            border-radius:50%;
            background:${color};
            border:3px solid white;
            box-shadow:0 1px 6px rgba(0,0,0,.45);
          "></div>
        `,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });

      const marker = L.marker(
        [lat, lng],
        { icon }
      );

      marker.bindPopup(`
        <div style="min-width:220px;font-family:Arial">
          <strong style="font-size:15px">
            ${alert.station || 'CWC Station'}
          </strong>

          <div style="margin-top:6px">
            <b>River:</b> ${alert.river || '—'}
          </div>

          <div>
            <b>District:</b> ${alert.district || '—'}
          </div>

          <div>
            <b>State:</b> ${alert.state || '—'}
          </div>

          <div style="margin-top:6px">
            <b>Condition:</b> ${alert.condition || '—'}
          </div>

          <div>
            <b>Current Level:</b> ${alert.current_level || '—'}
          </div>

          <div>
            <b>Warning Level:</b> ${alert.warning_level || '—'}
          </div>

          <div>
            <b>Danger Level:</b> ${alert.danger_level || '—'}
          </div>
        </div>
      `);

      marker.addTo(markersLayer.current!);
    });
  }, [filteredAlerts]);

  /* ================= STATISTICS ================= */

  const redCount = alerts.filter(
    a => a.alert_level === 'RED'
  ).length;

  const orangeCount = alerts.filter(
    a => a.alert_level === 'ORANGE'
  ).length;

  const yellowCount = alerts.filter(
    a => a.alert_level === 'YELLOW'
  ).length;

  const states = Array.from(
    new Set(
      alerts
        .map(a => a.state)
        .filter(Boolean)
    )
  ).sort();

  /* ================= UI ================= */

  return (
    <div className="max-w-[1500px] mx-auto px-4 sm:px-6 py-5">

      {/* HEADER */}

      <div className="bg-navy text-ivory rounded-xl shadow-md overflow-hidden">

        <div className="px-5 py-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">

          <div>
            <div className="flex items-center gap-3">
              <Waves className="w-7 h-7 text-terracotta" />

              <div>
                <h1 className="text-xl sm:text-2xl font-bold">
                  LIVE FLOOD MONITORING
                </h1>

                <p className="text-xs text-slate-light mt-0.5">
                  India Flood Forecast & Warning Information
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">

            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-navy-800 border border-slate/30">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-bold">
                LIVE CWC DATA
              </span>
            </div>

            <button
              onClick={loadAlerts}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-terracotta text-white text-xs font-semibold hover:bg-terracotta/90"
            >
              <RefreshCw
                className={`w-4 h-4 ${
                  loading ? 'animate-spin' : ''
                }`}
              />
              Refresh
            </button>

          </div>
        </div>

        {/* STATUS STRIP */}

        <div className="grid grid-cols-3 border-t border-navy-700">

          <div className="px-4 py-3 border-r border-navy-700">
            <div className="text-[10px] uppercase text-slate-light">
              Extreme
            </div>
            <div className="text-xl font-bold text-red-400">
              {redCount}
            </div>
          </div>

          <div className="px-4 py-3 border-r border-navy-700">
            <div className="text-[10px] uppercase text-slate-light">
              Severe
            </div>
            <div className="text-xl font-bold text-orange-400">
              {orangeCount}
            </div>
          </div>

          <div className="px-4 py-3">
            <div className="text-[10px] uppercase text-slate-light">
              Above Normal
            </div>
            <div className="text-xl font-bold text-yellow-400">
              {yellowCount}
            </div>
          </div>

        </div>
      </div>

      {/* ERROR */}

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
          {error}
        </div>
      )}

      {/* MAIN DASHBOARD */}

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_360px] gap-4 mt-4">

        {/* MAP */}

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">

            <div>
              <h2 className="font-bold text-navy">
                India Flood Situation
              </h2>

              <p className="text-xs text-slate-light">
                CWC monitoring stations and active conditions
              </p>
            </div>

            <Activity className="w-5 h-5 text-terracotta" />

          </div>

          <div
            ref={mapRef}
            className="w-full h-[480px] sm:h-[560px]"
          />

          {/* LEGEND */}

          <div className="px-4 py-3 border-t border-slate-200 flex flex-wrap gap-5 text-xs">

            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-600" />
              Extreme
            </div>

            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-orange-500" />
              Severe
            </div>

            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-yellow-500" />
              Above Normal
            </div>

          </div>
        </div>

        {/* ALERT PANEL */}

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">

          <div className="px-4 py-3 bg-navy text-white">

            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-terracotta" />

              <div>
                <h2 className="font-bold">
                  ALERTS & WARNINGS
                </h2>

                <p className="text-[10px] text-slate-light">
                  Current CWC flood conditions
                </p>
              </div>
            </div>

          </div>

          <div className="overflow-y-auto max-h-[560px]">

            {loading && alerts.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-light">
                Loading live alerts...
              </div>
            ) : filteredAlerts.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-light">
                No matching flood alerts.
              </div>
            ) : (
              filteredAlerts.map((alert, index) => (
                <div
                  key={`${alert.station}-${index}`}
                  className="p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors"
                >

                  <div className="flex justify-between gap-3">

                    <div className="min-w-0">

                      <div className="font-bold text-sm text-navy truncate">
                        {alert.station}
                      </div>

                      <div className="text-xs text-slate-light mt-1 flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {alert.district}, {alert.state}
                      </div>

                    </div>

                    <span
                      className={`shrink-0 px-2 py-1 rounded text-[10px] font-bold ${
                        alert.alert_level === 'RED'
                          ? 'bg-red-100 text-red-700'
                          : alert.alert_level === 'ORANGE'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {alert.condition}
                    </span>

                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs">

                    <div>
                      <span className="text-slate-light">
                        River
                      </span>

                      <div className="font-semibold text-navy truncate">
                        {alert.river || '—'}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-light">
                        Current Level
                      </span>

                      <div className="font-semibold text-navy">
                        {alert.current_level || '—'}
                      </div>
                    </div>

                  </div>

                </div>
              ))
            )}

          </div>
        </div>

      </div>

      {/* FILTERS */}

      <div className="mt-4 bg-white rounded-xl border border-slate-200 shadow-sm">

        <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-2">
          <Filter className="w-4 h-4 text-terracotta" />
          <h2 className="font-bold text-navy">
            Flood Forecast Stations
          </h2>
        </div>

        <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">

          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />

            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search station, district or river..."
              className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-200 text-sm outline-none focus:border-navy"
            />
          </div>

          <select
            value={stateFilter}
            onChange={e => setStateFilter(e.target.value)}
            className="px-3 py-2.5 rounded-lg border border-slate-200 text-sm bg-white"
          >
            <option value="ALL">
              All States
            </option>

            {states.map(state => (
              <option
                key={state}
                value={state.toUpperCase()}
              >
                {state}
              </option>
            ))}
          </select>

          <select
            value={conditionFilter}
            onChange={e => setConditionFilter(e.target.value)}
            className="px-3 py-2.5 rounded-lg border border-slate-200 text-sm bg-white"
          >
            <option value="ALL">
              All Conditions
            </option>
            <option value="RED">
              Extreme
            </option>
            <option value="ORANGE">
              Severe
            </option>
            <option value="YELLOW">
              Above Normal
            </option>
          </select>

        </div>

      </div>

      {/* TABLE */}

      <div className="mt-4 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">

        <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">

          <div>
            <h2 className="font-bold text-navy">
              CWC Flood Forecast Stations
            </h2>

            <p className="text-xs text-slate-light mt-0.5">
              {filteredAlerts.length} stations displayed
            </p>
          </div>

          <span className="text-[10px] uppercase font-bold text-slate-light">
            Source: Central Water Commission
          </span>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-sm">

            <thead className="bg-slate-50 text-xs uppercase text-slate-light">

              <tr>
                <th className="text-left px-4 py-3">
                  Station
                </th>

                <th className="text-left px-4 py-3">
                  River
                </th>

                <th className="text-left px-4 py-3">
                  District
                </th>

                <th className="text-left px-4 py-3">
                  State
                </th>

                <th className="text-left px-4 py-3">
                  Condition
                </th>

                <th className="text-left px-4 py-3">
                  Current Level
                </th>
              </tr>

            </thead>

            <tbody>

              {filteredAlerts.slice(0, 100).map(
                (alert, index) => (
                  <tr
                    key={`${alert.station}-table-${index}`}
                    className="border-t border-slate-100 hover:bg-slate-50"
                  >

                    <td className="px-4 py-3 font-semibold text-navy">
                      {alert.station}
                    </td>

                    <td className="px-4 py-3">
                      {alert.river || '—'}
                    </td>

                    <td className="px-4 py-3">
                      {alert.district || '—'}
                    </td>

                    <td className="px-4 py-3">
                      {alert.state || '—'}
                    </td>

                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded text-[10px] font-bold ${
                          alert.alert_level === 'RED'
                            ? 'bg-red-100 text-red-700'
                            : alert.alert_level === 'ORANGE'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {alert.condition}
                      </span>
                    </td>

                    <td className="px-4 py-3 font-semibold">
                      {alert.current_level || '—'}
                    </td>

                  </tr>
                )
              )}

            </tbody>

          </table>

        </div>
      </div>

      {/* SOURCE NOTE */}

      <div className="mt-4 flex items-start gap-2 text-xs text-slate-light">
        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />

        <span>
          Live flood conditions are provided from the Central Water
          Commission flood forecasting source. ResQFlow presents the
          source information for situational awareness and does not
          replace official emergency advisories.
        </span>
      </div>

    </div>
  );
};

export default FloodAlertsPage;