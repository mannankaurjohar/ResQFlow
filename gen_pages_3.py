from helper_writer import write_file

# 1. DonorPortalPage.tsx
donor_code = """import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
import { HeartHandshake, CheckCircle2, Search, ArrowRight, ShieldCheck, Gift } from 'lucide-react';

export const DonorPortalPage: React.FC = () => {
  const { showNotification, setActiveTab, setTraceIdInput } = useApp();

  const [donorName, setDonorName] = useState('Anita & Vikram Sharma');
  const [donorEmail, setDonorEmail] = useState('anita.sharma@gmail.com');
  const [category, setCategory] = useState('Drinking Water');
  const [quantity, setQuantity] = useState(500);
  const [unit, setUnit] = useState('Bottles');
  const [notes, setNotes] = useState('Emergency flood relief for stranded families in Zone B delta.');
  const [submitting, setSubmitting] = useState(false);
  const [createdReliefId, setCreatedReliefId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.createDonation({
        donor_name: donorName,
        donor_email: donorEmail,
        notes: notes,
        items: [{
          category: category,
          item_name: `${category} Supply Pack`,
          quantity: Number(quantity),
          unit: unit
        }]
      });
      setCreatedReliefId(res.relief_id);
      showNotification(`Donation registered! Track transparent delivery with ID: ${res.relief_id}`, 'success');
    } catch (err) {
      showNotification('Failed to pledge donation', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
          <HeartHandshake className="w-7 h-7 text-terracotta" />
          <span>Donor Transparency Portal</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate mt-1">
          Every contribution receives a unique tracking ID and verified delivery proof from warehouse to village.
        </p>
      </div>

      {/* Signature Impact Highlight Card (Directly from Hackathon Prompt) */}
      <div className="bg-gradient-to-r from-navy to-navy-900 text-ivory rounded-xl p-6 shadow-elevated border border-navy-700">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] bg-terracotta text-white font-bold px-2 py-0.5 rounded uppercase tracking-wider">
              Verified Delivery Example
            </span>
            <div className="text-xl font-bold font-mono mt-1 text-ivory">DONATION D-10284</div>
            <div className="text-sm text-slate-light mt-0.5">
              Donor: <b>Anita & Vikram Sharma</b> &bull; 500 Clean Water Bottles
            </div>
            <div className="text-xs text-slate-light mt-1">
              Destination: <b>Flood Zone B (Village A Shelter)</b> &bull; Impact: <b>~250 people supported</b>
            </div>
          </div>
          <button
            onClick={() => { setTraceIdInput('RELIEF-2026-00482'); setActiveTab('trace'); }}
            className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 transition-colors self-start sm:self-center"
          >
            <span>View Verified Timeline</span>
            <ArrowRight className="w-3.5 h-3.5 text-terracotta" />
          </button>
        </div>
      </div>

      {/* Donation Form */}
      <form onSubmit={handleSubmit} className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft space-y-5">
        <h3 className="font-bold text-base text-navy pb-2 border-b border-slate/15 flex items-center gap-2">
          <Gift className="w-4 h-4 text-terracotta" />
          <span>Pledge Relief Supplies</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-dark mb-1">Donor Full Name / Organization</label>
            <input
              type="text"
              value={donorName}
              onChange={e => setDonorName(e.target.value)}
              required
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Donor Email Address</label>
            <input
              type="email"
              value={donorEmail}
              onChange={e => setDonorEmail(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Relief Commodity Category</label>
            <select
              value={category}
              onChange={e => {
                setCategory(e.target.value);
                if (e.target.value === 'Drinking Water') setUnit('Bottles');
                else if (e.target.value === 'Food') setUnit('Packets');
                else setUnit('Kits');
              }}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-semibold"
            >
              <option value="Drinking Water">Drinking Water (Bottled / Cans)</option>
              <option value="Food">Ready-to-Eat Food Packets</option>
              <option value="Medicines">Emergency Medicine & First Aid</option>
              <option value="Sanitation">Sanitation & Hygiene Kits</option>
              <option value="Temporary Shelter">Tarpaulins & Thermal Blankets</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Quantity ({unit})</label>
            <input
              type="number"
              min="10"
              value={quantity}
              onChange={e => setQuantity(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-bold"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-semibold text-slate-dark mb-1">Notes / Target Flood Zone Preference</label>
            <input
              type="text"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>
        </div>

        {createdReliefId && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-lg text-xs flex items-center justify-between">
            <div>
              <span className="font-bold text-emerald-900">Contribution Pledged!</span>
              <div className="font-mono font-bold text-navy text-sm mt-0.5">{createdReliefId}</div>
            </div>
            <button
              type="button"
              onClick={() => { setTraceIdInput(createdReliefId); setActiveTab('trace'); }}
              className="bg-emerald-700 text-white font-bold px-3 py-1.5 rounded text-xs"
            >
              Trace Contribution Now
            </button>
          </div>
        )}

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-2.5 rounded-lg text-xs sm:text-sm transition-colors"
          >
            {submitting ? 'Registering Pledged Cargo...' : 'Confirm Relief Contribution'}
          </button>
        </div>
      </form>

    </div>
  );
};
"""
write_file("pages/DonorPortalPage.tsx", donor_code)

