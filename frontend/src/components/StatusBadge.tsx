import React from 'react';
import { AlertCircle, Clock, CheckCircle2, Truck, HelpCircle, ShieldAlert } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '', size = 'md' }) => {
  const s = status.toUpperCase();

  let bg = 'bg-slate-100 text-slate-dark border-slate/30';
  let icon = <HelpCircle className="w-3.5 h-3.5 mr-1 inline" />;
  let label = status;

  if (s === 'CRITICAL' || s === 'SEVERE') {
    bg = 'bg-red-50 text-status-critical border-status-critical/30';
    icon = <ShieldAlert className="w-3.5 h-3.5 mr-1 inline animate-pulse text-status-critical" />;
    label = 'Critical';
  } else if (s === 'HIGH') {
    bg = 'bg-orange-50 text-status-high border-status-high/30';
    icon = <AlertCircle className="w-3.5 h-3.5 mr-1 inline text-status-high" />;
    label = 'High Priority';
  } else if (s === 'MEDIUM' || s === 'MODERATE') {
    bg = 'bg-amber-50 text-status-medium border-status-medium/30';
    icon = <Clock className="w-3.5 h-3.5 mr-1 inline text-status-medium" />;
    label = 'Medium';
  } else if (s === 'LOW') {
    bg = 'bg-emerald-50 text-status-low border-status-low/30';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-status-low" />;
    label = 'Low Risk';
  } else if (s === 'DELIVERED' || s === 'FULFILLED') {
    bg = 'bg-emerald-50 text-status-fulfilled border-status-fulfilled/30 font-medium';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-status-fulfilled" />;
    label = 'Delivered';
  } else if (s === 'IN_TRANSIT' || s === 'DISPATCHED') {
    bg = 'bg-sky-50 text-status-transit border-status-transit/30 font-medium';
    icon = <Truck className="w-3.5 h-3.5 mr-1 inline text-status-transit" />;
    label = 'In Transit';
  } else if (s === 'ALLOCATED' || s === 'PARTIALLY_FULFILLED') {
    bg = 'bg-teal-50 text-teal-800 border-teal-300';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-teal-700" />;
    label = s === 'PARTIALLY_FULFILLED' ? 'Partially Fulfilled' : 'Allocated';
  } else if (s === 'FLAGGED_DUPLICATE') {
    bg = 'bg-amber-50 text-amber-900 border-amber-300';
    icon = <AlertCircle className="w-3.5 h-3.5 mr-1 inline text-amber-700" />;
    label = 'Duplicate Flagged';
  } else if (s === 'VERIFIED') {
    bg = 'bg-blue-50 text-blue-800 border-blue-300';
    icon = <CheckCircle2 className="w-3.5 h-3.5 mr-1 inline text-blue-700" />;
    label = 'Verified';
  } else if (s === 'PENDING') {
    bg = 'bg-stone-100 text-slate-dark border-stone-300';
    icon = <Clock className="w-3.5 h-3.5 mr-1 inline text-slate" />;
    label = 'Pending';
  }

  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${bg} ${sizeClass} ${className}`}>
      {icon}
      {label}
    </span>
  );
};
