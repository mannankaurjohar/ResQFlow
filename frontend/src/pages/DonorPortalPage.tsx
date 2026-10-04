
import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
import {
  HeartHandshake,
   CheckCircle2,
  Gift
} from 'lucide-react';

export const DonorPortalPage: React.FC = () => {
  const { showNotification } = useApp();

 const [donorName, setDonorName] = useState('');
const [donorEmail, setDonorEmail] = useState('');
const [category, setCategory] = useState('Drinking Water');
const [quantity, setQuantity] = useState(10);
const [unit, setUnit] = useState('Bottles');
const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [createdReliefId, setCreatedReliefId] = useState<string | null>(null);
const [donationCompleted, setDonationCompleted] = useState(false);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const res = await api.createDonation({
        donor_name: donorName,
        donor_email: donorEmail,
        notes: notes,
        items: [
          {
            category: category,
            item_name: `${category} Supply Pack`,
            quantity: Number(quantity),
            unit: unit
          }
        ]
      });

      console.log('DONATION RESPONSE:', res);

setCreatedReliefId(res.relief_id);
setDonationCompleted(true);

showNotification(
  'Donation completed successfully',
  'success'
);
    } catch (err) {
      showNotification(
        'Failed to register donation',
        'error'
      );
    } finally {
      setSubmitting(false);
    }
  };
if (donationCompleted) {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
      <div className="bg-ivory border border-slate/20 rounded-2xl shadow-soft p-8 sm:p-12 text-center">

        <div className="flex justify-center mb-5">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center">
            <CheckCircle2 className="w-9 h-9 text-emerald-600" />
          </div>
        </div>

        <h1 className="text-3xl font-extrabold text-navy">
          Donation Completed
        </h1>

        <p className="text-sm text-slate mt-3 max-w-md mx-auto">
          Thank you for contributing to flood relief efforts.
          Your donation has been successfully registered.
        </p>

        <div className="mt-7 bg-slate-50 border border-slate/20 rounded-xl p-5">
          <p className="text-xs text-slate">
            Donation ID
          </p>

          <p className="font-mono font-bold text-navy text-lg mt-1">
            {createdReliefId}
          </p>
        </div>

        <p className="text-xs text-slate mt-5">
          Your contribution has been recorded in the ResQFlow relief system.
        </p>

        <button
          type="button"
          onClick={() => {
            setDonationCompleted(false);
            setCreatedReliefId(null);
            setDonorName('');
            setDonorEmail('');
            setQuantity(10);
            setNotes('');
          }}
          className="mt-7 bg-navy hover:bg-navy-800 text-white font-semibold px-5 py-2.5 rounded-lg text-sm"
        >
          Make Another Donation
        </button>

      </div>
    </div>
  );
}
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
          <HeartHandshake className="w-7 h-7 text-terracotta" />
          <span>Donor Contribution Portal</span>
        </h1>

        <p className="text-xs sm:text-sm text-slate mt-1">
          Register relief contributions and help provide essential supplies
          to communities affected by floods.
        </p>
      </div>

      
      {/* Donation Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft space-y-5"
      >
        <h3 className="font-bold text-base text-navy pb-2 border-b border-slate/15 flex items-center gap-2">
          <Gift className="w-4 h-4 text-terracotta" />
          <span>Pledge Relief Supplies</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">

          <div>
            <label className="block font-semibold text-slate-dark mb-1">
              Donor Full Name / Organization
            </label>

            <input
              type="text"
              value={donorName}
              onChange={e => setDonorName(e.target.value)}
              required
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">
              Donor Email Address
            </label>

            <input
              type="email"
              value={donorEmail}
              onChange={e => setDonorEmail(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">
              Relief Commodity Category
            </label>

            <select
              value={category}
              onChange={e => {
                setCategory(e.target.value);

                if (e.target.value === 'Drinking Water') {
                  setUnit('Bottles');
                } else if (e.target.value === 'Food') {
                  setUnit('Packets');
                } else {
                  setUnit('Kits');
                }
              }}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-semibold"
            >
              <option value="Drinking Water">
                Drinking Water (Bottled / Cans)
              </option>

              <option value="Food">
                Ready-to-Eat Food Packets
              </option>

              <option value="Medicines">
                Emergency Medicine & First Aid
              </option>

              <option value="Sanitation">
                Sanitation & Hygiene Kits
              </option>

              <option value="Temporary Shelter">
                Tarpaulins & Thermal Blankets
              </option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">
              Quantity ({unit})
            </label>

            <input
              type="number"
              min="10"
              value={quantity}
              onChange={e => setQuantity(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-bold"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-semibold text-slate-dark mb-1">
              Notes / Target Flood Zone Preference
            </label>

            <input
              type="text"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

        </div>

        {/* Donation Confirmation */}
       {createdReliefId && (
  <div className="p-5 bg-emerald-50 border border-emerald-300 rounded-lg">
    <div className="flex items-center gap-3">
      <CheckCircle2 className="w-7 h-7 text-emerald-600" />

      <div>
        <div className="font-bold text-emerald-900 text-base">
          Donation Completed
        </div>

        <div className="text-xs text-emerald-800 mt-0.5">
          Your relief contribution has been successfully registered.
        </div>
      </div>
    </div>

    <div className="mt-4 pt-3 border-t border-emerald-200">
      <div className="text-[11px] text-slate">
        Donation ID
      </div>

      <div className="font-mono font-bold text-navy text-sm mt-0.5">
        {createdReliefId}
      </div>
    </div>
  </div>
)}

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-2.5 rounded-lg text-xs sm:text-sm transition-colors"
          >
            {submitting
              ? 'Registering Contribution...'
              : 'Confirm Relief Contribution'}
          </button>
        </div>

      </form>
    </div>
  );
};

