import React, { useEffect, useState } from 'react';
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

