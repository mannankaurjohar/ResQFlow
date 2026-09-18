import React from 'react';
import { useApp } from '../context/AppContext';
import {
  Waves, Radio, AlertTriangle, ChevronDown, Check, Menu, X
} from 'lucide-react';
import { UserRole } from '../types';

export const Navbar: React.FC = () => {
  const {
    activeRole, setActiveRole,
    activeTab, setActiveTab,
    isEmergencyMode, toggleEmergencyMode
  } = useApp();

  const [roleDropdownOpen, setRoleDropdownOpen] = React.useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

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

  const navigateTo = (tab: any) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 bg-navy text-ivory border-b border-navy-700 shadow-md">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* ================= DESKTOP / MOBILE TOP BAR ================= */}
        <div className="flex items-center justify-between min-h-20 py-2">

          {/* Logo & Brand */}
          <div
            className="flex items-center space-x-3 cursor-pointer min-w-0"
            onClick={() => navigateTo('landing')}
          >
            <div className="w-10 h-10 rounded-lg bg-terracotta flex items-center justify-center shadow-inner shrink-0">
              <Waves className="w-6 h-6 text-ivory" />
            </div>

            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight text-ivory font-sans whitespace-nowrap">
                  RESQFLOW AI
                </span>

                {/* Hidden on mobile so it doesn't squeeze the navbar */}
                <span className="hidden md:inline-block text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-0.5 rounded uppercase font-semibold tracking-wider">
                  Flood Relief Mode
                </span>
              </div>

              <p className="text-xs text-slate-light hidden sm:block">
                From community needs to verified relief delivery
              </p>
            </div>
          </div>


          {/* ================= DESKTOP NAVIGATION ================= */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setActiveTab('landing')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'landing'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Overview
            </button>

            <button
              onClick={() => setActiveTab('command')}
              className={`px-3 py-2 text-sm font-medium rounded-md flex items-center space-x-1.5 transition-colors ${
                activeTab === 'command'
                  ? 'bg-navy-800 text-terracotta font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              <Radio className="w-4 h-4 text-terracotta" />
              <span>Command Center</span>
            </button>

            <button
              onClick={() => setActiveTab('report')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'report'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Report Need
            </button>

            <button
              onClick={() => setActiveTab('trace')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'trace'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Trace Relief
            </button>

            <button
              onClick={() => setActiveTab('warehouse')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'warehouse'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Warehouses
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Analytics
            </button>

            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'audit'
                  ? 'bg-navy-800 text-ivory font-semibold'
                  : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
              }`}
            >
              Audit Trail
            </button>
          </nav>


          {/* ================= DESKTOP RIGHT CONTROLS ================= */}
          <div className="hidden md:flex items-center space-x-2.5">

            {/* Emergency Mode */}
            <button
              onClick={toggleEmergencyMode}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md border flex items-center space-x-1.5 transition-all shadow-sm ${
                isEmergencyMode
                  ? 'bg-status-critical text-white border-red-500 animate-pulse'
                  : 'bg-navy-800 text-slate-light border-slate/30 hover:border-slate hover:text-ivory'
              }`}
              title="Toggle High-Urgency Emergency View"
            >
              <AlertTriangle
                className={`w-3.5 h-3.5 ${
                  isEmergencyMode ? 'text-white' : 'text-status-high'
                }`}
              />

              <span>
                {isEmergencyMode ? 'EMERGENCY ACTIVE' : 'EMERGENCY MODE'}
              </span>
            </button>


            {/* Role Switcher */}
            <div className="relative">
              <button
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className="flex items-center space-x-2 bg-navy-800 hover:bg-navy-700 border border-slate/30 rounded-md px-3 py-1.5 text-xs font-medium text-ivory transition-colors"
              >
                <span className="w-2 h-2 rounded-full bg-terracotta"></span>

                <span className="max-w-[110px] truncate">
                  {currentRoleObj.title}
                </span>

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
                        <div className="font-semibold text-ivory">
                          {r.title}
                        </div>

                        <div className="text-[11px] text-slate-light">
                          {r.desc}
                        </div>
                      </div>

                      {activeRole === r.role && (
                        <Check className="w-4 h-4 text-terracotta shrink-0 mt-0.5" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>


          {/* ================= MOBILE MENU BUTTON ================= */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden w-10 h-10 flex items-center justify-center rounded-lg bg-navy-800 border border-slate/30 text-ivory hover:bg-navy-700 transition-colors shrink-0"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>

        </div>


        {/* ================= MOBILE MENU ================= */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-navy-700 py-3">

            {/* Flood Relief Mode */}
            <div className="mb-3 px-2">
              <div className="inline-flex items-center text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-1 rounded uppercase font-semibold tracking-wider">
                Flood Relief Mode
              </div>
            </div>


            {/* Navigation */}
            <div className="space-y-1">

              <button
                onClick={() => navigateTo('landing')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Overview
              </button>

              <button
                onClick={() => navigateTo('command')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800 flex items-center gap-2"
              >
                <Radio className="w-4 h-4 text-terracotta" />
                Command Center
              </button>

              <button
                onClick={() => navigateTo('report')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Report Need
              </button>

              <button
                onClick={() => navigateTo('trace')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Trace Relief
              </button>

              <button
                onClick={() => navigateTo('warehouse')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Warehouses
              </button>

              <button
                onClick={() => navigateTo('analytics')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Analytics
              </button>

              <button
                onClick={() => navigateTo('audit')}
                className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
              >
                Audit Trail
              </button>
            </div>


            {/* Emergency Mode */}
            <div className="border-t border-navy-700 mt-3 pt-3">

              <button
                onClick={toggleEmergencyMode}
                className={`w-full px-3 py-2.5 rounded-md border flex items-center gap-2 text-sm font-semibold transition-all ${
                  isEmergencyMode
                    ? 'bg-status-critical text-white border-red-500'
                    : 'bg-navy-800 text-slate-light border-slate/30'
                }`}
              >
                <AlertTriangle
                  className={`w-4 h-4 ${
                    isEmergencyMode ? 'text-white' : 'text-status-high'
                  }`}
                />

                {isEmergencyMode
                  ? 'EMERGENCY ACTIVE'
                  : 'EMERGENCY MODE'}
              </button>
            </div>


            {/* Mobile Role Selector */}
            <div className="mt-2 relative">

              <button
                onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
                className="w-full flex items-center justify-between bg-navy-800 border border-slate/30 rounded-md px-3 py-2.5 text-sm text-ivory"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="w-2 h-2 rounded-full bg-terracotta shrink-0"></span>

                  <span className="truncate">
                    {currentRoleObj.title}
                  </span>
                </div>

                <ChevronDown className="w-4 h-4 text-slate-light shrink-0" />
              </button>

              {roleDropdownOpen && (
                <div className="mt-2 bg-navy-900 border border-navy-700 rounded-lg shadow-elevated py-2">

                  <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-light border-b border-navy-800">
                    Switch Stakeholder View
                  </div>

                  {roles.map(r => (
                    <button
                      key={r.role}
                      onClick={() => {
                        setActiveRole(r.role);
                        setRoleDropdownOpen(false);

                        if (r.role === 'COMMUNITY') setActiveTab('report');
                        else if (r.role === 'DONOR') setActiveTab('donor');
                        else if (r.role === 'WAREHOUSE_MANAGER') setActiveTab('warehouse');
                        else if (r.role === 'VOLUNTEER') setActiveTab('volunteer');
                        else if (r.role === 'AUTHORITY') setActiveTab('command');
                        else if (r.role === 'ADMIN') setActiveTab('audit');

                        setMobileMenuOpen(false);
                      }}
                      className="w-full text-left px-3 py-2.5 hover:bg-navy-800 flex items-start justify-between"
                    >
                      <div>
                        <div className="font-semibold text-ivory text-sm">
                          {r.title}
                        </div>

                        <div className="text-[11px] text-slate-light">
                          {r.desc}
                        </div>
                      </div>

                      {activeRole === r.role && (
                        <Check className="w-4 h-4 text-terracotta shrink-0 mt-0.5" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </header>
  );
};