# 2. VolunteerDeskPage.tsx
volunteer_code = """import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { CommunityRequest } from '../types';
import api from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { CheckCircle, Users, AlertTriangle, GitMerge, XCircle, ShieldCheck, RefreshCw } from 'lucide-react';

export const VolunteerDeskPage: React.FC = () => {
  const { showNotification } = useApp();
  const [requests, setRequests] = useState<CommunityRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    api.getRequests().then(data => {
      setRequests(data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAction = async (requestId: number, action: string, duplicateOfId?: number) => {
    try {
      await api.verifyRequest(requestId, action, `Volunteer reviewed: ${action}`, duplicateOfId);
      showNotification(`Request updated to ${action}. Audited in central log.`, 'success');
      loadData();
    } catch (err) {
      showNotification('Failed to update verification', 'error');
    }
  };

  const duplicates = requests.filter(r => r.status === 'FLAGGED_DUPLICATE');
  const pending = requests.filter(r => r.status === 'PENDING');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate/20 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
            <Users className="w-7 h-7 text-terracotta" />
            <span>Volunteer Verification Desk</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate mt-1">
            Community reports triage &bull; Non-destructive duplicate detection & human-in-the-loop review
          </p>
        </div>
        <button onClick={loadData} className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Duplicate Resolution Queue */}
      <div className="bg-ivory border border-amber-300 rounded-xl p-6 shadow-soft">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-700" />
            <h3 className="font-bold text-base text-navy">Flagged Potential Duplicates ({duplicates.length})</h3>
          </div>
          <span className="text-[11px] text-amber-900 bg-amber-100 px-2.5 py-0.5 rounded font-semibold">
            NEVER AUTO-REJECTED &bull; HUMAN REVIEW REQUIRED
          </span>
        </div>

        {duplicates.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate">No flagged duplicates pending review.</div>
        ) : (
          <div className="space-y-4">
            {duplicates.map(req => {
              const verif = req.verifications[0];
              return (
                <div key={req.id} className="bg-white border border-amber-200 rounded-lg p-4 text-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate/15 pb-2 mb-2">
                    <div>
                      <span className="font-bold text-sm text-navy">{req.location_name}</span>
                      <span className="font-mono text-slate ml-2">({req.tracking_code})</span>
                    </div>
                    <span className="font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded">
                      {verif ? `${Math.round(verif.similarity_score * 100)}% Similarity` : 'High Similarity'}
                    </span>
                  </div>

                  <p className="text-slate-dark text-xs mb-2">
                    <b>Report:</b> "{req.raw_description}"
                  </p>
                  <div className="text-[11px] text-slate mb-3">
                    {verif?.notes || 'Geographic proximity and description overlap with primary cluster.'}
                  </div>

                  <div className="flex flex-wrap gap-2 pt-2 border-t border-slate/15">
                    <button
                      onClick={() => handleAction(req.id, 'APPROVED')}
                      className="bg-emerald-700 hover:bg-emerald-800 text-white font-semibold px-3 py-1.5 rounded text-xs flex items-center gap-1"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Approve as Distinct Need</span>
                    </button>
                    <button
                      onClick={() => handleAction(req.id, 'MERGED', verif?.duplicate_of_id)}
                      className="bg-navy hover:bg-navy-800 text-white font-semibold px-3 py-1.5 rounded text-xs flex items-center gap-1"
                    >
                      <GitMerge className="w-3.5 h-3.5" />
                      <span>Merge with Parent Request</span>
                    </button>
                    <button
                      onClick={() => handleAction(req.id, 'REJECTED')}
                      className="bg-slate/20 hover:bg-red-100 text-slate-dark hover:text-red-800 font-semibold px-3 py-1.5 rounded text-xs flex items-center gap-1"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Reject Invalid</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Open Pending Verification Requests */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-4">Pending Field Requests ({pending.length})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
              <tr>
                <th className="py-2.5 px-3">Location</th>
                <th className="py-2.5 px-3">Affected</th>
                <th className="py-2.5 px-3">Reporter</th>
                <th className="py-2.5 px-3">AI Score</th>
                <th className="py-2.5 px-3 text-right">Quick Triage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/15">
              {pending.slice(0, 6).map(req => (
                <tr key={req.id} className="hover:bg-ivory-50">
                  <td className="py-3 px-3">
                    <div className="font-bold text-navy">{req.location_name}</div>
                    <div className="text-[10px] font-mono text-slate">{req.tracking_code}</div>
                  </td>
                  <td className="py-3 px-3">{req.affected_people} people</td>
                  <td className="py-3 px-3">{req.reporter_name || 'Citizen'}</td>
                  <td className="py-3 px-3 font-mono font-bold text-terracotta">{Math.round(req.priority_score)}/100</td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => handleAction(req.id, 'APPROVED')}
                      className="bg-navy hover:bg-navy-800 text-white px-2.5 py-1 rounded text-xs font-semibold"
                    >
                      Verify
                    </button>
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
write_file("pages/VolunteerDeskPage.tsx", volunteer_code)

# 3. AnalyticsPage.tsx
analytics_code = """import React, { useEffect, useState } from 'react';
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
"""
write_file("pages/AnalyticsPage.tsx", analytics_code)

# 4. AuditTrailPage.tsx
audit_code = """import React, { useEffect, useState } from 'react';
import { AuditLog } from '../types';
import api from '../services/api';
import { ShieldCheck, Lock, AlertTriangle, CheckCircle2, RefreshCw, Key } from 'lucide-react';

