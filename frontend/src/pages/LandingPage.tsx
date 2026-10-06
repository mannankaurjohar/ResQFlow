import React from 'react';
import { useApp } from '../context/AppContext';
import { useTranslation } from '../i18n/LanguageContext';
import {
  FileText,
  ArrowRight,
  Radio,
  Bell,
  Presentation,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const {
    setActiveTab,
    setJudgeMode,
    setJudgeModeStep
  } = useApp();

  const { t } = useTranslation();

  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 bg-gradient-to-b from-navy to-navy-900 text-ivory rounded-2xl shadow-elevated px-6 sm:px-10 lg:px-14 mx-auto max-w-7xl mt-4 border border-navy-700">
        <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#D97450_1px,transparent_1px)] [background-size:24px_24px]" />

        <div className="relative z-10 w-full max-w-6xl">
          <div className="inline-flex items-center space-x-2 bg-navy-800 border border-slate/30 px-3 py-1 rounded-full text-xs font-semibold text-slate-light mb-6">
            <span className="w-2 h-2 rounded-full bg-terracotta animate-pulse" />
            <span>{t('landing.activeSystemBadge')}</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-ivory font-sans leading-tight">
            {t('landing.title')}
          </h1>

          <p className="text-xl sm:text-2xl font-medium text-terracotta mt-2">
            {t('landing.subtitle')}
          </p>

          <p className="text-base sm:text-lg text-slate-light mt-4 leading-relaxed font-normal max-w-5xl">
            {t('landing.description')}
          </p>

          {/* Public Emergency Actions */}
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <button
              onClick={() => {
                setJudgeModeStep(0);
                setJudgeMode(true);
                setActiveTab('judge-mode');
              }}
              className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <Presentation className="w-4 h-4 text-terracotta" />
              <span>{t('landing.judgeModeBtn')}</span>
            </button>
            <button
              onClick={() => setActiveTab('evacuation')}
              className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <Radio className="w-4 h-4" />
              <span>{t('landing.evacBtn')}</span>
            </button>

            <button
              onClick={() => setActiveTab('report')}
              className="bg-terracotta hover:bg-terracotta-hover text-white font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <FileText className="w-4 h-4" />
              <span>{t('landing.suppliesBtn')}</span>
            </button>
            <button
              onClick={() => setActiveTab('signup')}
              className="bg-ivory hover:bg-ivory-100 text-navy font-bold px-6 py-3.5 rounded-lg shadow-card text-sm flex items-center space-x-2 transition-all"
            >
              <Bell className="w-4 h-4 text-terracotta" />
              <span>{t('landing.notifyBtn')}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Five Core Questions */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-navy tracking-tight">
            {t('landing.questionsHeading')}
          </h2>
          <p className="text-slate text-sm mt-2">
            {t('landing.questionsSubtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">1</div>
            <h3 className="font-bold text-sm text-navy mb-1">{t('landing.q1Title')}</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              {t('landing.q1Desc')}
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">2</div>
            <h3 className="font-bold text-sm text-navy mb-1">{t('landing.q2Title')}</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              {t('landing.q2Desc')}
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-terracotta text-white flex items-center justify-center font-bold text-xs mb-3">3</div>
            <h3 className="font-bold text-sm text-navy mb-1">{t('landing.q3Title')}</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              {t('landing.q3Desc')}
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-navy text-ivory flex items-center justify-center font-bold text-xs mb-3">4</div>
            <h3 className="font-bold text-sm text-navy mb-1">{t('landing.q4Title')}</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              {t('landing.q4Desc')}
            </p>
          </div>

          <div className="bg-ivory border border-slate/20 rounded-xl p-5 shadow-soft">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs mb-3">5</div>
            <h3 className="font-bold text-sm text-navy mb-1">{t('landing.q5Title')}</h3>
            <p className="text-xs text-slate-dark leading-relaxed">
              {t('landing.q5Desc')}
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="bg-ivory-100 border border-slate/20 rounded-2xl p-8 shadow-card">
          <div className="text-center max-w-xl mx-auto mb-8">
            <h3 className="text-xl font-bold text-navy">
              {t('landing.pipelineHeading')}
            </h3>
            <p className="text-xs text-slate mt-1">
              {t('landing.pipelineSubtitle')}
            </p>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center">
            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 1</div>
              <div className="font-semibold text-navy text-sm">{t('landing.step1Title')}</div>
              <div className="text-[11px] text-slate mt-0.5">{t('landing.step1Desc')}</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 2</div>
              <div className="font-semibold text-navy text-sm">{t('landing.step2Title')}</div>
              <div className="text-[11px] text-slate mt-0.5">{t('landing.step2Desc')}</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 3</div>
              <div className="font-semibold text-navy text-sm">{t('landing.step3Title')}</div>
              <div className="text-[11px] text-slate mt-0.5">{t('landing.step3Desc')}</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 4</div>
              <div className="font-semibold text-navy text-sm">{t('landing.step4Title')}</div>
              <div className="text-[11px] text-slate mt-0.5">{t('landing.step4Desc')}</div>
            </div>

            <ArrowRight className="w-4 h-4 text-slate hidden md:block shrink-0" />

            <div className="flex-1 p-3 bg-white rounded-lg border border-slate/15 shadow-sm">
              <div className="text-xs font-bold text-terracotta mb-1">STEP 5</div>
              <div className="font-semibold text-navy text-sm">{t('landing.step5Title')}</div>
              <div className="text-[11px] text-slate mt-0.5">{t('landing.step5Desc')}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};