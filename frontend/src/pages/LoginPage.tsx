import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserRole } from '../types';

const LoginPage: React.FC = () => {
  const { login, setActiveTab } = useApp();

  const [username, setUsername] =
    useState('');

  const [password, setPassword] =
    useState('');

  const [role, setRole] =
    useState<UserRole>('COMMUNITY');

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setError('');

    if (
      !username.trim() ||
      !password
    ) {
      setError(
        'Please enter your Login ID and password.'
      );
      return;
    }

    try {
      setLoading(true);

      await login(
        username.trim(),
        password,
        role
      );

      // AppContext handles navigation
      // after login.
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Login failed. Please check your credentials.'
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
              Login
            </h1>

            <p className="text-slate-500 mt-2">
              Sign in to your ResQFlow account
            </p>
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
                htmlFor="username"
                className="block text-sm font-medium text-navy mb-2"
              >
                Login ID
              </label>

              <input
                id="username"
                type="text"
                value={username}
                onChange={e =>
                  setUsername(
                    e.target.value
                  )
                }
                placeholder="Enter your Login ID"
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="username"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-navy mb-2"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={e =>
                  setPassword(
                    e.target.value
                  )
                }
                placeholder="Enter your password"
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="current-password"
              />
            </div>

            <div>
              <label
                htmlFor="role"
                className="block text-sm font-medium text-navy mb-2"
              >
                Role
              </label>

              <select
                id="role"
                value={role}
                onChange={e =>
                  setRole(
                    e.target.value as UserRole
                  )
                }
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
              >
                <option value="COMMUNITY">
                  Community
                </option>
                <option value="ADMIN">
                  Administrator
                </option>

                <option value="EMERGENCY_COORDINATOR">
                  Emergency Coordinator
                </option>
                <option value="RESPONSE_UNIT_OPERATOR">
  Response Unit Operator
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

                
              </select>
            </div>

            <button
  type="submit"
  disabled={loading}
  className="w-full rounded-lg bg-navy px-4 py-3 font-semibold text-white transition hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-60"
>
  {loading
    ? 'Signing in...'
    : 'Sign In'}
</button>

<div className="text-center pt-2">
  <p className="text-sm text-slate-500">
    Don't have an account?{' '}
    <button
      type="button"
      onClick={() => {
  setActiveTab('signup');
}}
      className="font-semibold text-terracotta hover:underline"
    >
      Sign Up
    </button>
  </p>
</div>

          </form>

        </div>
      </div>
    </div>
  );
};

export default LoginPage;