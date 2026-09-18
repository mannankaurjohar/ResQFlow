import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import api from '../services/api';
import { HeartHandshake, CheckCircle2, Search, ArrowRight, ShieldCheck, Gift } from 'lucide-react';

export const DonorPortalPage: React.FC = () => {
  const { showNotification, setActiveTab, setTraceIdInput } = useApp();

  const [donorName, setDonorName] = useState('Anita & Vikram Sharma');
  const [donorEmail, setDonorEmail] = useState('anita.sharma@gmail.com');
  const [category, setCategory] = useState('Drinking Water');
  const [quantity, setQuantity] = useState(500);
  const [unit, setUnit] = useState('Bottles');
  const [notes, setNotes] = useState('Emergency flood relief for stranded families in Zone B delta.');
  const [submitting, setSubmitting] = useState(false);
  const [createdReliefId, setCreatedReliefId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.createDonation({
        donor_name: donorName,
        donor_email: donorEmail,
        notes: notes,
        items: [{
          category: category,
          item_name: `${category} Supply Pack`,
          quantity: Number(quantity),
          unit: unit
        }]
      });
      setCreatedReliefId(res.relief_id);
      showNotification(`Donation registered! Track transparent delivery with ID: ${res.relief_id}`, 'success');
    } catch (err) {
      showNotification('Failed to pledge donation', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
          <HeartHandshake className="w-7 h-7 text-terracotta" />
          <span>Donor Transparency Portal</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate mt-1">
          Every contribution receives a unique tracking ID and verified delivery proof from warehouse to village.
        </p>
      </div>

      {/* Signature Impact Highlight Card (Directly from Hackathon Prompt) */}
      <div className="bg-gradient-to-r from-navy to-navy-900 text-ivory rounded-xl p-6 shadow-elevated border border-navy-700">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] bg-terracotta text-white font-bold px-2 py-0.5 rounded uppercase tracking-wider">
              Verified Delivery Example
            </span>
            <div className="text-xl font-bold font-mono mt-1 text-ivory">DONATION D-10284</div>
            <div className="text-sm text-slate-light mt-0.5">
              Donor: <b>Anita & Vikram Sharma</b> &bull; 500 Clean Water Bottles
            </div>
            <div className="text-xs text-slate-light mt-1">
              Destination: <b>Flood Zone B (Village A Shelter)</b> &bull; Impact: <b>~250 people supported</b>
            </div>
          </div>
          <button
            onClick={() => { setTraceIdInput('RELIEF-2026-00482'); setActiveTab('trace'); }}
            className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 transition-colors self-start sm:self-center"
          >
            <span>View Verified Timeline</span>
            <ArrowRight className="w-3.5 h-3.5 text-terracotta" />
          </button>
        </div>
      </div>

      {/* Donation Form */}
      <form onSubmit={handleSubmit} className="bg-ivory border border-slate/20 rounded-xl p-6 shadow-soft space-y-5">
        <h3 className="font-bold text-base text-navy pb-2 border-b border-slate/15 flex items-center gap-2">
          <Gift className="w-4 h-4 text-terracotta" />
          <span>Pledge Relief Supplies</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-dark mb-1">Donor Full Name / Organization</label>
            <input
              type="text"
              value={donorName}
              onChange={e => setDonorName(e.target.value)}
              required
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Donor Email Address</label>
            <input
              type="email"
              value={donorEmail}
              onChange={e => setDonorEmail(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Relief Commodity Category</label>
            <select
              value={category}
              onChange={e => {
                setCategory(e.target.value);
                if (e.target.value === 'Drinking Water') setUnit('Bottles');
                else if (e.target.value === 'Food') setUnit('Packets');
                else setUnit('Kits');
              }}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-semibold"
            >
              <option value="Drinking Water">Drinking Water (Bottled / Cans)</option>
              <option value="Food">Ready-to-Eat Food Packets</option>
              <option value="Medicines">Emergency Medicine & First Aid</option>
              <option value="Sanitation">Sanitation & Hygiene Kits</option>
              <option value="Temporary Shelter">Tarpaulins & Thermal Blankets</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-dark mb-1">Quantity ({unit})</label>
            <input
              type="number"
              min="10"
              value={quantity}
              onChange={e => setQuantity(Number(e.target.value))}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy font-bold"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-semibold text-slate-dark mb-1">Notes / Target Flood Zone Preference</label>
            <input
              type="text"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full bg-white border border-slate/30 rounded-lg px-3 py-2 text-navy"
            />
          </div>
        </div>

        {createdReliefId && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-lg text-xs flex items-center justify-between">
            <div>
              <span className="font-bold text-emerald-900">Contribution Pledged!</span>
              <div className="font-mono font-bold text-navy text-sm mt-0.5">{createdReliefId}</div>
            </div>
            <button
              type="button"
              onClick={() => { setTraceIdInput(createdReliefId); setActiveTab('trace'); }}
              className="bg-emerald-700 text-white font-bold px-3 py-1.5 rounded text-xs"
            >
              Trace Contribution Now
            </button>
          </div>
        )}

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-2.5 rounded-lg text-xs sm:text-sm transition-colors"
          >
            {submitting ? 'Registering Pledged Cargo...' : 'Confirm Relief Contribution'}
          </button>
        </div>
      </form>

    </div>
  );
};
