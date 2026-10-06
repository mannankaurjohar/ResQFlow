import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import api from '../services/api';

const SignUpPage: React.FC = () => {
  const { setActiveTab } = useApp();
  const { t } = useTranslation();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [notifications, setNotifications] = useState(false);
  const [error, setError] = useState('');

  const [loginId, setLoginId] = useState('');
  const [accountCreated, setAccountCreated] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (
      !fullName.trim() ||
      !email.trim() ||
      !phone.trim() ||
      !location.trim() ||
      !password ||
      !confirmPassword
    ) {
      setError(t('signup.errFields'));
      return;
    }

    if (password.length < 8) {
      setError(t('signup.errPassLen'));
      return;
    }

    if (password !== confirmPassword) {
      setError(t('signup.errPassMatch'));
      return;
    }

    if (!notifications) {
      setError(t('signup.errNotifications'));
      return;
    }

    try {
      const result = await api.communitySignup({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        location: location.trim(),
        password
      });

      setLoginId(result.login_id);
      setAccountCreated(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('signup.errFields')
      );
    }
  };

  // Success screen
  if (accountCreated) {
    return (
      <div className="min-h-[calc(100vh-80px)] bg-ivory flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-sm border border-navy/10 p-8">
            <div className="text-center mb-8">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 border border-emerald-200">
                <span className="text-2xl text-emerald-600">✓</span>
              </div>

              <h1 className="text-3xl font-bold text-navy">
                {t('signup.successTitle')}
              </h1>

              <p className="text-slate-500 mt-2">
                {t('signup.successSubtitle')}
              </p>
            </div>

            <div className="rounded-xl border border-navy/10 bg-ivory p-5 text-center">
              <p className="text-sm font-medium text-slate-500">
                {t('signup.yourLoginId')}
              </p>

              <p className="mt-2 text-2xl font-bold tracking-wider text-navy">
                {loginId}
              </p>

              <p className="mt-3 text-xs text-slate-500">
                {t('signup.successSubtitle')}
              </p>
            </div>

            <button
              type="button"
              onClick={() => setActiveTab('login')}
              className="w-full mt-6 rounded-lg bg-navy px-4 py-3 font-semibold text-white transition hover:bg-navy/90"
            >
              {t('signup.proceedToLogin')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-ivory flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-sm border border-navy/10 p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-navy">
              {t('signup.title')}
            </h1>

            <p className="text-slate-500 mt-2">
              {t('signup.subtitle')}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label
                htmlFor="fullName"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.fullName')}
              </label>

              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder={t('signup.fullNamePlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="name"
              />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.email')}
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder={t('signup.emailPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="email"
              />
            </div>

            {/* Phone */}
            <div>
              <label
                htmlFor="phone"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.phone')}
              </label>

              <input
                id="phone"
                type="tel"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder={t('signup.phonePlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="tel"
              />
            </div>

            {/* Location */}
            <div>
              <label
                htmlFor="location"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.location')}
              </label>

              <input
                id="location"
                type="text"
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder={t('signup.locationPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="address-level2"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.password')}
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder={t('signup.passwordPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="new-password"
              />
            </div>

            {/* Confirm Password */}
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-navy mb-2"
              >
                {t('signup.confirmPassword')}
              </label>

              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder={t('signup.confirmPasswordPlaceholder')}
                className="w-full rounded-lg border border-navy/15 bg-white px-4 py-3 text-navy outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/10"
                autoComplete="new-password"
              />
            </div>

            {/* Notification Consent */}
            <div className="rounded-lg border border-navy/10 bg-ivory px-4 py-3">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications}
                  onChange={e => setNotifications(e.target.checked)}
                  className="mt-1 h-4 w-4 accent-terracotta"
                />

                <span className="text-sm text-slate-600">
                  {t('signup.notifyCheckbox')}
                </span>
              </label>
            </div>

            {/* Error message */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full rounded-lg bg-navy px-4 py-3 font-semibold text-white transition hover:bg-navy/90"
            >
              {t('signup.createBtn')}
            </button>

            <p className="text-center text-sm text-slate-500 pt-2">
              {t('signup.hasAccount')}{' '}
              <button
                type="button"
                onClick={() => setActiveTab('login')}
                className="font-semibold text-terracotta hover:underline"
              >
                {t('signup.loginLink')}
              </button>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;