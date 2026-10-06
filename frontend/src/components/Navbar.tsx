import React from 'react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import { LanguageSelector } from './LanguageSelector';
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
    currentUser,
    logout
  } = useApp();

  const { t } = useTranslation();
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
                  {t('common.appName')}
                </span>

                <span className="hidden md:inline-block text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-0.5 rounded uppercase font-semibold tracking-wider">
                  {t('common.floodReliefMode')}
                </span>
              </div>

              <p className="text-xs text-slate-light hidden sm:block">
                {t('common.tagline')}
              </p>
            </div>
          </div>

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
                  {t('nav.adminDashboard')}
                </button>

                <button
                  onClick={() => setActiveTab('admin-users')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'admin-users'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.userManagement')}
                </button>

                <button
                  onClick={() => setActiveTab('audit')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'audit'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.auditTrail')}
                </button>

                <button
                  onClick={() => setActiveTab('admin-settings')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'admin-settings'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.systemSettings')}
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
                      {t('nav.overview')}
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
                  {t('nav.liveAlerts')}
                </button>

                <button
                  onClick={() => setActiveTab('evacuation')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'evacuation'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.requestEvacuation')}
                </button>

                <button
                  onClick={() => setActiveTab('report')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'report'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.requestSupplies')}
                </button>

                <button
                  onClick={() => setActiveTab('trace')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'trace'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.traceRelief')}
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
                      {t('nav.donation')}
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
                  {t('nav.analytics')}
                </button>

                <button
                  onClick={() => navigateTo('my-requests')}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'my-requests'
                      ? 'bg-navy-800 text-ivory font-semibold'
                      : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                  }`}
                >
                  {t('nav.myRequests')}
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
                      {t('nav.tasks')}
                    </button>
                  )}

                {/* EMERGENCY COORDINATOR */}
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
                        <span>{t('nav.commandCenter')}</span>
                      </button>

                      <button
                        onClick={() => setActiveTab('response-units')}
                        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          activeTab === 'response-units'
                            ? 'bg-navy-800 text-ivory font-semibold'
                            : 'text-slate-light hover:text-ivory hover:bg-navy-800/60'
                        }`}
                      >
                        {t('nav.responseUnits')}
                      </button>
                    </>
                  )}
              </>
            )}
          </nav>

          {/* ================= DESKTOP RIGHT CONTROLS ================= */}
          <div className="hidden md:flex items-center space-x-2.5">
            {/* Language Selector */}
            <LanguageSelector />

            {/* Authentication */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <div className="px-3 py-1.5 text-xs font-medium text-ivory bg-navy-800 border border-slate/30 rounded-md">
                  {currentUser?.full_name || currentUser?.username}
                </div>

                <button
                  onClick={() => {
                    logout();
                    setActiveTab('landing');
                  }}
                  className="px-3 py-1.5 text-xs font-semibold rounded-md bg-terracotta text-ivory hover:bg-terracotta/90 transition-colors"
                >
                  {t('common.logout')}
                </button>
              </div>
            ) : (
              <button
                onClick={() => setActiveTab('login')}
                className="px-3 py-1.5 text-xs font-semibold rounded-md bg-terracotta text-ivory hover:bg-terracotta/90 transition-colors"
              >
                {t('common.login')}
              </button>
            )}
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
          <div className="md:hidden relative z-[2000] bg-navy border-t border-navy-700 py-3">

            {/* Language & Flood Relief Mode */}
            <div className="mb-3 px-2 flex items-center justify-between gap-2">
              <div className="inline-flex items-center text-[10px] bg-navy-800 text-slate-light border border-slate/40 px-2 py-1 rounded uppercase font-semibold tracking-wider">
                {t('common.floodReliefMode')}
              </div>
              <LanguageSelector />
            </div>

            {/* Navigation */}
            <div className="space-y-1">
              {isAuthenticated && currentUser?.role === 'ADMIN' ? (
                <>
                  <button
                    onClick={() => navigateTo('admin-dashboard')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.adminDashboard')}
                  </button>

                  <button
                    onClick={() => navigateTo('admin-users')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.userManagement')}
                  </button>

                  <button
                    onClick={() => navigateTo('audit')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.auditTrail')}
                  </button>

                  <button
                    onClick={() => navigateTo('admin-settings')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.systemSettings')}
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => navigateTo('landing')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.overview')}
                  </button>

                  <button
                    onClick={() => navigateTo('flood-alerts')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.liveAlerts')}
                  </button>

                  <button
                    onClick={() => navigateTo('evacuation')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.requestEvacuation')}
                  </button>

                  <button
                    onClick={() => navigateTo('report')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.requestSupplies')}
                  </button>

                  <button
                    onClick={() => navigateTo('trace')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.traceRelief')}
                  </button>

                  <button
                    onClick={() => navigateTo('donor')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.donation')}
                  </button>

                  <button
                    onClick={() => navigateTo('analytics')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.analytics')}
                  </button>

                  <button
                    onClick={() => navigateTo('my-requests')}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                  >
                    {t('nav.myRequests')}
                  </button>

                  {isAuthenticated &&
                    currentUser?.role === 'RESPONSE_UNIT_OPERATOR' && (
                      <button
                        onClick={() => navigateTo('response-tasks')}
                        className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                      >
                        {t('nav.tasks')}
                      </button>
                    )}

                  {isAuthenticated &&
                    currentUser?.role === 'EMERGENCY_COORDINATOR' && (
                      <>
                        <button
                          onClick={() => navigateTo('command')}
                          className="w-full text-left px-3 py-2.5 rounded-md text-sm text-terracotta hover:bg-navy-800"
                        >
                          {t('nav.commandCenter')}
                        </button>

                        <button
                          onClick={() => navigateTo('response-units')}
                          className="w-full text-left px-3 py-2.5 rounded-md text-sm text-slate-light hover:text-ivory hover:bg-navy-800"
                        >
                          {t('nav.responseUnits')}
                        </button>
                      </>
                    )}
                </>
              )}
            </div>

            {/* Mobile Authentication */}
            <div className="border-t border-navy-700 mt-3 pt-3">
              {isAuthenticated ? (
                <div className="space-y-2">
                  <div className="px-3 py-2.5 bg-navy-800 border border-slate/30 rounded-md text-sm text-ivory">
                    {currentUser?.full_name || currentUser?.username}
                  </div>

                  <button
                    onClick={() => {
                      logout();
                      setActiveTab('landing');
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-2.5 rounded-md text-sm font-semibold bg-terracotta text-ivory"
                  >
                    {t('common.logout')}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => navigateTo('login')}
                  className="w-full text-left px-3 py-2.5 rounded-md text-sm font-semibold bg-terracotta text-ivory"
                >
                  {t('common.login')}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};