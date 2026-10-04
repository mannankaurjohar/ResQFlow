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
  Send,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { LocationPicker } from '../components/LocationPicker';
import api from '../services/api';
const EvacuationRequestPage: React.FC = () => {
  const { setActiveTab } = useApp();

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

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!name.trim() || !phone.trim()) {
    alert('Please enter your name and phone number.');
    return;
  }

  if (
    locationLatitude === null ||
    locationLongitude === null ||
    !locationName.trim()
  ) {
    alert('Please select your current location from the map.');
    return;
  }

  if (!situation) {
    alert('Please select the current situation.');
    return;
  }

  if (!mobility) {
    alert('Please select the mobility assistance required.');
    return;
  }

  try {
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
              Evacuation Request Submitted
            </h1>

            <p className="text-sm text-slate-light mt-2">
              Your emergency request has been registered.
            </p>
          </div>

          <div className="p-6">

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-center">
              <p className="text-xs text-slate uppercase tracking-wide">
                Request ID
              </p>

              <p className="text-2xl font-bold text-navy mt-2 tracking-wider">
                {requestId}
              </p>

              <p className="text-xs text-slate mt-2">
                Keep this ID to track your evacuation request.
              </p>
            </div>

            <div className="mt-5 bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />

              <div>
                <p className="font-semibold text-amber-800 text-sm">
                  Emergency response
                </p>

                <p className="text-xs text-amber-700 mt-1">
                  Stay in a safe location if possible and follow
                  instructions from authorized emergency personnel.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 mt-6">

              <button
                onClick={() => setActiveTab('trace')}
                className="flex-1 px-5 py-3 rounded-xl bg-navy text-ivory font-semibold text-sm hover:opacity-90"
              >
                Track Request
              </button>

              <button
                onClick={() => setActiveTab('landing')}
                className="flex-1 px-5 py-3 rounded-xl border border-slate/30 text-navy font-semibold text-sm hover:bg-slate-50"
              >
                Return Home
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
          className="flex items-center gap-2 text-xs text-slate hover:text-navy mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </button>

        <div className="flex items-start gap-4">

          <div className="w-12 h-12 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shrink-0">
            <Navigation className="w-6 h-6" />
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-navy">
              Request Evacuation
            </h1>

            <p className="text-sm text-slate mt-1">
              Request emergency evacuation assistance from your current
              location.
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
                Contact Information
              </h2>

              <p className="text-xs text-slate">
                So responders can contact you if required
              </p>
            </div>

          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                Name
              </label>

              <input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Your name"
                className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm outline-none focus:border-navy"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                Phone Number
              </label>

              <input
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="10-digit mobile number"
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
                Current Location
              </h2>

              <p className="text-xs text-slate">
                Select where evacuation is required
              </p>
            </div>

          </div>

         <LocationPicker
  locationName={locationName}
  latitude={locationLatitude}
  longitude={locationLongitude}
  onLocationChange={(name, latitude, longitude) => {
    setLocationName(name);
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
                People Requiring Evacuation
              </h2>

              <p className="text-xs text-slate">
                Help responders understand the group size
              </p>
            </div>

          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

            <div>
              <label className="block text-xs font-semibold text-navy mb-2">
                Total People
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
                Children
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
                Elderly
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
                Persons with Disabilities
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
                Current Situation
              </h2>

              <p className="text-xs text-slate">
                Select the condition that best describes your situation
              </p>
            </div>

          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">

            {[
              'Trapped by floodwater',
              'Water level is rapidly rising',
              'Area is becoming isolated',
              'Building is unsafe',
              'Roads / routes are blocked',
              'Immediate evacuation required',
            ].map(option => (

              <button
                key={option}
                type="button"
                onClick={() => setSituation(option)}
                className={`text-left px-4 py-3 rounded-xl border text-sm transition ${
                  situation === option
                    ? 'border-red-500 bg-red-50 text-red-700 font-semibold'
                    : 'border-slate/20 bg-white text-slate hover:border-navy'
                }`}
              >
                {option}
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
                Evacuation Assistance
              </h2>

              <p className="text-xs text-slate">
                Tell responders what assistance is needed
              </p>
            </div>

          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

            {[
              'Can move independently',
              'Need physical assistance',
              'Cannot move without assistance',
            ].map(option => (

              <button
                key={option}
                type="button"
                onClick={() => setMobility(option)}
                className={`px-4 py-3 rounded-xl border text-sm transition ${
                  mobility === option
                    ? 'border-navy bg-navy/5 text-navy font-semibold'
                    : 'border-slate/20 bg-white text-slate hover:border-navy'
                }`}
              >
                {option}
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
                Medical emergency present
              </p>

              <p className="text-xs text-red-600 mt-0.5">
                Select this if someone requires urgent medical attention.
              </p>
            </div>

          </label>

        </section>

        {/* ADDITIONAL INFO */}

        <section className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-6">

          <label className="block text-sm font-bold text-navy mb-2">
            Additional Information
          </label>

          <textarea
            value={additionalInfo}
            onChange={e => setAdditionalInfo(e.target.value)}
            rows={4}
            placeholder="Describe anything else responders should know..."
            className="w-full px-4 py-3 rounded-xl border border-slate/20 bg-white text-sm resize-none outline-none focus:border-navy"
          />

        </section>

        {/* SUBMIT */}

        <div className="bg-navy rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

          <div className="text-ivory">

            <p className="font-bold text-sm">
              Need immediate evacuation assistance?
            </p>

            <p className="text-xs text-slate-light mt-1">
              Submit your location and situation so the response team can
              assess the request.
            </p>

          </div>

          <button
            type="submit"
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-terracotta text-white font-bold text-sm hover:opacity-90 shrink-0"
          >
            <Send className="w-4 h-4" />
            Submit Evacuation Request
          </button>

        </div>

      </form>
    </div>
  );
};

export default EvacuationRequestPage;