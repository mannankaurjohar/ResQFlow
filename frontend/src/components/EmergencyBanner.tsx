import React from 'react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import { AlertOctagon, ArrowRight } from 'lucide-react';

export const EmergencyBanner: React.FC = () => {
  const { isEmergencyMode, isEscalated, setActiveTab } = useApp();
  const { t } = useTranslation();

  if (!isEmergencyMode && !isEscalated) return null;

  return (
    <div className="bg-gradient-to-r from-red-950 via-status-critical to-red-900 text-white px-4 py-2.5 shadow-md border-b border-red-800">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-xs sm:text-sm">
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-5 h-5 animate-pulse text-amber-300 shrink-0" />
          <span className="font-bold tracking-wide">
            {isEscalated
              ? t('emergencyBanner.flashFlood')
              : t('emergencyBanner.protocolActive')}
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('command')}
            className="bg-white/15 hover:bg-white/25 text-white font-medium px-3 py-1 rounded text-xs transition-colors flex items-center space-x-1"
          >
            <span>{t('emergencyBanner.openCommandMap')}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
