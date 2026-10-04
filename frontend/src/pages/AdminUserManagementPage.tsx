
import React, { useEffect, useState } from 'react';
import { Copy, RefreshCw, UserPlus } from 'lucide-react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
import { User, UserRole } from '../types';

interface GeneratedCredentials {
  login_id: string;
  temporary_password: string;
  full_name: string;
}

const AdminUserManagementPage: React.FC = () => {
  const {
    currentUser,
    showNotification,
     judgeMode
  } = useApp();

  const [users, setUsers] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [creating, setCreating] = useState(false);
  const [resettingUserId, setResettingUserId] =
    useState<number | null>(null);

  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] =
    useState<UserRole>('VOLUNTEER');

  const [organizationId, setOrganizationId] =
    useState<number | ''>('');

  const [unitType, setUnitType] = useState('');

  const [
    generatedCredentials,
    setGeneratedCredentials
  ] = useState<GeneratedCredentials | null>(null);

  const loadUsers = async () => {
    try {
      setLoadingUsers(true);

      const data = await api.getWorkers();

      setUsers(data);
    } catch (error) {
      showNotification(
        error instanceof Error
          ? error.message
          : 'Failed to load users',
        'error'
      );
    } finally {
      setLoadingUsers(false);
    }
  };

  useEffect(() => {
    if (currentUser?.role === 'ADMIN'|| judgeMode) {
      loadUsers();
    }
  }, [currentUser, judgeMode]);

  if (currentUser?.role !== 'ADMIN' && !judgeMode) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
          <h2 className="text-lg font-bold text-red-900">
            Access Denied
          </h2>

          <p className="mt-2 text-sm text-red-700">
            Only administrators can manage user accounts.
          </p>
        </div>
      </div>
    );
  }

  const handleCreateUser = async (
    event: React.FormEvent
  ) => {
    event.preventDefault();

    if (!fullName.trim()) {
      showNotification(
        "Please enter the user's full name.",
        'warning'
      );
      return;
    }

    if (
      role === 'RESPONSE_UNIT_OPERATOR' &&
      !unitType
    ) {
      showNotification(
        'Please select a response unit type.',
        'warning'
      );
      return;
    }

    try {
      setCreating(true);
      setGeneratedCredentials(null);

      const result = await api.createWorker({
  full_name: fullName.trim(),
  phone: phone.trim() || undefined,
  role,
  unit_type:
    role === 'RESPONSE_UNIT_OPERATOR'
      ? unitType
      : undefined,
 organization_id:
  organizationId === ''
    ? undefined
    : Number(organizationId)
});

      setGeneratedCredentials({
        login_id: result.login_id,
        temporary_password:
          result.temporary_password,
        full_name: result.user.full_name
      });

      setFullName('');
      setPhone('');
      setRole('VOLUNTEER');
      setOrganizationId('');
      setUnitType('');

      await loadUsers();

      showNotification(
        'User account created successfully.',
        'success'
      );
    } catch (error) {
      showNotification(
        error instanceof Error
          ? error.message
          : 'Failed to create user',
        'error'
      );
    } finally {
      setCreating(false);
    }
  };

  const handleResetPassword = async (
    user: User
  ) => {
    const confirmed = window.confirm(
      `Reset the password for ${user.full_name}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setResettingUserId(user.id);

      const result =
        await api.resetWorkerPassword(
          user.id
        );

      setGeneratedCredentials({
        login_id: result.login_id,
        temporary_password:
          result.temporary_password,
        full_name: result.user.full_name
      });

      showNotification(
        'Temporary password generated successfully.',
        'success'
      );
    } catch (error) {
      showNotification(
        error instanceof Error
          ? error.message
          : 'Failed to reset password',
        'error'
      );
    } finally {
      setResettingUserId(null);
    }
  };

  const copyCredentials = async () => {
    if (!generatedCredentials) {
      return;
    }

    const text =
      `ResQFlow Account\n\n` +
      `Name: ${generatedCredentials.full_name}\n` +
      `Login ID: ${generatedCredentials.login_id}\n` +
      `Temporary Password: ${generatedCredentials.temporary_password}`;

    try {
      await navigator.clipboard.writeText(text);

      showNotification(
        'Credentials copied to clipboard.',
        'success'
      );
    } catch {
      showNotification(
        'Unable to copy credentials.',
        'error'
      );
    }
  };

  const roleLabel = (userRole: UserRole) => {
    switch (userRole) {
      case 'ADMIN':
        return 'Administrator';

      case 'EMERGENCY_COORDINATOR':
        return 'Emergency Coordinator';

      case 'COMMUNITY':
        return 'Community';

      case 'VOLUNTEER':
        return 'Volunteer';

      case 'NGO_MANAGER':
        return 'NGO Manager';

      case 'WAREHOUSE_MANAGER':
        return 'Warehouse Manager';

      case 'DONOR':
        return 'Donor';

      case 'RESPONSE_UNIT_OPERATOR':
        return 'Response Unit Operator';

      default:
        return userRole;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">

      {/* Header */}
      <div className="mb-6">
        <p className="text-xs font-bold uppercase tracking-wider text-terracotta">
          Administration
        </p>

        <h1 className="mt-1 text-2xl sm:text-3xl font-bold text-navy">
          User Management
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Create ResQFlow accounts and manage temporary passwords.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Create User */}
        <section className="lg:col-span-1">
          <div className="bg-white border border-navy/10 rounded-2xl p-6 shadow-sm">

            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-navy text-white flex items-center justify-center">
                <UserPlus size={20} />
              </div>

              <div>
                <h2 className="font-bold text-navy">
                  Create User
                </h2>

                <p className="text-xs text-slate-500">
                  Generate a new account
                </p>
              </div>
            </div>

            <form
              onSubmit={handleCreateUser}
              className="space-y-4"
            >

              {/* Full Name */}
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">
                  Full Name
                </label>

                <input
                  type="text"
                  value={fullName}
                  onChange={e =>
                    setFullName(e.target.value)
                  }
                  placeholder="Enter full name"
                  className="w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">
                  Phone
                </label>

                <input
                  type="tel"
                  value={phone}
                  onChange={e =>
                    setPhone(e.target.value)
                  }
                  placeholder="Optional"
                  className="w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta"
                />
              </div>

              {/* Role */}
              <div>
                <label className="block text-sm font-semibold text-navy mb-1.5">
                  Role
                </label>

                <select
                  value={role}
                  onChange={e => {
                    const selectedRole =
                      e.target.value as UserRole;

                    setRole(selectedRole);

                    if (
                      selectedRole !==
                      'RESPONSE_UNIT_OPERATOR'
                    ) {
                      setUnitType('');
                    }
                  }}
                  className="w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta bg-white"
                >
                  <option value="EMERGENCY_COORDINATOR">
                    Emergency Coordinator
                  </option>

                  <option value="COMMUNITY">
                    Community
                  </option>

                  <option value="VOLUNTEER">
                    Volunteer
                  </option>

                  <option value="NGO_MANAGER">
                    NGO Manager
                  </option>

                  <option value="WAREHOUSE_MANAGER">
                    Warehouse Manager
                  </option>

                  <option value="RESPONSE_UNIT_OPERATOR">
                    Response Unit Operator
                  </option>
                </select>
              </div>

              {/* Response Unit Type */}
              {role === 'RESPONSE_UNIT_OPERATOR' && (
                <div>
                  <label className="block text-sm font-semibold text-navy mb-1.5">
                    Response Unit Type
                  </label>

                  <select
                    value={unitType}
                    onChange={e =>
                      setUnitType(e.target.value)
                    }
                    required
                    className="w-full rounded-xl border border-navy/15 px-3 py-2.5 text-sm outline-none focus:border-terracotta focus:ring-1 focus:ring-terracotta bg-white"
                  >
                    <option value="">
                      Select response unit type
                    </option>

                    <option value="SDRF">
                      SDRF
                    </option>

                    <option value="NDRF">
                      NDRF
                    </option>

                    <option value="Fire & Rescue">
                      Fire & Rescue
                    </option>

                    <option value="Police / Emergency">
                      Police / Emergency
                    </option>

                    <option value="Aapda Mitra / Authorized Local Team">
                      Aapda Mitra / Authorized Local Team
                    </option>

                    <option value="Other Authorized Unit">
                      Other Authorized Unit
                    </option>
                  </select>
                </div>
              )}

              {/* Generate Account */}
              <button
                type="submit"
                disabled={creating}
                className="w-full rounded-xl bg-navy text-white py-3 text-sm font-bold hover:bg-navy/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {creating
                  ? 'Generating Account...'
                  : 'Generate Account'}
              </button>

            </form>
          </div>
        </section>

        {/* Generated Credentials */}
        <section className="lg:col-span-2">

          {generatedCredentials ? (
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6">

              <div className="flex items-start justify-between gap-4 mb-5">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                    Account Credentials
                  </p>

                  <h2 className="text-xl font-bold text-emerald-950 mt-1">
                    Account Ready
                  </h2>

                  <p className="text-sm text-emerald-800 mt-1">
                    Give these credentials to the user securely.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={copyCredentials}
                  className="inline-flex items-center gap-2 rounded-xl bg-white border border-emerald-200 px-3 py-2 text-sm font-semibold text-emerald-900 hover:bg-emerald-100"
                >
                  <Copy size={16} />
                  Copy
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

                <div className="bg-white rounded-xl border border-emerald-200 p-4">
                  <p className="text-xs text-slate-500 mb-1">
                    Login ID
                  </p>

                  <p className="font-mono font-bold text-navy break-all">
                    {generatedCredentials.login_id}
                  </p>
                </div>

                <div className="bg-white rounded-xl border border-emerald-200 p-4">
                  <p className="text-xs text-slate-500 mb-1">
                    Temporary Password
                  </p>

                  <p className="font-mono font-bold text-navy break-all">
                    {generatedCredentials.temporary_password}
                  </p>
                </div>

              </div>

              <div className="mt-4 rounded-xl bg-white/70 border border-emerald-200 px-4 py-3">
                <p className="text-xs text-emerald-900">
                  The user will be required to change this
                  temporary password after their first login.
                </p>
              </div>

            </div>
          ) : (
            <div className="bg-white border border-navy/10 rounded-2xl p-6 min-h-[220px] flex items-center justify-center text-center">
              <div>
                <div className="w-12 h-12 rounded-full bg-slate-100 mx-auto flex items-center justify-center text-slate-400">
                  <UserPlus size={22} />
                </div>

                <h2 className="mt-4 font-bold text-navy">
                  No credentials generated
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Create a user to generate Login ID and
                  temporary password.
                </p>
              </div>
            </div>
          )}

        </section>
      </div>

      {/* Existing Users */}
      <section className="mt-6 bg-white border border-navy/10 rounded-2xl overflow-hidden shadow-sm">

        <div className="px-6 py-5 border-b border-navy/10 flex items-center justify-between gap-4">

          <div>
            <h2 className="font-bold text-navy">
              Existing Users
            </h2>

            <p className="text-xs text-slate-500 mt-1">
              Manage accounts and reset temporary passwords.
            </p>
          </div>

          <button
            type="button"
            onClick={loadUsers}
            disabled={loadingUsers}
            className="p-2 rounded-lg border border-navy/10 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            title="Refresh users"
          >
            <RefreshCw
              size={17}
              className={
                loadingUsers
                  ? 'animate-spin'
                  : ''
              }
            />
          </button>

        </div>

        {loadingUsers ? (
          <div className="px-6 py-10 text-center text-sm text-slate-500">
            Loading users...
          </div>
        ) : users.length === 0 ? (
          <div className="px-6 py-10 text-center text-sm text-slate-500">
            No users found.
          </div>
        ) : (
          <div className="overflow-x-auto">

            <table className="w-full text-sm">

              <thead>
                <tr className="bg-slate-50 border-b border-navy/10">
                  <th className="text-left px-6 py-3 font-semibold text-navy">
                    User
                  </th>

                  <th className="text-left px-6 py-3 font-semibold text-navy">
                    Login ID
                  </th>

                  <th className="text-left px-6 py-3 font-semibold text-navy">
                    Role
                  </th>

                  <th className="text-right px-6 py-3 font-semibold text-navy">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-navy/5">

                {users.map(user => (
                  <tr key={user.id}>

                    <td className="px-6 py-4">
                      <div className="font-semibold text-navy">
                        {user.full_name}
                      </div>

                      <div className="text-xs text-slate-500">
                        {user.email}
                      </div>
                    </td>

                    <td className="px-6 py-4 font-mono text-xs text-slate-700">
                      {user.username}
                    </td>

                    <td className="px-6 py-4">
                      <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        {roleLabel(user.role)}
                      </span>

                      {user.role === 'RESPONSE_UNIT_OPERATOR' &&
                        user.unit_type && (
                          <span className="ml-2 inline-flex rounded-full bg-terracotta/10 px-2.5 py-1 text-xs font-semibold text-terracotta">
                            {user.unit_type}
                          </span>
                        )}
                    </td>

                    <td className="px-6 py-4 text-right">
                      {currentUser && user.id === currentUser.id ? (
                        <span className="text-xs text-slate-400">
                          Current account
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() =>
                            handleResetPassword(user)
                          }
                          disabled={
                            resettingUserId === user.id
                          }
                          className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-800 hover:bg-amber-100 disabled:opacity-50"
                        >
                          {resettingUserId ===
                          user.id
                            ? 'Generating...'
                            : 'Reset Password'}
                        </button>
                      )}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>
        )}

      </section>

    </div>
  );
};

export default AdminUserManagementPage;
