import React, { useEffect } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { EmergencyBanner } from './components/EmergencyBanner';
import { ExplainPriorityModal } from './components/ExplainPriorityModal';
import { AiMatchingModal } from './components/AiMatchingModal';

import { LandingPage } from './pages/LandingPage';
import { AuthorityCommandPage } from './pages/AuthorityCommandPage';
import { CommunityReportPage } from './pages/CommunityReportPage';
import { TraceReliefPage } from './pages/TraceReliefPage';
import { NgoWarehousePage } from './pages/NgoWarehousePage';
import { DonorPortalPage } from './pages/DonorPortalPage';
import { VolunteerDeskPage } from './pages/VolunteerDeskPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AuditTrailPage } from './pages/AuditTrailPage';

const AppContent: React.FC = () => {
  const { activeTab, notification } = useApp();

  // Scroll to the top whenever the user changes to another page
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [activeTab]);

  return (
    <div className="min-h-screen flex flex-col bg-ivory text-navy font-sans antialiased">
      {/* Toast Notification Alert Banner */}
      {notification && (
        <div
          className={`fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-elevated border text-xs font-semibold max-w-md animate-in slide-in-from-bottom-5 duration-200 ${
            notification.type === 'error'
              ? 'bg-red-50 text-red-900 border-red-300'
              : notification.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border-emerald-300'
              : notification.type === 'warning'
              ? 'bg-amber-50 text-amber-900 border-amber-300'
              : 'bg-navy text-ivory border-navy-700'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Top Navbar */}
      <Navbar />

      {/* Emergency Mode Notification Banner */}
      <EmergencyBanner />

      {/* Main Routed Content View */}
      <main className="flex-1 py-4">
        {activeTab === 'landing' && <LandingPage />}
        {activeTab === 'command' && <AuthorityCommandPage />}
        {activeTab === 'report' && <CommunityReportPage />}
        {activeTab === 'trace' && <TraceReliefPage />}
        {activeTab === 'warehouse' && <NgoWarehousePage />}
        {activeTab === 'donor' && <DonorPortalPage />}
        {activeTab === 'volunteer' && <VolunteerDeskPage />}
        {activeTab === 'analytics' && <AnalyticsPage />}
        {activeTab === 'audit' && <AuditTrailPage />}
      </main>

      {/* Modals */}
      <ExplainPriorityModal />
      <AiMatchingModal />

      {/* Humanitarian Footer */}
      <Footer />
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
