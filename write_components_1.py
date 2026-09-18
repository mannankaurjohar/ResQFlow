import os

SRC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "src")
COMPONENTS_DIR = os.path.join(SRC_DIR, "components")
CONTEXT_DIR = os.path.join(SRC_DIR, "context")
os.makedirs(COMPONENTS_DIR, exist_ok=True)
os.makedirs(CONTEXT_DIR, exist_ok=True)

# 1. context/AppContext.tsx
context_ts = """import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, CommunityRequest } from '../types';
import api from '../services/api';

interface AppContextType {
  activeRole: UserRole;
  setActiveRole: (role: UserRole) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isEmergencyMode: boolean;
  toggleEmergencyMode: () => void;
  isEscalated: boolean;
  triggerEscalation: () => Promise<void>;
  triggerReset: () => Promise<void>;
  traceIdInput: string;
  setTraceIdInput: (id: string) => void;
  activePriorityModalRequest: CommunityRequest | null;
  setActivePriorityModalRequest: (req: CommunityRequest | null) => void;
  activeMatchModalRequest: CommunityRequest | null;
  setActiveMatchModalRequest: (req: CommunityRequest | null) => void;
  notification: { message: string; type: 'success' | 'info' | 'warning' | 'error' } | null;
  showNotification: (message: string, type?: 'success' | 'info' | 'warning' | 'error') => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeRole, setActiveRole] = useState<UserRole>('AUTHORITY');
  const [activeTab, setActiveTab] = useState<string>('landing');
  const [isEmergencyMode, setIsEmergencyMode] = useState<boolean>(false);
  const [isEscalated, setIsEscalated] = useState<boolean>(false);
  const [traceIdInput, setTraceIdInput] = useState<string>('RELIEF-2026-00482');
  const [activePriorityModalRequest, setActivePriorityModalRequest] = useState<CommunityRequest | null>(null);
  const [activeMatchModalRequest, setActiveMatchModalRequest] = useState<CommunityRequest | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'warning' | 'error' } | null>(null);

  const showNotification = (message: string, type: 'success' | 'info' | 'warning' | 'error' = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  useEffect(() => {
    api.getSimulationStatus().then(status => {
      setIsEscalated(status.is_escalated);
    }).catch(() => {});
  }, []);

  const toggleEmergencyMode = () => {
    setIsEmergencyMode(prev => {
      const next = !prev;
      showNotification(
        next ? '🚨 EMERGENCY MODE ACTIVATED: Prioritizing critical requests and shortage radar.' : 'Standard operational mode restored.',
        next ? 'warning' : 'info'
      );
      return next;
    });
  };

  const triggerEscalation = async () => {
    try {
      const res = await api.escalateSimulation();
      setIsEscalated(true);
      showNotification(res.message || 'Flood escalation simulated!', 'error');
    } catch (err) {
      showNotification('Failed to trigger simulation', 'error');
    }
  };

  const triggerReset = async () => {
    try {
      const res = await api.resetSimulation();
      setIsEscalated(false);
      showNotification(res.message || 'Simulation reset successfully', 'success');
    } catch (err) {
      showNotification('Failed to reset simulation', 'error');
    }
  };

  return (
    <AppContext.Provider value={{
      activeRole, setActiveRole,
      activeTab, setActiveTab,
      isEmergencyMode, toggleEmergencyMode,
      isEscalated, triggerEscalation, triggerReset,
      traceIdInput, setTraceIdInput,
      activePriorityModalRequest, setActivePriorityModalRequest,
      activeMatchModalRequest, setActiveMatchModalRequest,
      notification, showNotification
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
};
"""

with open(os.path.join(CONTEXT_DIR, "AppContext.tsx"), "w", encoding="utf-8") as f:
    f.write(context_ts)

