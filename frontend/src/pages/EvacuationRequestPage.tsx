import React, { useState } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ClipboardList,
  MapPin,
  Phone,
  Users,
  Navigation,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import { LocationPicker } from '../components/LocationPicker';

export const EvacuationRequestPage: React.FC = () => {
  const { setActiveTab } = useApp();
  const { t } = useTranslation();

  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');

  const [locationName, setLocationName] = useState('');
  const [locationLatitude, setLocationLatitude] =
    useState<number | null>(null);
  const [locationLongitude, setLocationLongitude] =
    useState<number | null>(null);

  const [people, setPeople] = useState('1');
  const [children, setChildren] = useState('0');
  const [elderly, setElderly] = useState('0');
  const [disabled, setDisabled] = useState('0');

  const [situation, setSituation] = useState('');
  const [mobility, setMobility] = useState('');
  const [medicalEmergency, setMedicalEmergency] = useState(false);
  const [additionalInfo, setAdditionalInfo] = useState('');

  const [submitted, setSubmitted] = useState(false);
  const [requestId, setRequestId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const situationOptions = [
    { value: 'Trapped by floodwater', key: 'evac.situation.trapped' },
    { value: 'Water level is rapidly rising', key: 'evac.situation.rising' },
    { value: 'Area is becoming isolated', key: 'evac.situation.isolated' },
    { value: 'Building is unsafe', key: 'evac.situation.unsafe' },
    { value: 'Roads / routes are blocked', key: 'evac.situation.blocked' },
    { value: 'Immediate evacuation required', key: 'evac.situation.immediate' },
  ];

  const mobilityOptions = [
    { value: 'Can move independently', key: 'evac.mobility.independent' },
    { value: 'Need physical assistance', key: 'evac.mobility.assistance' },
    { value: 'Cannot move without assistance', key: 'evac.mobility.cannotMove' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim() || !phone.trim()) {
      alert(t('evac.errContact'));
      return;
    }

    if (
      locationLatitude === null ||
      locationLongitude === null ||
      !locationName.trim()
    ) {
      alert(t('evac.errLocation'));
      return;
    }

    if (!situation) {
      alert(t('evac.errSituation'));
      return;
    }

    if (!mobility) {
      alert(t('evac.errMobility'));
      return;
    }

    try {
      setSubmitting(true);
      const response = await fetch(
        'http://127.0.0.1:8000/api/requests/citizen',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            request_type: 'EVACUATION',

            reporter_name: name.trim(),
            reporter_phone: phone.trim(),

            location_name: locationName.trim(),
            latitude: locationLatitude,
            longitude: locationLongitude,

            affected_people: Number(people),
            children: Number(children),
            elderly: Number(elderly),

            situation_flags: [situation],

            medical_emergency: medicalEmergency,

            mobility_assistance:
              mobility === 'Can move independently'
                ? 0
                : mobility === 'Need physical assistance'
                  ? 1
                  : 2,

            immediate_danger:
              situation === 'Immediate evacuation required'
                ? 'YES'
                : 'NOT_SURE',

            additional_information: [
              `Mobility assistance: ${mobility}`,
              `Persons with disabilities: ${disabled}`,
              additionalInfo.trim(),
            ]
              .filter(Boolean)
              .join(' | '),

            communication_method: 'INTERNET',
            communication_status: 'RECEIVED',
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === 'string'
            ? data.detail
            : JSON.stringify(data?.detail || 'Failed to submit evacuation request')
        );
      }

      setRequestId(data.tracking_code);
      setSubmitted(true);
    } catch (error) {
      console.error('Evacuation request failed:', error);

      alert(
        error instanceof Error
          ? error.message
          : 'Failed to submit evacuation request. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <div className="bg-white rounded-2xl border border-slate/20 shadow-soft overflow-hidden">
          <div className="bg-navy px-6 py-8 text-center text-ivory">
            <div className="w-16 h-16 mx-auto rounded-full bg-green-500/20 flex items-center justify-center mb-4">
              <CheckCircle2 className="w-9 h-9 text-green-400" />
            </div>

            <h1 className="text-2xl font-bold">
              {t('evac.successTitle')}
            </h1>

            <p className="text-sm text-slate-light mt-2">
              {t('evac.successDesc')}
            </p>
          </div>

          <div className="p-6">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-center">
              <p className="text-xs text-slate uppercase tracking-wide">
                {t('evac.trackingCodeLabel')}
              </p>

              <p className="text-2xl font-bold text-navy mt-2 tracking-wider">
                {requestId}
              </p>

              <p className="text-xs text-slate mt-2">
                {t('evac.instructionsHeading')}
              </p>
            </div>

            <div className="mt-5 bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />

              <div>
                <p className="font-semibold text-amber-800 text-sm">
                  {t('emergencyBanner.protocolActive')}
                </p>

                <p className="text-xs text-amber-700 mt-1">
                  {t('evac.inst1')} {t('evac.inst2')}
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 mt-6">
              <button
                onClick={() => setActiveTab('trace')}
                className="flex-1 px-5 py-3 rounded-xl bg-navy text-ivory font-semibold text-sm hover:opacity-90"
              >
                {t('evac.trackBtn')}
              </button>

              <button
                onClick={() => setActiveTab('landing')}
                className="flex-1 px-5 py-3 rounded-xl border border-slate/30 text-navy font-semibold text-sm hover:bg-slate-50"
              >
                {t('common.back')}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
      {/* HEADER */}
      <div className="mb-6">
        <button
          onClick={() => setActiveTab('landing')}
          className="flex items-center gap-2 text-xs text-slate hover:text-navy mb-4 font-semibold"
        >
          <ArrowLeft className="w-4 h-4" />
          {t('evac.backBtn')}
        </button>

        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shrink-0">
            <Navigation className="w-6 h-6" />
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-navy">
              {t('evac.title')}
            </h1>

            <p className="text-sm text-slate mt-1">
              {t('evac.subtitle')}
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* CONTACT */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-lg bg-navy/5 text-navy flex items-center justify-center">
              <Phone className="w-4 h-4" />
            </div>

            <div>
              <h2 className="font-bold text-navy">
                {t('evac.contactHeading')}
              </h2>

              <p className="text-xs text-slate">
                {t('evac.contactSub')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.nameLabel')}
              </label>

              <input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder={t('evac.namePlaceholder')}
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm outline-none focus:border-navy"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.phoneLabel')}
              </label>

              <input
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder={t('evac.phonePlaceholder')}
                type="tel"
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm outline-none focus:border-navy"
              />
            </div>
          </div>
        </section>

        {/* LOCATION */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-lg bg-navy/5 text-navy flex items-center justify-center">
              <MapPin className="w-4 h-4" />
            </div>

            <div>
              <h2 className="font-bold text-navy">
                {t('evac.locationHeading')}
              </h2>

              <p className="text-xs text-slate">
                {t('evac.locationSub')}
              </p>
            </div>
          </div>

          <LocationPicker
            locationName={locationName}
            latitude={locationLatitude}
            longitude={locationLongitude}
            onLocationChange={(locName, latitude, longitude) => {
              setLocationName(locName);
              setLocationLatitude(latitude);
              setLocationLongitude(longitude);
            }}
          />
        </section>

        {/* PEOPLE */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-lg bg-navy/5 text-navy flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>

            <div>
              <h2 className="font-bold text-navy">
                {t('evac.peopleHeading')}
              </h2>

              <p className="text-xs text-slate">
                {t('evac.peopleSub')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.totalPeople')}
              </label>

              <input
                type="number"
                min="1"
                value={people}
                onChange={e => setPeople(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.children')}
              </label>

              <input
                type="number"
                min="0"
                value={children}
                onChange={e => setChildren(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.elderly')}
              </label>

              <input
                type="number"
                min="0"
                value={elderly}
                onChange={e => setElderly(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                {t('evac.disabled')}
              </label>

              <input
                type="number"
                min="0"
                value={disabled}
                onChange={e => setDisabled(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm"
              />
            </div>
          </div>
        </section>

        {/* SITUATION */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-lg bg-red-50 text-red-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>

            <div>
              <h2 className="font-bold text-navy">
                {t('evac.situationHeading')}
              </h2>

              <p className="text-xs text-slate">
                {t('evac.situationSub')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {situationOptions.map(option => (
              <button
                key={option.value}
                type="button"
                onClick={() => setSituation(option.value)}
                className={`text-left px-4 py-3 rounded-xl border text-sm transition ${
                  situation === option.value
                    ? 'border-red-500 bg-red-50 text-red-700 font-semibold'
                    : 'border-slate/20 bg-white text-slate hover:border-navy'
                }`}
              >
                {t(option.key)}
              </button>
            ))}
          </div>
        </section>

        {/* ASSISTANCE */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-lg bg-navy/5 text-navy flex items-center justify-center">
              <ClipboardList className="w-4 h-4" />
            </div>

            <div>
              <h2 className="font-bold text-navy">
                {t('evac.assistanceHeading')}
              </h2>

              <p className="text-xs text-slate">
                {t('evac.assistanceSub')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {mobilityOptions.map(option => (
              <button
                key={option.value}
                type="button"
                onClick={() => setMobility(option.value)}
                className={`px-4 py-3 rounded-xl border text-sm transition ${
                  mobility === option.value
                    ? 'border-navy bg-navy/5 text-navy font-semibold'
                    : 'border-slate/20 bg-white text-slate hover:border-navy'
                }`}
              >
                {t(option.key)}
              </button>
            ))}
          </div>

          <label className="flex items-center gap-3 mt-5 p-4 rounded-xl border border-red-200 bg-red-50 cursor-pointer">
            <input
              type="checkbox"
              checked={medicalEmergency}
              onChange={e => setMedicalEmergency(e.target.checked)}
              className="w-4 h-4"
            />

            <div>
              <p className="text-sm font-semibold text-red-700">
                {t('evac.medicalEmergencyTitle')}
              </p>

              <p className="text-xs text-red-600 mt-0.5">
                {t('evac.medicalEmergencySub')}
              </p>
            </div>
          </label>
        </section>

        {/* ADDITIONAL INFO */}
        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">
          <label className="block text-sm font-bold text-navy mb-2">
            {t('evac.additionalHeading')}
          </label>

          <textarea
            value={additionalInfo}
            onChange={e => setAdditionalInfo(e.target.value)}
            rows={4}
            placeholder={t('evac.additionalPlaceholder')}
            className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm resize-none outline-none focus:border-navy"
          />
        </section>

        {/* SUBMIT */}
        <div className="bg-navy rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <p className="text-xs text-slate-light">
            {t('evac.submitNotice')}
          </p>

          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-xl bg-terracotta text-white font-bold text-sm hover:bg-terracotta/90 disabled:opacity-50 transition-colors"
          >
            {submitting
              ? t('evac.submitting')
              : t('evac.submitBtn')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EvacuationRequestPage;