export const AuditTrailPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [verification, setVerification] = useState<{ total_records: number; is_chain_valid: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  const loadLogs = () => {
    setLoading(true);
    api.getAuditLogs().then(data => {
      setLogs(data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleVerifyChain = async () => {
    setVerifying(true);
    try {
      const res = await api.verifyAuditIntegrity();
      setVerification(res);
    } catch (err) {
      console.error(err);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate/20 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-terracotta" />
            <span>Tamper-Evident Cryptographic Audit Trail</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate mt-1">
            Every authority approval, dispatch, and delivery state change is chained using SHA-256 block hashes
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleVerifyChain}
            disabled={verifying}
            className="bg-navy hover:bg-navy-800 text-white font-bold px-4 py-2 rounded-lg text-xs flex items-center gap-2 shadow-sm transition-colors"
          >
            <Key className="w-4 h-4 text-terracotta" />
            <span>{verifying ? 'Verifying Block Hashes...' : 'Verify Cryptographic Integrity'}</span>
          </button>
          <button onClick={loadLogs} className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Verification Certificate Banner */}
      {verification && (
        <div className={`p-5 rounded-xl border text-xs flex items-start gap-3 shadow-card ${
          verification.is_chain_valid
            ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
            : 'bg-red-50 border-red-300 text-red-950'
        }`}>
          {verification.is_chain_valid ? (
            <CheckCircle2 className="w-6 h-6 text-status-fulfilled shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-6 h-6 text-status-critical shrink-0 mt-0.5" />
          )}
          <div>
            <div className="font-bold text-sm">
              {verification.is_chain_valid ? 'Cryptographic Proof Verified: 100% Tamper-Proof' : 'Tamper Detected in Historical Chain!'}
            </div>
            <p className="mt-1 text-xs leading-relaxed">
              {verification.message}
            </p>
            <div className="font-mono text-[11px] text-slate-dark mt-1">
              Verified {verification.total_records} chained blocks against genesis block (000000...0000)
            </div>
          </div>
        </div>
      )}

      {/* Ledger Table */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-base text-navy">Audit Ledger Blocks</h3>
          <span className="text-xs text-slate font-mono">{logs.length} Blocks Recorded</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
              <tr>
                <th className="py-2.5 px-3">Block #</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Actor & Role</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Entity ID</th>
                <th className="py-2.5 px-3 font-mono">Current Block Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/15">
              {logs.map(log => (
                <tr key={log.id} className="hover:bg-ivory-50">
                  <td className="py-3 px-3 font-mono font-bold text-navy">#{log.id}</td>
                  <td className="py-3 px-3 text-slate font-mono text-[11px]">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-3 px-3">
                    <div className="font-semibold text-navy">{log.actor_name}</div>
                    <div className="text-[10px] text-slate uppercase">{log.actor_role}</div>
                  </td>
                  <td className="py-3 px-3 font-semibold text-navy">{log.action}</td>
                  <td className="py-3 px-3 font-mono text-terracotta">{log.entity_id}</td>
                  <td className="py-3 px-3 font-mono text-[10px] text-slate-dark max-w-[180px] truncate" title={log.curr_hash}>
                    {log.curr_hash}
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
write_file("pages/AuditTrailPage.tsx", audit_code)

print("DonorPortalPage, VolunteerDeskPage, AnalyticsPage, AuditTrailPage written successfully.")