# 2. components/StatusBadge.tsx
badge_ts = """import React from 'react';
import { AlertCircle, Clock, CheckCircle2, Truck, HelpCircle, ShieldAlert } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '', size = 'md' }) => {
  const s = status.toUpperCase();

  let bg = 'bg-slate-100 text-slate-dark border-slate/30';
  let icon = <HelpCircle className="w-3.5 h-3.5 mr-1 inline" />;
  let label = status;

  if (s === 'CRITICAL' || s === 'SEVERE') {
    bg = 'bg-red-50 text-status-critical border-status-critical/30';
    icon = <ShieldAlert className="w-3.5 h-3.5 mr-1 inline animate-pulse text-status-critical" />;
    label = 'Critical';
  } else if (s === 'HIGH') {
    bg = 'bg-orange-50 text-status-high border-status-high/30';
    icon = <AlertCircle className="w-3.5 h-3.5 mr-1 inline text-status-high" />;
    label = 'High Priority';
  } else if (s === 'MEDIUM' || s === 'MODERATE') {
    bg = 'bg-amber-50 text-status-medium border-status-medium/30';
    icon = <Clock className="w-3.5 h-3.5 mr-1 inline text-status-medium" />;
    label = 'Medium';
  } else if (s === 'LOW') {
    bg = 'bg-emerald-50 text-status-low border-status-low/30';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-status-low" />;
    label = 'Low Risk';
  } else if (s === 'DELIVERED' || s === 'FULFILLED') {
    bg = 'bg-emerald-50 text-status-fulfilled border-status-fulfilled/30 font-medium';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-status-fulfilled" />;
    label = 'Delivered';
  } else if (s === 'IN_TRANSIT' || s === 'DISPATCHED') {
    bg = 'bg-sky-50 text-status-transit border-status-transit/30 font-medium';
    icon = <Truck className="w-3.5 h-3.5 mr-1 inline text-status-transit" />;
    label = 'In Transit';
  } else if (s === 'ALLOCATED' || s === 'PARTIALLY_FULFILLED') {
    bg = 'bg-teal-50 text-teal-800 border-teal-300';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-teal-700" />;
    label = s === 'PARTIALLY_FULFILLED' ? 'Partially Fulfilled' : 'Allocated';
  } else if (s === 'FLAGGED_DUPLICATE') {
    bg = 'bg-amber-50 text-amber-900 border-amber-300';
    icon = <AlertCircle className="w-3.5 h-3.5 mr-1 inline text-amber-700" />;
    label = 'Duplicate Flagged';
  } else if (s === 'VERIFIED') {
    bg = 'bg-blue-50 text-blue-800 border-blue-300';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-blue-700" />;
    label = 'Verified';
  } else if (s === 'PENDING') {
    bg = 'bg-stone-100 text-slate-dark border-stone-300';
    icon = <Clock className="w-3.5 h-3.5 mr-1 inline text-slate" />;
    label = 'Pending';
  }

  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${bg} ${sizeClass} ${className}`}>
      {icon}
      {label}
    </span>
  );
};
"""

with open(os.path.join(COMPONENTS_DIR, "StatusBadge.tsx"), "w", encoding="utf-8") as f:
    f.write(badge_ts)

