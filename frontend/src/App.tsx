import React, { useEffect } from 'react';
import AdminUserManagementPage from './pages/AdminUserManagementPage';
import {
  AppProvider,
  useApp
} from './context/AppContext';
import FloodAlertsPage from './pages/FloodAlertsPage';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { EmergencyBanner } from './components/EmergencyBanner';
import { ExplainPriorityModal } from './components/ExplainPriorityModal';
import { AiMatchingModal } from './components/AiMatchingModal';
import AdminDashboardPage from './pages/AdminDashboardPage';
import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import AdminSettingsPage from './pages/AdminSettingsPage';
import { LandingPage } from './pages/LandingPage';
import { AuthorityCommandPage } from './pages/AuthorityCommandPage';
import { CommunityReportPage } from './pages/CommunityReportPage';
import { TraceReliefPage } from './pages/TraceReliefPage';
import { NgoWarehousePage } from './pages/NgoWarehousePage';
import { DonorPortalPage } from './pages/DonorPortalPage';
import { VolunteerDeskPage } from './pages/VolunteerDeskPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AuditTrailPage } from './pages/AuditTrailPage';
import EvacuationRequestPage from './pages/EvacuationRequestPage';
import MyRequestsPage from './pages/MyRequestsPage';
import SignUpPage from './pages/SignUpPage';
import ResponseUnitsPage from './pages/ResponseUnitsPage';
import ResponseAssignmentPage from './pages/ResponseAssignmentPage';
import ResponseUnitTasksPage from './pages/ResponseUnitTasksPage';
import JudgeModePage from './pages/JudgeModePage';
const AppContent: React.FC = () => {
  const {
  activeTab,
  notification,
  judgeMode,
  currentUser
} = useApp();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: 'instant'
    });
  }, [activeTab]);

  if (activeTab === 'login') {
    return <LoginPage />;
  }

  if (
    activeTab === 'change-password'
  ) {
    return <ChangePasswordPage />;
  }
if (judgeMode && activeTab === 'judge-mode') {
  return <JudgeModePage />;
}
  return (
    <div className="min-h-screen flex flex-col bg-ivory text-navy font-sans antialiased">

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

      <Navbar />

      <EmergencyBanner />

      <main
  className={`flex-1 ${
    judgeMode && activeTab !== 'judge-mode'
      ? 'pb-32'
      : ''
  }`}
>
 {judgeMode && activeTab !== 'judge-mode' && (
    <JudgeModePage />
  )}
        {activeTab === 'landing' && (
          <LandingPage />
        )}
        {activeTab === 'flood-alerts' && (
  <FloodAlertsPage />
)}
{activeTab === 'command' &&
  currentUser?.role === 'EMERGENCY_COORDINATOR' && (
    <AuthorityCommandPage />
  )}
{activeTab === 'response-units' && (
  <ResponseUnitsPage />
)}
{activeTab === 'response-assignment' && (
  <ResponseAssignmentPage />
)}
        {activeTab === 'report' && (
          <CommunityReportPage />
        )}

        {activeTab === 'trace' && (
          <TraceReliefPage />
        )}
{activeTab === 'admin-settings' && (
  <AdminSettingsPage />
)}
        {activeTab === 'warehouse' && (
          <NgoWarehousePage />
        )}
{activeTab === 'my-requests' && (
  <MyRequestsPage />
)}
        {activeTab === 'donor' && (
          <DonorPortalPage />
        )}
{activeTab === 'evacuation' && <EvacuationRequestPage />}
        {activeTab === 'volunteer' && (
          <VolunteerDeskPage />
        )}
{activeTab === 'signup' && (
  <SignUpPage />
)}
        {activeTab === 'analytics' && (
          <AnalyticsPage />
        )}
{activeTab === 'admin-dashboard' && (
  <AdminDashboardPage />
)}
        {activeTab === 'audit' && (
          <AuditTrailPage />
        )}
        {activeTab === 'response-tasks' && (
  <ResponseUnitTasksPage />
)}
{activeTab === 'admin-users' && (
  <AdminUserManagementPage />
)}

      </main>

      <ExplainPriorityModal />
      <AiMatchingModal />

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