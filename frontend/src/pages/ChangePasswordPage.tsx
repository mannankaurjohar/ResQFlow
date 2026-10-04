import React, {
  useState
} from 'react';

import { useApp } from '../context/AppContext';
import api from '../services/api';

const ChangePasswordPage: React.FC = () => {
  const {
    setActiveTab,
    setActiveRole,
    currentUser,
    showNotification
  } = useApp();

  const [
    currentPassword,
    setCurrentPassword
  ] = useState('');

  const [
    newPassword,
    setNewPassword
  ] = useState('');

  const [
    confirmPassword,
    setConfirmPassword
  ] = useState('');

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setError('');

    if (!currentPassword) {
      setError(
        'Please enter your current password.'
      );
      return;
    }

    if (newPassword.length < 8) {
      setError(
        'New password must be at least 8 characters.'
      );
      return;
    }

    if (
      newPassword !==
      confirmPassword
    ) {
      setError(
        'New passwords do not match.'
      );
      return;
    }

    if (
      currentPassword ===
      newPassword
    ) {
      setError(
        'New password must be different from current password.'
      );
      return;
    }

    try {
      setLoading(true);

      const updatedUser =
        await api.changePassword(
          currentPassword,
          newPassword
        );

      setActiveRole(
        updatedUser.role
      );

      showNotification(
        'Password changed successfully.',
        'success'
      );

      switch (updatedUser.role) {
        case 'EMERGENCY_COORDINATOR':
          setActiveTab('command');
          break;

        case 'COMMUNITY':
          setActiveTab('report');
          break;

        case 'VOLUNTEER':
          setActiveTab('volunteer');
          break;

        case 'NGO_MANAGER':
        case 'WAREHOUSE_MANAGER':
          setActiveTab('warehouse');
          break;

        case 'DONOR':
          setActiveTab('donor');
          break;

        case 'ADMIN':
        default:
          setActiveTab('landing');
          break;
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to change password.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] bg-ivory flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">

        <div className="bg-white rounded-2xl shadow-sm border border-navy/10 p-8">

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-navy">
              Change Password
            </h1>

            <p className="text-slate-500 mt-2">
              Please create a new password before continuing.
            </p>

            {currentUser && (
              <p className="text-sm text-slate-500 mt-3">
                Account: {currentUser.username}
              </p>
            )}
          </div>

          {error && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            <div>
              <label
                htmlFor="current-password"
                className="block text-sm font-medium text-navy mb-2"
              >
                Current Password
              </label>

              <input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={e =>
                  setCurrentPassword(
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="current-password"
              />
            </div>

            <div>
              <label
                htmlFor="new-password"
                className="block text-sm font-medium text-navy mb-2"
              >
                New Password
              </label>

              <input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={e =>
                  setNewPassword(
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="new-password"
              />

              <p className="text-xs text-slate-500 mt-2">
                Minimum 8 characters.
              </p>
            </div>

            <div>
              <label
                htmlFor="confirm-password"
                className="block text-sm font-medium text-navy mb-2"
              >
                Confirm New Password
              </label>

              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={e =>
                  setConfirmPassword(
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-navy px-4 py-3 font-semibold text-white transition hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? 'Changing Password...'
                : 'Change Password'}
            </button>

          </form>

        </div>

      </div>
    </div>
  );
};

export default ChangePasswordPage;