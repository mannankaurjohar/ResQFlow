import React from 'react';
import { Waves } from 'lucide-react';
import { useTranslation } from '../i18n/LanguageContext';

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-navy text-ivory border-t border-navy-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2.5 mb-3">
              <div className="w-8 h-8 rounded bg-terracotta flex items-center justify-center">
                <Waves className="w-5 h-5 text-ivory" />
              </div>
              <span className="font-extrabold text-lg tracking-tight">ResQFlow</span>
            </div>
            <p className="text-slate-light text-sm max-w-md leading-relaxed mb-4">
              {t('footer.taglineQuote')}
            </p>
            <p className="text-xs text-slate max-w-md">
              {t('footer.desc')}
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-light mb-3">
              {t('footer.platformPrinciples')}
            </h4>
            <ul className="space-y-2 text-xs text-slate-light">
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">1.</span>
                <span>{t('footer.p1')}</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">2.</span>
                <span>{t('footer.p2')}</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">3.</span>
                <span>{t('footer.p3')}</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span className="text-terracotta font-bold">4.</span>
                <span>{t('footer.p4')}</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-light mb-3">
              {t('footer.emergencyCoordination')}
            </h4>
            <p className="text-xs text-slate-light leading-relaxed mb-2">
              {t('footer.ndrfText')}
            </p>
            <div className="text-xs text-slate border-t border-navy-800 pt-2">
              {t('footer.disasterMode')} <span className="text-amber-400 font-semibold">{t('footer.floodReliefActive')}</span>
            </div>
          </div>

        </div>

        <div className="border-t border-navy-800 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate">
          <div>{t('footer.copyright')}</div>
          <div className="mt-2 sm:mt-0 flex items-center space-x-4">
            <span>{t('footer.ledgerActive')}</span>
            <span>{t('footer.zeroDependencies')}</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
