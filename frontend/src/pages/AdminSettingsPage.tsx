import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  Bell,
  Database,
  Radio,
  Save,
  RefreshCw,
  LockKeyhole
} from 'lucide-react';

const AdminSettingsPage: React.FC = () => {
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [floodDataRefresh, setFloodDataRefresh] = useState('15');
  const [sessionTimeout, setSessionTimeout] = useState('30');

  const handleSave = () => {
    // Settings persistence can be connected to the backend later.
    alert('System settings saved.');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 pb-12">

      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-navy rounded-lg">
              <Settings className="w-6 h-6 text-white" />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-navy">
                System Settings
              </h1>

              <p className="text-sm text-slate-500 mt-1">
                Configure platform-wide administration and system behavior
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="
            flex items-center gap-2
            bg-navy
            hover:bg-navy-800
            text-white
            px-4 py-2
            rounded-lg
            text-sm
            font-semibold
          "
        >
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>

      {/* SECURITY SETTINGS */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <ShieldCheck className="w-5 h-5 text-terracotta" />

          <h2 className="text-lg font-semibold text-navy">
            Security
          </h2>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm">

          <div className="p-5 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <LockKeyhole className="w-5 h-5 text-slate-500" />

              <div>
                <h3 className="font-semibold text-navy">
                  Session Timeout
                </h3>

                <p className="text-sm text-slate-500">
                  Automatically expire inactive administrator sessions.
                </p>
              </div>
            </div>

            <select
              value={sessionTimeout}
              onChange={(e) =>
                setSessionTimeout(e.target.value)
              }
              className="
                mt-4
                w-full sm:w-64
                border border-slate-300
                rounded-lg
                px-3 py-2
                text-sm
                text-navy
              "
            >
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="60">60 minutes</option>
              <option value="120">120 minutes</option>
            </select>
          </div>

          <div className="p-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-navy">
                  Maintenance Mode
                </h3>

                <p className="text-sm text-slate-500">
                  Temporarily restrict access while system maintenance
                  is being performed.
                </p>
              </div>

              <button
                onClick={() =>
                  setMaintenanceMode(!maintenanceMode)
                }
                className={`
                  relative
                  w-12 h-6
                  rounded-full
                  transition-colors
                  ${
                    maintenanceMode
                      ? 'bg-terracotta'
                      : 'bg-slate-300'
                  }
                `}
              >
                <span
                  className={`
                    absolute
                    top-1
                    w-4 h-4
                    bg-white
                    rounded-full
                    transition-transform
                    ${
                      maintenanceMode
                        ? 'translate-x-7'
                        : 'translate-x-1'
                    }
                  `}
                />
              </button>
            </div>
          </div>

        </div>
      </section>

      {/* NOTIFICATION SETTINGS */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Bell className="w-5 h-5 text-terracotta" />

          <h2 className="text-lg font-semibold text-navy">
            Notifications
          </h2>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">

          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="font-semibold text-navy">
                System Notifications
              </h3>

              <p className="text-sm text-slate-500">
                Enable system-level notifications for administrators.
              </p>
            </div>

            <button
              onClick={() =>
                setNotificationsEnabled(
                  !notificationsEnabled
                )
              }
              className={`
                relative
                w-12 h-6
                rounded-full
                transition-colors
                ${
                  notificationsEnabled
                    ? 'bg-terracotta'
                    : 'bg-slate-300'
                }
              `}
            >
              <span
                className={`
                  absolute
                  top-1
                  w-4 h-4
                  bg-white
                  rounded-full
                  transition-transform
                  ${
                    notificationsEnabled
                      ? 'translate-x-7'
                      : 'translate-x-1'
                  }
                `}
              />
            </button>
          </div>

        </div>
      </section>

      {/* DATA SERVICES */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <Radio className="w-5 h-5 text-terracotta" />

          <h2 className="text-lg font-semibold text-navy">
            Data Services
          </h2>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm">

          <div className="p-5 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <RefreshCw className="w-5 h-5 text-slate-500" />

              <div>
                <h3 className="font-semibold text-navy">
                  Flood Data Refresh
                </h3>

                <p className="text-sm text-slate-500">
                  Configure how frequently the system refreshes
                  flood monitoring data.
                </p>
              </div>
            </div>

            <select
              value={floodDataRefresh}
              onChange={(e) =>
                setFloodDataRefresh(e.target.value)
              }
              className="
                mt-4
                w-full sm:w-64
                border border-slate-300
                rounded-lg
                px-3 py-2
                text-sm
                text-navy
              "
            >
              <option value="5">Every 5 minutes</option>
              <option value="15">Every 15 minutes</option>
              <option value="30">Every 30 minutes</option>
              <option value="60">Every 60 minutes</option>
            </select>
          </div>

          <div className="p-5">
            <div className="flex items-start gap-3">
              <Database className="w-5 h-5 text-slate-500 mt-0.5" />

              <div>
                <h3 className="font-semibold text-navy">
                  Database
                </h3>

                <p className="text-sm text-slate-500">
                  Application data is stored in the configured
                  ResQFlow database.
                </p>

                <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 text-green-700 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  Database Connected
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* SYSTEM INFORMATION */}
      <section>
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-navy">
            System Information
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">

            <div>
              <p className="text-xs text-slate-500">
                Platform
              </p>
              <p className="font-semibold text-navy mt-1">
                ResQFlow
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">
                Environment
              </p>
              <p className="font-semibold text-navy mt-1">
                Development
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">
                Administration
              </p>
              <p className="font-semibold text-navy mt-1">
                System Administrator
              </p>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
};

export default AdminSettingsPage;