import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Waves, Radio, FileText, Search, ArrowRight,
  Cpu, MapPin, Truck, AlertTriangle, Eye, Compass
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { setActiveTab, setTraceIdInput, triggerEscalation, isEscalated } = useApp();
  const [searchInput, setSearchInput] = useState('RELIEF-2026-00482');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setTraceIdInput(searchInput.trim());
      setActiveTab('trace');
    }
  };

  return (
    <div className="space-y-16 pb-12">

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 bg-gradient-to-b from-navy to-navy-900 text-ivory rounded-2xl shadow-elevated px-6 sm:px-10 lg:px-14 mx-auto max-w-7xl mt-4 border border-navy-700">
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#D97450_1px,transparent_1px)] [background-size:24px_24px]"></div>

        {/* Expanded content area - alignment fix only */}
        <div className="relative z-10 w-full max-w-6xl">

          <div className="inline-flex items-center space-x-2 bg-navy-800 border border-slate/30 px-3 py-1 rounded-full text-xs font-semibold text-slate-light mb-6">
            <span className="w-2 h-2 rounded-full bg-terracotta animate-pulse"></span>
            <span>Active Flood Response Coordination System</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-ivory font-sans leading-tight">
            ResQFlow
          </h1>

          <p className="text-xl sm:text-2xl font-medium text-terracotta mt-2">
            From community needs to verified relief delivery.
          </p>

          <p className="text-base sm:text-lg text-slate-light mt-4 leading-relaxed font-normal max-w-5xl">
            An AI-powered flood-relief coordination platform that identifies urgent community needs,
            intelligently connects them with available resources, and provides transparent end-to-end relief tracking.
          </p>

          {/* Primary Action Buttons */}
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              onClick={() => setActiveTab('command')}
              className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <Radio className="w-4 h-4" />
              <span>View Relief Operations</span>
            </button>

            <button
              onClick={() => setActiveTab('report')}
              className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <FileText className="w-4 h-4 text-terracotta" />
              <span>Report a Need</span>
            </button>
          </div>

          {/* Direct Relief Tracker Quick Bar */}
          <div className="mt-10 pt-8 border-t border-navy-800 max-w-4xl">
            <div className="text-xs font-semibold text-slate-light uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5 text-terracotta" />
              <span>Transparent Relief Package Tracker</span>
            </div>

            <form onSubmit={handleSearch} className="flex gap-2 w-full">
              <input
                type="text"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                placeholder="Enter Relief ID (e.g. RELIEF-2026-00482 or D-10284)"
                className="flex-1 min-w-0 bg-navy-800 border border-slate/40 text-ivory placeholder-slate rounded-lg px-4 py-2.5 text-xs sm:text-sm font-mono focus:outline-none focus:border-terracotta"
              />

              <button
                type="submit"
                className="bg-navy-700 hover:bg-terracotta text-ivory font-bold px-5 py-2.5 rounded-lg text-xs transition-colors shrink-0"
              >
                Track Journey
              </button>
            </form>

            <p className="text-[11px] text-slate mt-1.5">
              Public verification: Try demo signature ID <b>RELIEF-2026-00482</b> (500 Water Bottles &bull; Zone B)
            </p>
          </div>

        </div>
      </section>

      

      {/* 5 Core Questions Answered Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
            Answering Five Questions Immediately
          </h2>
          <p className="text-slate text-sm mt-2">
            The system connects community needs directly with physical response capacity without delays or duplicate confusion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">1</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHO needs help?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Identifies stranded populations and vulnerable demographics (elderly, infants, pregnant mothers).
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">2</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHAT do they need?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Extracts precise quantities of drinking water, rations, first aid, baby care, or thermal shelter.
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-terracotta text-white flex items-center justify-center font-bold text-xs mb-3">3</div>
            <h3 className="font-bold text-sm text-navy mb-1">HOW URGENT is it?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Explainable AI priority engine calculates transparent 0-100 scores with audited factor points.
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">4</div>
            <h3 className="font-bold text-sm text-navy mb-1">WHERE from?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              Multi-objective AI matching analyzes warehouse proximity, batch expiry, and flooded road bypasses.
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs mb-3">5</div>
            <h3 className="font-bold text-sm text-navy mb-1">HAS IT REACHED?</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              End-to-end transparent delivery tracking with verified digital handover signature & photo proof.
            </p>
          </div>

        </div>
      </section>

      {/* How It Works Flow */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="bg-ivory-100 border border-slate/20 rounded-2xl p-8 shadow-card">

          <div className="text-center max-w-xl mx-auto mb-8">
            <h3 className="text-xl font-bold text-navy">
              The End-to-End Humanitarian Pipeline
            </h3>
            <p className="text-xs text-slate mt-1">
              From community distress voice to sealed proof of delivery
            </p>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center">

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 1</div>
              <div className="font-semibold text-navy text-sm">Natural Need Report</div>
              <div className="text-[11px] text-slate mt-0.5">AI entity parsing</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 2</div>
              <div className="font-semibold text-navy text-sm">AI Prioritization</div>
              <div className="text-[11px] text-slate mt-0.5">Explainable points matrix</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 3</div>
              <div className="font-semibold text-navy text-sm">Resource Matching</div>
              <div className="text-[11px] text-slate mt-0.5">Depots & capacity</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 4</div>
              <div className="font-semibold text-navy text-sm">Human Approval</div>
              <div className="text-[11px] text-slate mt-0.5">Authority manifest lock</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 5</div>
              <div className="font-semibold text-navy text-sm">Delivery & Trace</div>
              <div className="text-[11px] text-slate mt-0.5">8-step transparent journey</div>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
};
