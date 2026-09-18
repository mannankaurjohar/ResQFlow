import React, { useEffect, useState } from 'react';
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
