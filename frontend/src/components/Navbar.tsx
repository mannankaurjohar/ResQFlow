import React from 'react';
import { useApp } from '../context/AppContext';
import {
  Waves,
  Radio,

  Menu,
  X
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    
    isAuthenticated,
    activeRole,
    currentUser,
    logout
  } = useApp();

  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const navigateTo = (tab: string) => {
    setActiveTab(tab);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-[9999] bg-navy text-ivory border-b border-navy-700 shadow-md">

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
                  ResQFlow
                </span>

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
          {/* ================= DESKTOP NAVIGATION ================= */}
<nav className="hidden md:flex items-center space-x-1">

  {isAuthenticated && currentUser?.role === 'ADMIN' ? (
    <>
      {/* ADMIN NAVIGATION */}

      <button
        onClick={() => setActiveTab('admin-dashboard')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'admin-dashboard'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        Admin Dashboard
      </button>

      <button
        onClick={() => setActiveTab('admin-users')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'admin-users'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        User Management
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

      <button
        onClick={() => setActiveTab('admin-settings')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'admin-settings'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        System Settings
      </button>
    </>
  ) : (
    <>
      {/* PUBLIC NAVIGATION */}

      {currentUser?.role !== 'EMERGENCY_COORDINATOR' &&
 currentUser?.role !== 'RESPONSE_UNIT_OPERATOR' && (
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
)}

      <button
        onClick={() => setActiveTab('flood-alerts')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'flood-alerts'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        Live Alerts
      </button>

      <button
        onClick={() => setActiveTab('evacuation')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'evacuation'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        Request Evacuation
      </button>

      <button
        onClick={() => setActiveTab('report')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'report'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        Request Supplies
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

      {currentUser?.role !== 'EMERGENCY_COORDINATOR' &&
 currentUser?.role !== 'RESPONSE_UNIT_OPERATOR' && (
  <button
    onClick={() => setActiveTab('donor')}
    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
      activeTab === 'donor'
        ? 'bg-navy-800 text-ivory font-semibold'
        : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
    }`}
  >
    Donation
  </button>
)}

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
        onClick={() => navigateTo('my-requests')}
        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          activeTab === 'my-requests'
            ? 'bg-navy-800 text-ivory font-semibold'
            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
        }`}
      >
        My Requests
      </button>
{/* RESPONSE UNIT OPERATOR */}

{isAuthenticated &&
 currentUser?.role === 'RESPONSE_UNIT_OPERATOR' && (
  <button
    onClick={() => setActiveTab('response-tasks')}
    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
      activeTab === 'response-tasks'
        ? 'bg-navy-800 text-ivory font-semibold'
        : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
    }`}
  >
    Tasks
  </button>
)}


      {/* OTHER AUTHENTICATED ROLES */}

      {isAuthenticated &&
 currentUser?.role === 'EMERGENCY_COORDINATOR' && (
  <>
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

{currentUser?.role === 'EMERGENCY_COORDINATOR' && (
  <button
    onClick={() => setActiveTab('response-units')}
    className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
      activeTab === 'response-units'
        ? 'bg-navy-800 text-ivory font-semibold'
        : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
    }`}
  >
    Response Units
  </button>
)}

        </>
      )}
    </>
  )}

</nav>
          {/* ================= DESKTOP RIGHT CONTROLS ================= */}
          <div className="hidden md:flex items-center space-x-2.5">

           

            {/* Authentication */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2">

                <div className="px-3 py-1.5 text-xs font-medium text-ivory bg-navy-800 border border-slate/30 rounded-md">
                  {currentUser?.full_name ||
                    currentUser?.username}
                </div>

                <button
                  onClick={() => {
                    logout();
                    setActiveTab('landing');
                  }}
                  className="px-3 py-1.5 text-xs font-semibold rounded-md bg-terracotta text-ivory hover:bg-terracotta/90 transition-colors"
                >
                  Logout
                </button>

              </div>
            ) : (
              <button
                onClick={() => setActiveTab('login')}
                className="px-3 py-1.5 text-xs font-semibold rounded-md bg-terracotta text-ivory hover:bg-terracotta/90 transition-colors"
              >
                Login
              </button>
            )}

          </div>

          {/* ================= MOBILE MENU BUTTON ================= */}
          <button
            onClick={() =>
              setMobileMenuOpen(!mobileMenuOpen)
            }
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
          <div className="md:hidden relative z-[2000] bg-navy border-t border-navy-700 py-3">

            {/* Flood Relief Mode */}
            <div className="mb-3 px-2">
              <div className="inline-flex items-center text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-1 rounded uppercase font-semibold tracking-wider">
                Flood Relief Mode
              </div>
            </div>

            {/* Navigation */}
           {/* Navigation */}
<div className="space-y-1">

  {isAuthenticated && currentUser?.role === 'ADMIN' ? (
    <>
      <button
        onClick={() => navigateTo('admin-dashboard')}
        className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
      >
        Admin Dashboard
      </button>

      <button
        onClick={() => navigateTo('admin-users')}
        className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
      >
        User Management
      </button>

      <button
        onClick={() => navigateTo('audit')}
        className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
      >
        Audit Trail
      </button>

      <button
        onClick={() => navigateTo('admin-settings')}
        className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
      >
        System Settings
      </button>
    </>
  ) : (
    <>
      {/* KEEP YOUR EXISTING PUBLIC + OTHER ROLE NAVIGATION HERE */}
    </>
  )}

</div>

            

            {/* Mobile Authentication */}
            <div className="border-t border-navy-700 mt-3 pt-3">

              {isAuthenticated ? (
                <div className="space-y-2">

                  <div className="px-3 py-2.5 bg-navy-800 border border-slate/30 rounded-md text-sm text-ivory">
                    {currentUser?.full_name ||
                      currentUser?.username}
                  </div>

                  <button
                    onClick={() => {
                      logout();
                      setActiveTab('landing');
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm font-semibold bg-terracotta text-ivory"
                  >
                    Logout
                  </button>

                </div>
              ) : (
                <button
                  onClick={() => navigateTo('login')}
                  className="w-full text-left px-3 py-2.5 rounded-md text-sm font-semibold bg-terracotta text-ivory"
                >
                  Login
                </button>
              )}

            </div>

          </div>
        )}

      </div>
    </header>
  );
};