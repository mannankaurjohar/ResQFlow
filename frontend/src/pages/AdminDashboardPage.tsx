import React, { useEffect, useState } from 'react';
import {
  Users,
  UserCheck,
  ShieldCheck,
  Building2,
  Server,
  Database,
  LockKeyhole,
  Radio,
  BrainCircuit,
  ArrowRight,
  Activity,
  Settings,
  FileText
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
const AdminDashboardPage: React.FC = () => {
  const { setActiveTab } = useApp();
  const [dashboard, setDashboard] = useState<{
    total_users: number;
    active_users: number;
    total_roles: number;
    total_organizations: number;
    role_distribution: Record<string, number>;
  } | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError('');

        const data = await api.getAdminDashboard();

        setDashboard(data);
      } catch (err) {
        console.error(
          'Failed to load admin dashboard:',
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load dashboard'
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);
  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 pb-12">

      {/* ================= HEADER ================= */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-terracotta font-semibold">
            System Administration
          </p>

          <h1 className="text-2xl sm:text-3xl font-bold text-navy mt-1">
            Admin Dashboard
          </h1>

          <p className="text-sm text-slate-500 mt-1">
            Platform administration, user management and system health.
          </p>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-green-500" />
          <span className="text-slate-600">
            System Operational
          </span>
        </div>
      </div>

      {/* ================= PLATFORM OVERVIEW ================= */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-5 h-5 text-terracotta" />
          <h2 className="text-lg font-semibold text-navy">
            Platform Overview
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

          {/* Total Users */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  Total Users
                </p>

                <p className="text-3xl font-bold text-navy mt-2">
                  {loading ? '...' : dashboard?.total_users ?? 0}
                </p>

                <p className="text-xs text-slate-400 mt-1">
                  From user database
                </p>
              </div>

              <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center">
                <Users className="w-5 h-5 text-navy" />
              </div>
            </div>
          </div>

          {/* Active Users */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  Active Users
                </p>

                <p className="text-3xl font-bold text-navy mt-2">
                  {loading ? '...' : dashboard?.active_users ?? 0}
                </p>

                <p className="text-xs text-slate-400 mt-1">
                  Currently active accounts
                </p>
              </div>

              <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
                <UserCheck className="w-5 h-5 text-green-600" />
              </div>
            </div>
          </div>

          {/* Roles */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  User Roles
                </p>

                <p className="text-3xl font-bold text-navy mt-2">
                  {loading ? '...' : dashboard?.total_roles ?? 0}
                </p>

                <p className="text-xs text-slate-400 mt-1">
                  Configured platform roles
                </p>
              </div>

              <div className="w-10 h-10 rounded-lg bg-terracotta/10 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-terracotta" />
              </div>
            </div>
          </div>

          {/* Organizations */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">
                  Organizations
                </p>

                <p className="text-3xl font-bold text-navy mt-2">
                  {loading ? '...' : dashboard?.total_organizations ?? 0}
                </p>

                <p className="text-xs text-slate-400 mt-1">
                  Registered organizations
                </p>
              </div>

              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </div>

        </div>
      </section>
{/* ================= USER DISTRIBUTION ================= */}
<section>
  <div className="flex items-center gap-2 mb-3">
    <Users className="w-5 h-5 text-terracotta" />

    <h2 className="text-lg font-semibold text-navy">
      User Distribution
    </h2>
  </div>

  <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">

    {loading ? (
      <p className="text-sm text-slate-500">
        Loading user distribution...
      </p>
    ) : dashboard ? (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">

        {Object.entries(
          dashboard.role_distribution
        ).map(([role, count]) => {

          const label = role
            .replace(/_/g, ' ')
            .toLowerCase()
            .replace(/\b\w/g, char =>
              char.toUpperCase()
            );

          return (
            <div
              key={role}
              className="flex items-center justify-between px-4 py-3 bg-slate-50 rounded-lg border border-slate-100"
            >
              <span className="text-sm text-slate-600">
                {label}
              </span>

              <span className="font-bold text-navy">
                {count}
              </span>
            </div>
          );
        })}

      </div>
    ) : (
      <p className="text-sm text-red-600">
        {error || 'Unable to load user data.'}
      </p>
    )}

  </div>
</section>
      {/* ================= SYSTEM HEALTH ================= */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Server className="w-5 h-5 text-terracotta" />
          <h2 className="text-lg font-semibold text-navy">
            System Health
          </h2>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm divide-y divide-slate-100">

          <SystemStatusRow
            icon={<Server className="w-5 h-5" />}
            name="Backend API"
            description="Application server and API endpoints"
            status="Operational"
          />

          <SystemStatusRow
            icon={<Database className="w-5 h-5" />}
            name="Database"
            description="ResQFlow application database"
            status="Connected"
          />

          <SystemStatusRow
            icon={<LockKeyhole className="w-5 h-5" />}
            name="Authentication"
            description="User authentication and access control"
            status="Operational"
          />

          <SystemStatusRow
            icon={<Radio className="w-5 h-5" />}
            name="Flood Data Source"
            description="External flood monitoring data"
            status="Connected"
          />

          <SystemStatusRow
            icon={<BrainCircuit className="w-5 h-5" />}
            name="AI Services"
            description="AI-powered request analysis services"
            status="Operational"
          />

        </div>
      </section>

      {/* ================= ADMIN ACTIONS ================= */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Settings className="w-5 h-5 text-terracotta" />
          <h2 className="text-lg font-semibold text-navy">
            Administration
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* User Management */}
          <AdminActionCard
            icon={<Users className="w-5 h-5" />}
            title="User Management"
            description="Manage users, roles, account status and access."
            buttonText="Manage Users"
            onClick={() => setActiveTab('admin-users')}
          />

          {/* Audit Trail */}
          <AdminActionCard
            icon={<FileText className="w-5 h-5" />}
            title="Audit Trail"
            description="Review administrative and system activity."
            buttonText="View Audit Trail"
            onClick={() => setActiveTab('audit')}
          />

          {/* System Settings */}
          <AdminActionCard
            icon={<Settings className="w-5 h-5" />}
            title="System Settings"
            description="Configure platform-wide system settings."
            buttonText="Open Settings"
            onClick={() => setActiveTab('admin-settings')}
          />

        </div>
      </section>

      {/* ================= SECURITY NOTICE ================= */}
      <section className="bg-navy rounded-xl p-5 sm:p-6 text-ivory">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-5 h-5 text-terracotta" />
          </div>

          <div>
            <h3 className="font-semibold">
              Administrative Access
            </h3>

            <p className="text-sm text-slate-light mt-1 leading-relaxed">
              Administrative actions can affect users, permissions and
              platform configuration. All sensitive administrative activity
              should be recorded in the audit trail.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
};


/* =========================================================
   SYSTEM STATUS ROW
========================================================= */

interface SystemStatusRowProps {
  icon: React.ReactNode;
  name: string;
  description: string;
  status: string;
}

const SystemStatusRow: React.FC<SystemStatusRowProps> = ({
  icon,
  name,
  description,
  status
}) => {
  return (
    <div className="flex items-center justify-between gap-4 p-4 sm:p-5">

      <div className="flex items-center gap-4 min-w-0">

        <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center text-navy shrink-0">
          {icon}
        </div>

        <div className="min-w-0">
          <p className="font-medium text-navy">
            {name}
          </p>

          <p className="text-xs sm:text-sm text-slate-500 truncate">
            {description}
          </p>
        </div>

      </div>

      <div className="flex items-center gap-2 shrink-0">
        <span className="w-2 h-2 rounded-full bg-green-500" />

        <span className="text-xs sm:text-sm font-medium text-green-700">
          {status}
        </span>
      </div>

    </div>
  );
};


/* =========================================================
   ADMIN ACTION CARD
========================================================= */

interface AdminActionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  buttonText: string;
  onClick: () => void;
}

const AdminActionCard: React.FC<AdminActionCardProps> = ({
  icon,
  title,
  description,
  buttonText,
  onClick
}) => {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">

      <div className="w-10 h-10 rounded-lg bg-navy-50 text-navy flex items-center justify-center">
        {icon}
      </div>

      <h3 className="font-semibold text-navy mt-4">
        {title}
      </h3>

      <p className="text-sm text-slate-500 mt-1 min-h-[40px]">
        {description}
      </p>

      <button
        type="button"
        onClick={onClick}
        className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-terracotta hover:text-terracotta/80 transition-colors"
      >
        {buttonText}
        <ArrowRight className="w-4 h-4" />
      </button>

    </div>
  );
};

export default AdminDashboardPage;