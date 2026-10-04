import React, { useMemo, useState } from 'react';
import {
  Search,
  Package,
  ShieldAlert,
  MapPin,
  Clock,
  Users,
  ArrowRight,
  RefreshCw
} from 'lucide-react';

import api from '../services/api';
import { useApp } from '../context/AppContext';
import { CommunityRequest } from '../types';

type RequestFilter = 'ALL' | 'SUPPLIES' | 'EVACUATION';

type RequestWithExtras = CommunityRequest & {
  created_at?: string;
  updated_at?: string;
  request_type?: string;
};

const MyRequestsPage: React.FC = () => {
  const { setActiveTab } = useApp();

  const [phone, setPhone] = useState('');
  const [requests, setRequests] = useState<RequestWithExtras[]>([]);
  const [filter, setFilter] = useState<RequestFilter>('ALL');

  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');

  const loadRequests = async () => {
    const cleanedPhone = phone.trim();

    if (!cleanedPhone) {
      setError('Please enter the phone number used when submitting your request.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await api.getMyRequests(cleanedPhone);

      setRequests((data || []) as RequestWithExtras[]);
      setSearched(true);
    } catch (err) {
      console.error('Failed to load requests:', err);

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load your requests.'
      );

      setRequests([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const filteredRequests = useMemo(() => {
    if (filter === 'ALL') {
      return requests;
    }

    return requests.filter(request => {
      const type =
        request.request_type ||
        '';

      const description =
        request.raw_description ||
        '';

      if (filter === 'EVACUATION') {
        return (
          type.toUpperCase() === 'EVACUATION' ||
          description.toUpperCase().includes('TYPE: EVACUATION')
        );
      }

      return (
        type.toUpperCase() === 'SUPPLIES' ||
        description.toUpperCase().includes('TYPE: SUPPLIES')
      );
    });
  }, [requests, filter]);

  const getRequestType = (
    request: RequestWithExtras
  ) => {
    const type =
      request.request_type ||
      '';

    if (
      type.toUpperCase() === 'EVACUATION' ||
      request.raw_description
        ?.toUpperCase()
        .includes('TYPE: EVACUATION')
    ) {
      return 'EVACUATION';
    }

    return 'SUPPLIES';
  };

  const getStatusLabel = (status: unknown) => {
    const value = String(status || 'PENDING');

    return value
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, char => char.toUpperCase());
  };

  const getStatusClass = (status: unknown) => {
    const value = String(status || '').toUpperCase();

    if (
      value.includes('COMPLETED') ||
      value.includes('FULFILLED') ||
      value.includes('CLOSED')
    ) {
      return 'bg-emerald-100 text-emerald-700';
    }

    if (
      value.includes('REJECTED') ||
      value.includes('CANCELLED')
    ) {
      return 'bg-red-100 text-red-700';
    }

    if (
      value.includes('CRITICAL') ||
      value.includes('ESCALATED')
    ) {
      return 'bg-red-100 text-red-700';
    }

    if (
      value.includes('VERIFIED') ||
      value.includes('PROCESS')
    ) {
      return 'bg-blue-100 text-blue-700';
    }

    return 'bg-amber-100 text-amber-700';
  };

  const getPriorityClass = (priority: unknown) => {
    const value = String(priority || '').toUpperCase();

    if (
      value.includes('CRITICAL') ||
      value.includes('HIGH')
    ) {
      return 'bg-red-100 text-red-700';
    }

    if (value.includes('MEDIUM')) {
      return 'bg-amber-100 text-amber-700';
    }

    return 'bg-slate-100 text-slate-600';
  };

  const formatDate = (date?: string) => {
    if (!date) {
      return 'Date unavailable';
    }

    const parsed = new Date(date);

    if (Number.isNaN(parsed.getTime())) {
      return date;
    }

    return parsed.toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">

      {/* HEADER */}
      <div className="mb-7">

        <div className="flex items-center gap-3 mb-2">
          <div className="w-11 h-11 rounded-xl bg-navy flex items-center justify-center">
            <Clock className="w-5 h-5 text-ivory" />
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-navy">
              My Requests
            </h1>

            <p className="text-sm text-slate-500 mt-1">
              View the history and current status of requests
              submitted with your phone number.
            </p>
          </div>
        </div>

      </div>

      {/* PHONE SEARCH */}
      <div className="bg-ivory border border-slate/20 rounded-2xl shadow-sm p-5 mb-6">

        <div className="max-w-2xl">

          <label className="block text-sm font-semibold text-slate-dark mb-2">
            Phone Number
          </label>

          <div className="flex flex-col sm:flex-row gap-3">

            <div className="relative flex-1">

              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />

              <input
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    loadRequests();
                  }
                }}
                placeholder="Enter the phone number used for your request"
                className="
                  w-full
                  pl-10
                  pr-4
                  py-3
                  rounded-lg
                  border
                  border-slate/30
                  bg-white
                  text-sm
                  text-slate-dark
                  outline-none
                  focus:border-navy
                  focus:ring-2
                  focus:ring-navy/10
                "
              />

            </div>

            <button
              type="button"
              onClick={loadRequests}
              disabled={loading}
              className="
                px-5
                py-3
                rounded-lg
                bg-navy
                hover:bg-navy-800
                text-white
                font-semibold
                text-sm
                flex
                items-center
                justify-center
                gap-2
                disabled:opacity-60
              "
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}

              {loading ? 'Loading...' : 'View Requests'}
            </button>

          </div>

          {error && (
            <p className="mt-3 text-sm text-red-600">
              {error}
            </p>
          )}

        </div>

      </div>

      {/* FILTERS */}
      {searched && (
        <div className="flex flex-wrap items-center gap-2 mb-5">

          <button
            onClick={() => setFilter('ALL')}
            className={`
              px-4 py-2 rounded-lg text-sm font-semibold
              ${
                filter === 'ALL'
                  ? 'bg-navy text-white'
                  : 'bg-white border border-slate/20 text-slate-600 hover:bg-slate-50'
              }
            `}
          >
            All
          </button>

          <button
            onClick={() => setFilter('SUPPLIES')}
            className={`
              px-4 py-2 rounded-lg text-sm font-semibold
              ${
                filter === 'SUPPLIES'
                  ? 'bg-navy text-white'
                  : 'bg-white border border-slate/20 text-slate-600 hover:bg-slate-50'
              }
            `}
          >
            Supplies
          </button>

          <button
            onClick={() => setFilter('EVACUATION')}
            className={`
              px-4 py-2 rounded-lg text-sm font-semibold
              ${
                filter === 'EVACUATION'
                  ? 'bg-navy text-white'
                  : 'bg-white border border-slate/20 text-slate-600 hover:bg-slate-50'
              }
            `}
          >
            Evacuation
          </button>

          <span className="ml-auto text-xs text-slate-400">
            {filteredRequests.length} request
            {filteredRequests.length === 1 ? '' : 's'}
          </span>

        </div>
      )}

      {/* EMPTY STATE */}
      {searched && filteredRequests.length === 0 && !loading && (
        <div className="bg-ivory border border-slate/20 rounded-2xl p-10 text-center">

          <div className="w-14 h-14 mx-auto rounded-full bg-slate-100 flex items-center justify-center mb-4">
            <Search className="w-6 h-6 text-slate-400" />
          </div>

          <h2 className="text-lg font-bold text-navy">
            No requests found
          </h2>

          <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto">
            No requests were found for this phone number.
            Make sure you entered the same number used when
            submitting your request.
          </p>

        </div>
      )}

      {/* REQUEST HISTORY */}
      <div className="space-y-4">

        {filteredRequests.map(request => {

          const requestType =
            getRequestType(request);

          const isEvacuation =
            requestType === 'EVACUATION';

          return (
            <div
              key={request.id}
              className="
                bg-ivory
                border
                border-slate/20
                rounded-2xl
                shadow-sm
                overflow-hidden
              "
            >

              {/* CARD HEADER */}
              <div className="px-5 py-4 border-b border-slate/10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">

                <div className="flex items-center gap-3">

                  <div
                    className={`
                      w-10 h-10 rounded-lg
                      flex items-center justify-center
                      ${
                        isEvacuation
                          ? 'bg-red-50 text-red-600'
                          : 'bg-blue-50 text-blue-600'
                      }
                    `}
                  >
                    {isEvacuation ? (
                      <ShieldAlert className="w-5 h-5" />
                    ) : (
                      <Package className="w-5 h-5" />
                    )}
                  </div>

                  <div>

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">
                      {isEvacuation
                        ? 'Evacuation Request'
                        : 'Supply Request'}
                    </p>

                    <p className="font-bold text-navy text-sm">
                      {request.tracking_code}
                    </p>

                  </div>

                </div>

                <span
                  className={`
                    self-start sm:self-auto
                    px-3 py-1.5
                    rounded-full
                    text-[11px]
                    font-bold
                    ${getStatusClass(request.status)}
                  `}
                >
                  {getStatusLabel(request.status)}
                </span>

              </div>

              {/* CARD BODY */}
              <div className="p-5">

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

                  {/* LOCATION */}
                  <div>

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                      Location
                    </p>

                    <div className="flex items-start gap-2">

                      <MapPin className="w-4 h-4 text-terracotta mt-0.5 shrink-0" />

                      <p className="text-sm text-slate-dark">
                        {request.location_name || 'Location unavailable'}
                      </p>

                    </div>

                  </div>

                  {/* SUBMITTED */}
                  <div>

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                      Submitted
                    </p>

                    <div className="flex items-center gap-2">

                      <Clock className="w-4 h-4 text-slate-400 shrink-0" />

                      <p className="text-sm text-slate-dark">
                        {formatDate(request.created_at)}
                      </p>

                    </div>

                  </div>

                  {/* PEOPLE */}
                  <div>

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                      People Affected
                    </p>

                    <div className="flex items-center gap-2">

                      <Users className="w-4 h-4 text-slate-400" />

                      <p className="text-sm text-slate-dark">
                        {request.affected_people ?? 0}
                      </p>

                    </div>

                  </div>

                  {/* PRIORITY */}
                  <div>

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                      Priority
                    </p>

                    <span
                      className={`
                        inline-flex
                        px-2.5
                        py-1
                        rounded-md
                        text-[11px]
                        font-bold
                        ${getPriorityClass(
                          request.priority_classification
                        )}
                      `}
                    >
                      {request.priority_classification ||
                        'PENDING'}
                    </span>

                  </div>

                </div>

                {/* DESCRIPTION */}
                {request.raw_description && (
                  <div className="mt-4 pt-4 border-t border-slate/10">

                    <p className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1">
                      Request Details
                    </p>

                    <p className="text-sm text-slate-600 line-clamp-2">
                      {request.raw_description}
                    </p>

                  </div>
                )}

                {/* ACTION */}
                <div className="mt-5 flex justify-end">

                  <button
                    type="button"
                    onClick={() => setActiveTab('trace')}
                    className="
                      flex
                      items-center
                      gap-2
                      px-4
                      py-2.5
                      rounded-lg
                      bg-navy
                      hover:bg-navy-800
                      text-white
                      text-xs
                      font-semibold
                      transition
                    "
                  >
                    Track Relief
                    <ArrowRight className="w-4 h-4" />
                  </button>

                </div>

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
};

export default MyRequestsPage;