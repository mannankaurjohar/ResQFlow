import React, { useEffect, useState } from 'react';
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