# 3. components/Navbar.tsx
navbar_ts = """import React from 'react';
import { useApp } from '../context/AppContext';
import {
  Shield, Waves, Radio, Package, Users, Eye,
  BarChart3, RefreshCw, AlertTriangle, ChevronDown, Check
} from 'lucide-react';
import { UserRole } from '../types';

export const Navbar: React.FC = () => {
  const {
    activeRole, setActiveRole,
    activeTab, setActiveTab,
    isEmergencyMode, toggleEmergencyMode,
    isEscalated, triggerEscalation, triggerReset
  } = useApp();

  const [roleDropdownOpen, setRoleDropdownOpen] = React.useState(false);

  const roles: { role: UserRole; title: string; desc: string }[] = [
    { role: 'AUTHORITY', title: 'Authority Command', desc: 'Disaster coordination & approvals' },
    { role: 'COMMUNITY', title: 'Affected Community', desc: 'Report needs & view relief' },
    { role: 'VOLUNTEER', title: 'Field Volunteer', desc: 'Verify requests & triage' },
    { role: 'NGO_MANAGER', title: 'NGO Coordinator', desc: 'Manage supplies & missions' },
    { role: 'WAREHOUSE_MANAGER', title: 'Warehouse Master', desc: 'Inventory batches & manifests' },
    { role: 'DONOR', title: 'Relief Donor', desc: 'Track contribution journey' },
    { role: 'ADMIN', title: 'System Administrator', desc: 'Audit chain & configuration' }
  ];

  const currentRoleObj = roles.find(r => r.role === activeRole) || roles[0];

  return (
    <header className="sticky top-0 z-40 bg-navy text-ivory border-b border-navy-700 shadow-md">
      {/* Primary Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('landing')}>
            <div className="w-10 h-10 rounded-lg bg-terracotta flex items-center justify-center shadow-inner">
              <Waves className="w-6 h-6 text-ivory" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight text-ivory font-sans">RESQFLOW AI</span>
                <span className="text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-0.5 rounded uppercase font-semibold tracking-wider">
                  Flood Relief Mode
                </span>
              </div>
              <p className="text-xs text-slate-light hidden sm:block">From community needs to verified relief delivery</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setActiveTab('landing')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'landing' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('command')}
              className={`px-3 py-2 text-sm font-medium rounded-md flex items-center space-x-1.5 transition-colors ${activeTab === 'command' ? 'bg-navy-800 text-terracotta font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              <Radio className="w-4 h-4 text-terracotta" />
              <span>Command Center</span>
            </button>
            <button
              onClick={() => setActiveTab('report')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'report' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Report Need
            </button>
            <button
              onClick={() => setActiveTab('trace')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'trace' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Trace Relief
            </button>
            <button
              onClick={() => setActiveTab('warehouse')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'warehouse' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Warehouses
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'analytics' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'audit' ? 'bg-navy-800 text-ivory font-semibold' : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'}`}
            >
              Audit Trail
            </button>
          </nav>

          {/* Right Action Controls */}
          <div className="flex items-center space-x-2.5">
            {/* Emergency Mode Toggle */}
            <button
              onClick={toggleEmergencyMode}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md border flex items-center space-x-1.5 transition-all shadow-sm ${
                isEmergencyMode
                  ? 'bg-status-critical text-white border-red-500 animate-pulse'
                  : 'bg-navy-800 text-slate-light border-slate/30 hover:border-slate hover:text-ivory'
              }`}
              title="Toggle High-Urgency Emergency View"
            >
              <AlertTriangle className={`w-3.5 h-3.5 ${isEmergencyMode ? 'text-white' : 'text-status-high'}`} />
              <span className="hidden sm:inline">{isEmergencyMode ? 'EMERGENCY ACTIVE' : 'EMERGENCY MODE'}</span>
            </button>

            {/* Simulation Triggers (Hackathon Showcase) */}
            <div className="hidden lg:flex items-center space-x-1 bg-navy-800/90 rounded-md p-1 border border-navy-700">
              <button
                onClick={triggerEscalation}
                disabled={isEscalated}
                className={`px-2.5 py-1 text-xs rounded font-medium transition-colors ${
                  isEscalated
                    ? 'bg-red-950 text-red-300 cursor-not-allowed border border-red-800'
                    : 'bg-navy-700 text-ivory hover:bg-terracotta hover:text-white'
                }`}
                title="Simulate flash flood surge & breach in Zone B"
              >
                {isEscalated ? '⚡ Flood Escalated' : 'Simulate Surge'}
              </button>
              <button
                onClick={triggerReset}
                className="p-1 text-slate-light hover:text-ivory rounded hover:bg-navy-700"
                title="Reset simulation to baseline"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* 1-Click Role Switcher */}
            <div className="relative">
              <button
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className="flex items-center space-x-2 bg-navy-800 hover:bg-navy-700 border border-slate/30 rounded-md px-3 py-1.5 text-xs font-medium text-ivory transition-colors"
              >
                <span className="w-2 h-2 rounded-full bg-terracotta"></span>
                <span className="max-w-[110px] truncate">{currentRoleObj.title}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-light" />
              </button>

              {roleDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-navy-900 border border-navy-700 rounded-lg shadow-elevated py-2 z-50">
                  <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-light border-b border-navy-800">
                    Switch Stakeholder View
                  </div>
                  {roles.map(r => (
                    <button
                      key={r.role}
                      onClick={() => {
                        setActiveRole(r.role);
                        setRoleDropdownOpen(false);
                        // Sensible auto-routing per role
                        if (r.role === 'COMMUNITY') setActiveTab('report');
                        else if (r.role === 'DONOR') setActiveTab('donor');
                        else if (r.role === 'WAREHOUSE_MANAGER') setActiveTab('warehouse');
                        else if (r.role === 'VOLUNTEER') setActiveTab('volunteer');
                        else if (r.role === 'AUTHORITY') setActiveTab('command');
                        else if (r.role === 'ADMIN') setActiveTab('audit');
                      }}
                      className="w-full text-left px-3 py-2 text-xs hover:bg-navy-800 flex items-start justify-between transition-colors"
                    >
                      <div>
                        <div className="font-semibold text-ivory">{r.title}</div>
                        <div className="text-[11px] text-slate-light">{r.desc}</div>
                      </div>
                      {activeRole === r.role && <Check className="w-4 h-4 text-terracotta shrink-0 mt-0.5" />}
                    </button>
                  ))}
                </div>
              )}
            </div>

          </div>

        </div>
      </div>
    </header>
  );
};
"""

with open(os.path.join(COMPONENTS_DIR, "Navbar.tsx"), "w", encoding="utf-8") as f:
    f.write(navbar_ts)

# 4. components/Footer.tsx
footer_ts = """import React from 'react';
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
"""

with open(os.path.join(COMPONENTS_DIR, "Footer.tsx"), "w", encoding="utf-8") as f:
    f.write(footer_ts)

# 5. components/EmergencyBanner.tsx
banner_ts = """import React from 'react';
import { useApp } from '../context/AppContext';
import { AlertOctagon, Siren, ArrowRight } from 'lucide-react';

export const EmergencyBanner: React.FC = () => {
  const { isEmergencyMode, isEscalated, setActiveTab } = useApp();

  if (!isEmergencyMode && !isEscalated) return null;

  return (
    <div className="bg-gradient-to-r from-red-950 via-status-critical to-red-900 text-white px-4 py-2.5 shadow-md border-b border-red-800">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs sm:text-sm">
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-5 h-5 animate-pulse text-amber-300 shrink-0" />
          <span className="font-bold tracking-wide">
            {isEscalated ? '🚨 FLASH FLOOD SURGE IN PROGRESS: Zone B Delta breached 3.2m water level. Priority queue escalated.' : '⚠️ EMERGENCY RESPONSE PROTOCOL ACTIVE: High-density critical requests elevated.'}
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('command')}
            className="bg-white/15 hover:bg-white/25 text-white font-medium px-3 py-1 rounded text-xs transition-colors flex items-center space-x-1"
          >
            <span>Open Command Map</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
"""

with open(os.path.join(COMPONENTS_DIR, "EmergencyBanner.tsx"), "w", encoding="utf-8") as f:
    f.write(banner_ts)

print("AppContext, StatusBadge, Navbar, Footer, EmergencyBanner written successfully.")
