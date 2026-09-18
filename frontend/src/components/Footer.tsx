import React from 'react';
import { Waves, Shield, HeartHandshake, MapPin } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-navy text-ivory border-t border-navy-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2.5 mb-3">
              <div className="w-8 h-8 rounded bg-terracotta flex items-center justify-center">
                <Waves className="w-5 h-5 text-ivory" />
              </div>
              <span className="font-extrabold text-lg tracking-tight">RESQFLOW AI</span>
            </div>
            <p className="text-slate-light text-sm max-w-md leading-relaxed mb-4">
              “Know what is needed. Know where it is needed. Know where the resources went.”
            </p>
            <p className="text-xs text-slate max-w-md">
              ResQFlow AI connects community needs with relief resources using explainable AI, GIS intelligence and transparent delivery tracking.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-light mb-3">Platform Principles</h4>
            <ul className="space-y-2 text-xs text-slate-light">
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">1.</span>
                <span>Right Resource</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">2.</span>
                <span>Right Place & Time</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">3.</span>
                <span>Explainable Priority</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">4.</span>
                <span>Full Traceability</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-light mb-3">Emergency Coordination</h4>
            <p className="text-xs text-slate-light leading-relaxed mb-2">
              National Disaster Response Framework (NDRF) & State Emergency Operations Center integration node.
            </p>
            <div className="text-xs text-slate border-t border-navy-800 pt-2">
              Disaster Mode: <span className="text-amber-400 font-semibold">FLOOD RELIEF ACTIVE</span>
            </div>
          </div>

        </div>

        <div className="border-t border-navy-800 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate">
          <div>© 2026 ResQFlow AI. Open humanitarian coordination technology.</div>
          <div className="mt-2 sm:mt-0 flex items-center space-x-4">
            <span>SHA-256 Tamper-Evident Ledger Active</span>
            <span>Zero External API Critical Dependencies</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
