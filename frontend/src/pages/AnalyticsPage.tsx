import React, { useEffect, useMemo, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  RefreshCw,
  Users,
  Truck,
  Clock,
  Package,
  AlertTriangle,
} from 'lucide-react';

import api from '../services/api';
import { AnalyticsData } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [forecasts, setForecasts] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);

    try {
      const [analyticsData, forecastData] = await Promise.all([
        api.getAnalytics(),
        api.getForecasts(),
      ]);

      setAnalytics(analyticsData);
      setForecasts(forecastData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const maxTrendRequests = useMemo(() => {
    if (!analytics?.request_trend?.length) return 1;

    return Math.max(
      ...analytics.request_trend.map(
        (item: any) => item.requests || 0
      ),
      1
    );
  }, [analytics]);

  const maxLocationRequests = useMemo(() => {
    if (!analytics?.location_breakdown?.length) return 1;

    return Math.max(
      ...analytics.location_breakdown.map(
        (item: any) => item.requests || 0
      ),
      1
    );
  }, [analytics]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex items-center justify-center min-h-[300px]">
          <RefreshCw className="w-6 h-6 animate-spin text-terracotta mr-3" />
          <span className="text-slate">
            Loading operational analytics...
          </span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="bg-ivory border border-slate/20 rounded-xl p-8 text-center">
          <AlertTriangle className="w-8 h-8 text-terracotta mx-auto mb-3" />
          <h2 className="font-bold text-navy">
            Analytics unavailable
          </h2>
          <p className="text-sm text-slate mt-1">
            Unable to load analytics data from the backend.
          </p>

          <button
            onClick={loadData}
            className="mt-4 px-4 py-2 rounded-lg bg-navy text-white text-sm font-semibold hover:bg-navy-800"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate/20 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-terracotta" />
            <span>Impact Analytics</span>
          </h1>

          <p className="text-xs sm:text-sm text-slate mt-1">
            Live operational metrics derived from ResQFlow request,
            allocation, delivery and inventory data
          </p>
        </div>

        <button
          onClick={loadData}
          className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory"
          title="Refresh analytics"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Primary KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <div className="text-xs uppercase tracking-wider text-slate font-semibold">
              Total Requests
            </div>
            <Package className="w-5 h-5 text-terracotta" />
          </div>

          <div className="text-3xl font-extrabold text-navy mt-2">
            {analytics.total_requests}
          </div>

          <div className="text-xs text-slate mt-1">
            {analytics.supply_requests} supply •{' '}
            {analytics.evacuation_requests} evacuation
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <div className="text-xs uppercase tracking-wider text-slate font-semibold">
              Fulfillment Rate
            </div>
            <TrendingUp className="w-5 h-5 text-terracotta" />
          </div>

          <div className="text-3xl font-extrabold text-navy mt-2">
            {analytics.fulfillment_rate_pct}%
          </div>

          <div className="text-xs text-slate mt-1">
            {analytics.fulfilled_requests} requests delivered
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <div className="text-xs uppercase tracking-wider text-slate font-semibold">
              People Assisted
            </div>
            <Users className="w-5 h-5 text-terracotta" />
          </div>

          <div className="text-3xl font-extrabold text-navy mt-2">
            {analytics.people_assisted.toLocaleString()}
          </div>

          <div className="text-xs text-slate mt-1">
            of {analytics.people_affected.toLocaleString()} affected
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <div className="text-xs uppercase tracking-wider text-slate font-semibold">
              Active Deliveries
            </div>
            <Truck className="w-5 h-5 text-terracotta" />
          </div>

          <div className="text-3xl font-extrabold text-navy mt-2">
            {analytics.active_deliveries}
          </div>

          <div className="text-xs text-slate mt-1">
            Currently allocated / dispatched / in transit
          </div>
        </div>

      </div>

      {/* Response Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="bg-ivory border border-slate/20 rounded-xl p-5">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-terracotta" />
            <h3 className="font-bold text-navy">
              Request → Allocation
            </h3>
          </div>

          <div className="text-2xl font-extrabold text-navy mt-3">
            {analytics.average_response_time_mins !== null &&
            analytics.average_response_time_mins !== undefined
              ? `${analytics.average_response_time_mins} mins`
              : '—'}
          </div>

          <p className="text-xs text-slate mt-1">
            Calculated from recorded request and allocation timestamps
          </p>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-5">
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-terracotta" />
            <h3 className="font-bold text-navy">
              Dispatch → Delivery
            </h3>
          </div>

          <div className="text-2xl font-extrabold text-navy mt-3">
            {analytics.average_delivery_time_mins !== null &&
            analytics.average_delivery_time_mins !== undefined
              ? `${analytics.average_delivery_time_mins} mins`
              : '—'}
          </div>

          <p className="text-xs text-slate mt-1">
            Calculated from recorded delivery timestamps
          </p>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-5">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-terracotta" />
            <h3 className="font-bold text-navy">
              Critical Pending
            </h3>
          </div>

          <div className="text-2xl font-extrabold text-navy mt-3">
            {analytics.critical_requests_pending}
          </div>

          <p className="text-xs text-slate mt-1">
            Critical requests still awaiting action
          </p>
        </div>

      </div>

      {/* Request Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
          <h3 className="font-bold text-base text-navy mb-4">
            Request Status
          </h3>

          <div className="space-y-3">
            {Object.entries(
              analytics.status_breakdown || {}
            ).map(([status, count]) => (
              <div
                key={status}
                className="flex items-center justify-between"
              >
                <span className="text-xs font-semibold text-slate">
                  {status.replace(/_/g, ' ')}
                </span>

                <span className="text-sm font-bold text-navy">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
          <h3 className="font-bold text-base text-navy mb-4">
            Priority Distribution
          </h3>

          <div className="space-y-3">
            {Object.entries(
              analytics.priority_breakdown || {}
            ).map(([priority, count]) => (
              <div
                key={priority}
                className="flex items-center justify-between"
              >
                <span className="text-xs font-semibold text-slate">
                  {priority}
                </span>

                <span className="text-sm font-bold text-navy">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* People Impact */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-4">
          People Impact
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">

          <div>
            <div className="text-xs text-slate">
              Children
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.children_affected}
            </div>
          </div>

          <div>
            <div className="text-xs text-slate">
              Elderly
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.elderly_affected}
            </div>
          </div>

          <div>
            <div className="text-xs text-slate">
              Infants
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.infants_affected}
            </div>
          </div>

          <div>
            <div className="text-xs text-slate">
              Pregnant
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.pregnant_affected}
            </div>
          </div>

          <div>
            <div className="text-xs text-slate">
              Medical Emergency
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.medical_emergency_requests}
            </div>
          </div>

          <div>
            <div className="text-xs text-slate">
              Immediate Danger
            </div>
            <div className="text-xl font-bold text-navy">
              {analytics.immediate_danger_requests}
            </div>
          </div>

        </div>
      </div>

      {/* Supply Demand */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">

        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-navy">
              Supply-Demand Analysis
            </h3>
            <p className="text-xs text-slate mt-1">
              Based on actual requested quantities, fulfilled quantities
              and current inventory
            </p>
          </div>
        </div>

        {analytics.supply_demand_gap?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
                <tr>
                  <th className="py-2.5 px-3">
                    Category
                  </th>
                  <th className="py-2.5 px-3">
                    Demand
                  </th>
                  <th className="py-2.5 px-3">
                    Fulfilled
                  </th>
                  <th className="py-2.5 px-3">
                    Available
                  </th>
                  <th className="py-2.5 px-3">
                    Gap
                  </th>
                  <th className="py-2.5 px-3">
                    Fulfillment
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate/15">
                {analytics.supply_demand_gap.map(
                  (item: any, index: number) => (
                    <tr
                      key={index}
                      className="hover:bg-ivory-50"
                    >
                      <td className="py-3 px-3 font-bold text-navy">
                        {item.category}
                      </td>

                      <td className="py-3 px-3">
                        {item.demand.toLocaleString()}
                      </td>

                      <td className="py-3 px-3">
                        {item.fulfilled.toLocaleString()}
                      </td>

                      <td className="py-3 px-3">
                        {item.available.toLocaleString()}
                      </td>

                      <td className="py-3 px-3 font-bold text-terracotta">
                        {item.gap.toLocaleString()}
                      </td>

                      <td className="py-3 px-3">
                        {item.fulfillment_pct}%
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-sm text-slate py-6 text-center">
            No supply-demand data available yet.
          </div>
        )}
      </div>

      {/* Request Trend */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-1">
          Request Trend
        </h3>

        <p className="text-xs text-slate mb-5">
          Number of requests recorded per day
        </p>

        {analytics.request_trend?.length ? (
          <div className="space-y-3">
            {analytics.request_trend.map(
              (item: any) => (
                <div key={item.date}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate">
                      {item.date}
                    </span>

                    <span className="font-bold text-navy">
                      {item.requests}
                    </span>
                  </div>

                  <div className="w-full bg-slate/10 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-terracotta h-2 rounded-full"
                      style={{
                        width: `${
                          (item.requests /
                            maxTrendRequests) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          <div className="text-sm text-slate py-6 text-center">
            No request history available yet.
          </div>
        )}
      </div>

      {/* Location Breakdown */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-1">
          Requests by Location
        </h3>

        <p className="text-xs text-slate mb-5">
          Locations ranked by recorded request volume
        </p>

        {analytics.location_breakdown?.length ? (
          <div className="space-y-4">
            {analytics.location_breakdown.map(
              (item: any) => (
                <div key={item.location}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-semibold text-navy">
                      {item.location}
                    </span>

                    <span className="text-slate">
                      {item.requests} requests •{' '}
                      {item.people} people
                    </span>
                  </div>

                  <div className="w-full bg-slate/10 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-navy h-2 rounded-full"
                      style={{
                        width: `${
                          (item.requests /
                            maxLocationRequests) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>
        ) : (
          <div className="text-sm text-slate py-6 text-center">
            No location data available yet.
          </div>
        )}
      </div>

      {/* Resources Distributed */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-4">
          Resources Distributed
        </h3>

        {analytics.resources_distributed?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
                <tr>
                  <th className="py-2.5 px-3">
                    Item
                  </th>
                  <th className="py-2.5 px-3">
                    Quantity
                  </th>
                  <th className="py-2.5 px-3">
                    Unit
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate/15">
                {analytics.resources_distributed.map(
                  (resource: any, index: number) => (
                    <tr key={index}>
                      <td className="py-3 px-3 font-semibold text-navy">
                        {resource.item}
                      </td>

                      <td className="py-3 px-3 font-mono font-bold">
                        {resource.quantity.toLocaleString()}
                      </td>

                      <td className="py-3 px-3 text-slate">
                        {resource.unit}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-sm text-slate py-6 text-center">
            No fulfilled resources recorded yet.
          </div>
        )}
      </div>

      {/* Demand Forecast */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">

        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-navy flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-terracotta" />
              Demand Forecast
            </h3>

            <p className="text-xs text-slate mt-1">
              Model-generated estimate based on current zones and request
              data. This is a forecast, not historical activity.
            </p>
          </div>

          <span className="text-[10px] bg-navy-800 text-slate-light px-2.5 py-1 rounded font-mono">
            FORECAST
          </span>
        </div>

        {forecasts?.forecasts?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
                <tr>
                  <th className="py-2.5 px-3">
                    Commodity
                  </th>
                  <th className="py-2.5 px-3">
                    6 Hours
                  </th>
                  <th className="py-2.5 px-3">
                    12 Hours
                  </th>
                  <th className="py-2.5 px-3">
                    24 Hours
                  </th>
                  <th className="py-2.5 px-3">
                    Confidence
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate/15">
                {forecasts.forecasts.map(
                  (forecast: any, index: number) => (
                    <tr key={index}>
                      <td className="py-3 px-3 font-bold text-navy">
                        {forecast.category}
                      </td>

                      <td className="py-3 px-3 font-mono">
                        {forecast.hours_6.toLocaleString()}{' '}
                        {forecast.unit}
                      </td>

                      <td className="py-3 px-3 font-mono text-terracotta font-bold">
                        {forecast.hours_12.toLocaleString()}{' '}
                        {forecast.unit}
                      </td>

                      <td className="py-3 px-3 font-mono">
                        {forecast.hours_24.toLocaleString()}{' '}
                        {forecast.unit}
                      </td>

                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 font-semibold text-[10px]">
                          {Math.round(
                            forecast.confidence * 100
                          )}
                          %
                        </span>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-sm text-slate py-6 text-center">
            No forecast data available.
          </div>
        )}

      </div>

    </div>
  );
};