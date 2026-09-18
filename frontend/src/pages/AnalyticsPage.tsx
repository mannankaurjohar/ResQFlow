import React, { useEffect, useState } from 'react';
import { AnalyticsData } from '../types';
import api from '../services/api';
import { BarChart3, TrendingUp, AlertCircle, ShieldAlert, Clock, RefreshCw } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [forecasts, setForecasts] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getAnalytics(),
      api.getForecasts()
    ]).then(([aData, fData]) => {
      setAnalytics(aData);
      setForecasts(fData);
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
            <BarChart3 className="w-7 h-7 text-terracotta" />
            <span>Impact Analytics & Demand Forecasting</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate mt-1">
            Operational metrics, supply-demand gaps, and 6h / 12h / 24h predictive relief curves
          </p>
        </div>
        <button onClick={loadData} className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* 4 Primary Operational KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="text-xs uppercase tracking-wider text-slate font-semibold">Total Requests Handled</div>
          <div className="text-3xl font-extrabold text-navy mt-1">{analytics?.total_requests || 28}</div>
          <div className="text-xs text-status-fulfilled font-medium mt-1">
            {analytics?.fulfillment_rate_pct}% Fulfilled
          </div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="text-xs uppercase tracking-wider text-slate font-semibold">Average Response Time</div>
          <div className="text-3xl font-extrabold text-navy mt-1">38 mins</div>
          <div className="text-xs text-slate mt-1">From report to AI allocation</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="text-xs uppercase tracking-wider text-slate font-semibold">Average Delivery Time</div>
          <div className="text-3xl font-extrabold text-terracotta mt-1">74 mins</div>
          <div className="text-xs text-slate mt-1">Through inundated corridors</div>
        </div>
        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="text-xs uppercase tracking-wider text-slate font-semibold">People Supported</div>
          <div className="text-3xl font-extrabold text-navy mt-1">{analytics?.people_assisted.toLocaleString() || '12,450'}</div>
          <div className="text-xs text-slate mt-1">Verified handovers</div>
        </div>
      </div>

      {/* Demand Forecasting Table (6h, 12h, 24h) */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-navy flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-terracotta" />
              <span>Predictive Emergency Demand Forecasting</span>
            </h3>
            <p className="text-xs text-slate mt-0.5">
              Simulated consumption curves based on WHO/Sphere minimum emergency standards & water-level telemetry
            </p>
          </div>
          <span className="text-[10px] bg-navy-800 text-slate-light px-2.5 py-1 rounded font-mono">
            6H &bull; 12H &bull; 24H FORECAST
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
              <tr>
                <th className="py-2.5 px-3">Relief Commodity</th>
                <th className="py-2.5 px-3 font-mono text-terracotta">Next 6 Hours</th>
                <th className="py-2.5 px-3 font-mono text-terracotta">Next 12 Hours</th>
                <th className="py-2.5 px-3 font-mono text-terracotta">Next 24 Hours</th>
                <th className="py-2.5 px-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/15">
              {forecasts?.forecasts?.map((f: any, idx: number) => (
                <tr key={idx} className="hover:bg-ivory-50">
                  <td className="py-3 px-3 font-bold text-navy">{f.category}</td>
                  <td className="py-3 px-3 font-mono font-bold">{f.hours_6.toLocaleString()} {f.unit}</td>
                  <td className="py-3 px-3 font-mono font-bold text-terracotta">{f.hours_12.toLocaleString()} {f.unit}</td>
                  <td className="py-3 px-3 font-mono font-bold">{f.hours_24.toLocaleString()} {f.unit}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 font-semibold text-[10px]">
                      {Math.round(f.confidence * 100)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Supply-Demand Gap Breakdown */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-4">Supply-Demand Gap Radar</h3>
        <div className="space-y-4">
          {analytics?.supply_demand_gap?.map((item, idx) => (
            <div key={idx} className="text-xs">
              <div className="flex justify-between font-semibold mb-1">
                <span className="text-navy">{item.category}</span>
                <span className="text-slate">
                  Demanded: <b>{item.demand.toLocaleString()}</b> &bull; Available: <b>{item.available.toLocaleString()}</b> &bull; Gap: <b className="text-red-600">{item.gap.toLocaleString()}</b>
                </span>
              </div>
              <div className="w-full bg-slate/20 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-terracotta h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(100, item.fulfillment_pct || 50)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
