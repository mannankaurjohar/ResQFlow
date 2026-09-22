import React, { useEffect, useState } from 'react';
import { InventoryItem } from '../types';
import api from '../services/api';
import { Warehouse, AlertTriangle, Clock, CheckCircle2, ShieldAlert, Package, RefreshCw } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export const NgoWarehousePage: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getInventory(),
      api.getInventoryAlerts()
    ]).then(([invData, alertData]) => {
      setInventory(invData);
      setAlerts(alertData);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate/20 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight flex items-center gap-2">
            <Warehouse className="w-7 h-7 text-terracotta" />
            <span>Warehouses & NGO Inventory Hub</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate mt-1">
            Real-time batch visibility, FEFO expiration tracking, and multi-depot stock coordination
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 border border-slate/30 rounded-lg text-slate hover:text-navy bg-ivory"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Alerts Row: Low Stock & Expiring Batches */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-bold text-navy uppercase tracking-wider flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-status-critical" />
            <span>Critical Inventory Alerts & Batch Expirations</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.map((al, idx) => (
              <div key={idx} className="bg-amber-50/70 border border-amber-200 rounded-lg p-3 text-xs flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-navy">{al.warehouse} &bull; {al.item}</div>
                  <div className="text-slate-dark text-[11px] mt-0.5">{al.message}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inventory Grid Table */}
      <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
        <h3 className="font-bold text-base text-navy mb-3">Depot Stock Levels & Allocations</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-ivory-100 text-slate uppercase text-[10px] font-bold border-b border-slate/20">
              <tr>
                <th className="py-2.5 px-3">Depot</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Item Name</th>
                <th className="py-2.5 px-3">Total In Stock</th>
                <th className="py-2.5 px-3">Allocated</th>
                <th className="py-2.5 px-3">Available</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/15">
              {inventory.map(item => (
                <tr key={item.id} className="hover:bg-ivory-50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-navy">{item.warehouse_name}</td>
                  <td className="py-3 px-3 text-slate">{item.category}</td>
                  <td className="py-3 px-3 font-bold text-navy">{item.item_name}</td>
                  <td className="py-3 px-3 font-mono">{item.total_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3 font-mono text-terracotta">{item.allocated_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3 font-mono font-bold text-status-fulfilled">{item.available_quantity.toLocaleString()} {item.unit}</td>
                  <td className="py-3 px-3">
                    <StatusBadge status={item.status} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
