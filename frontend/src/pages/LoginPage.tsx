import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import { LanguageSelector } from '../components/LanguageSelector';
import { UserRole } from '../types';

const LoginPage: React.FC = () => {
  const { login, setActiveTab } = useApp();
  const { t } = useTranslation();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('COMMUNITY');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password) {
      setError(t('login.errorRequired'));
      return;
    }

    try {
      setLoading(true);
      await login(username.trim(), password, role);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('login.errorFailed')
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] bg-ivory flex items-center justify-center px-4 py-10 relative">
      <div className="w-full max-w-md">
        {/* Top bar with back to overview & language switcher */}
        <div className="flex items-center justify-between mb-4 px-1">
          <button
            type="button"
            onClick={() => setActiveTab('landing')}
            className="text-xs text-slate-500 hover:text-navy font-semibold transition-colors"
          >
            ← {t('common.back')}
          </button>
          <LanguageSelector variant="standalone" />
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-navy/10 p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-navy">
              {t('login.title')}
            </h1>

            <p className="text-slate-500 mt-2">
              {t('login.subtitle')}
            </p>
          </div>

          {error && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('login.loginIdLabel')}
              </label>

              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder={t('login.loginIdPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="username"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('login.passwordLabel')}
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder={t('login.passwordPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="current-password"
              />
            </div>

            <div>
              <label
                htmlFor="role"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('login.roleLabel')}
              </label>

              <select
                id="role"
                value={role}
                onChange={e => setRole(e.target.value as UserRole)}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
              >
                <option value="COMMUNITY">
                  {t('role.community')}
                </option>
                <option value="ADMIN">
                  {t('role.admin')}
                </option>
                <option value="EMERGENCY_COORDINATOR">
                  {t('role.emergencyCoordinator')}
                </option>
                <option value="RESPONSE_UNIT_OPERATOR">
                  {t('role.responseUnitOperator')}
                </option>
                <option value="VOLUNTEER">
                  {t('role.volunteer')}
                </option>
                <option value="NGO_MANAGER">
                  {t('role.ngoManager')}
                </option>
                <option value="WAREHOUSE_MANAGER">
                  {t('role.warehouseManager')}
                </option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-navy px-4 py-3 font-semibold text-white transition hover:bg-navy/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? t('login.signingIn')
                : t('login.signInBtn')}
            </button>

            <div className="text-center pt-2">
              <p className="text-sm text-slate-500">
                {t('login.noAccount')}{' '}
                <button
                  type="button"
                  onClick={() => setActiveTab('signup')}
                  className="font-semibold text-terracotta hover:underline"
                >
                  {t('login.signUpLink')}
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