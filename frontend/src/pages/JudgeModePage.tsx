import React from 'react';
import { useApp } from '../context/AppContext';

const steps = [
  {
    title: 'What is ResQFlow?',
    subtitle: 'AI-Powered Flood Relief Coordination',
    description:
      'ResQFlow connects affected communities, authorities, NGOs, warehouses, volunteers, donors and response teams through one coordinated platform.',
    points: [
      'Centralized disaster-relief coordination',
      'AI-assisted resource matching',
      'Real-time response tracking',
      'Transparent relief distribution'
    ]
  },
  {
    title: 'Community Reports a Need',
    subtitle: 'Request Help or Essential Supplies',
    description:
      'A citizen can report a need such as food, medicine, shelter or other emergency supplies through the community interface.',
    points: [
      'Simple emergency reporting',
      'Location and priority information',
      'Supply and evacuation requests',
      'Request tracking'
    ],
    tab: 'report'
  },
  {
    title: 'Authority Verifies & Prioritizes',
    subtitle: 'Command Center',
    description:
      'Authorities review incoming requests, verify them and prioritize urgent cases so resources can be directed where they are needed most.',
    points: [
      'Central request dashboard',
      'Priority-based handling',
      'Verification workflow',
      'Emergency escalation'
    ],
    tab: 'command'
  },
  {
    title: 'AI Matches Relief Resources',
    subtitle: 'Intelligent Supply Allocation',
    description:
      'For supply requests, the AI matching workflow connects community demand with available resources and warehouse inventory.',
    points: [
      'Demand analysis',
      'Available-stock matching',
      'Warehouse coordination',
      'Allocation approval'
    ],
    tab: 'warehouse'
  },
  {
    title: 'Create Response Team',
    subtitle: 'Organize Emergency Response Units',
    description:
      'For evacuation and emergency operations, authorities can create response units such as NDRF, SDRF, Fire & Rescue and authorized local teams.',
    points: [
      'Create response teams',
      'Select response organization',
      'Assign an operator',
      'Track team availability'
    ],
    tab: 'response-units'
  },
  {
  title: 'Response Unit Management',
  subtitle: 'Monitor Emergency Teams',
  description:
    'Authorities can manage registered response units, assign operators and monitor team availability for emergency deployment.',
  points: [
    'View available response units',
    'Manage NDRF, SDRF and other teams',
    'Assign response unit operators',
    'Monitor team readiness'
  ],
  tab: 'response-units'
},
  {
    title: 'Response Operator Tasks',
    subtitle: 'Field-Level Execution',
    description:
      'Response operators receive their assigned tasks and can manage the operational status of emergency activities from the response task interface.',
    points: [
      'View assigned tasks',
      'Accept or manage operations',
      'Update task progress',
      'Complete field activities'
    ],
    tab: 'response-tasks'
  },
  {
    title: 'Evacuation & Emergency Response',
    subtitle: 'Protect People During Critical Situations',
    description:
      'Evacuation requests follow a dedicated response workflow instead of the normal supply-matching process.',
    points: [
      'Dedicated evacuation approval',
      'Response-unit coordination',
      'Emergency deployment',
      'Status tracking'
    ],
    tab: 'evacuation'
  },
  {
    title: 'Relief Distribution',
    subtitle: 'Track Movement of Relief',
    description:
      'Once resources are allocated, the relief movement can be tracked from source to destination to improve accountability.',
    points: [
      'Relief movement tracking',
      'Distribution status',
      'Request-to-delivery visibility',
      'Traceable operations'
    ],
    tab: 'trace'
  },
  {
    title: 'Volunteer & NGO Coordination',
    subtitle: 'Coordinate the Relief Network',
    description:
      'NGOs, volunteers and warehouse teams contribute to the response by managing resources, inventory and field support.',
    points: [
      'Warehouse coordination',
      'Volunteer support',
      'NGO operations',
      'Inventory visibility'
    ],
    tab: 'warehouse'
  },
  {
    title: 'Analytics & Transparency',
    subtitle: 'Measure the Response',
    description:
      'Authorities can monitor operational performance and relief activity through analytics and audit information.',
    points: [
      'Response statistics',
      'Relief activity insights',
      'Operational monitoring',
      'Transparent records'
    ],
    tab: 'analytics'
  },
  {
    title: 'Complete Disaster-Relief Workflow',
    subtitle: 'From Request to Resolution',
    description:
      'ResQFlow brings the complete process together: report → verify → match → allocate → create response team → assign → execute → distribute → track → analyze.',
    points: [
      'One connected workflow',
      'AI-assisted decisions',
      'Coordinated emergency response',
      'Transparent end-to-end operations'
    ]
  }
];

const JudgeModePage: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    judgeMode,
    setJudgeMode,
    judgeModeStep,
    setJudgeModeStep
  } = useApp();

  if (!judgeMode) {
    return null;
  }

  const current = steps[judgeModeStep];
 const isViewingModule =
  activeTab !== 'judge-mode' &&
  activeTab !== 'landing';

  const nextStep = () => {
  if (judgeModeStep < steps.length - 1) {
    setJudgeModeStep(judgeModeStep + 1);
    setActiveTab('judge-mode');
  } else {
    exitDemo();
  }
};
  const previousStep = () => {
  if (judgeModeStep > 0) {
    setJudgeModeStep(judgeModeStep - 1);
    setActiveTab('judge-mode');
  }
};

  const openModule = () => {
    if (current.tab) {
      setActiveTab(current.tab);
    }
  };

  const exitDemo = () => {
    setJudgeMode(false);
    setJudgeModeStep(0);
    setActiveTab('landing');
  };

  /*
   * Full Judge Mode screen
   */
  if (!isViewingModule) {
    return (
      <div className="max-w-6xl mx-auto px-4 md:px-8 py-6">
        <div className="bg-white rounded-2xl border border-navy/10 shadow-elevated overflow-hidden">

          <div className="p-6 md:p-10">

            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
                  Hackathon Judge Mode
                </div>

                <h1 className="text-3xl md:text-4xl font-bold text-navy mt-1">
                  ResQFlow
                </h1>

                <p className="text-slate mt-1">
                  Guided product demonstration • No login required
                </p>
              </div>

              <button
                onClick={exitDemo}
                className="px-4 py-2 rounded-lg border border-navy/15 text-navy text-sm font-semibold hover:bg-ivory"
              >
                Exit Demo
              </button>
            </div>

            <div className="mb-7">
              <div className="flex justify-between text-xs font-semibold text-slate mb-2">
                <span>Demo Progress</span>
                <span>
                  {judgeModeStep + 1} / {steps.length}
                </span>
              </div>

              <div className="h-2 bg-navy/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-terracotta transition-all duration-300"
                  style={{
                    width: `${((judgeModeStep + 1) / steps.length) * 100}%`
                  }}
                />
              </div>
            </div>

            <div className="inline-flex items-center px-3 py-1 rounded-full bg-terracotta/10 text-terracotta text-xs font-bold mb-4">
              STEP {judgeModeStep + 1}
            </div>

            <h2 className="text-3xl md:text-4xl font-bold text-navy">
              {current.title}
            </h2>

            <p className="text-lg font-semibold text-terracotta mt-2">
              {current.subtitle}
            </p>

            <p className="text-slate leading-7 mt-5 text-base md:text-lg max-w-4xl">
              {current.description}
            </p>

            <div className="grid md:grid-cols-2 gap-3 mt-7">
              {current.points.map((point, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-4 rounded-xl bg-ivory border border-navy/10"
                >
                  <div className="w-6 h-6 shrink-0 rounded-full bg-terracotta text-white flex items-center justify-center text-xs font-bold">
                    ✓
                  </div>

                  <span className="text-sm font-medium text-navy">
                    {point}
                  </span>
                </div>
              ))}
            </div>

            {current.tab && (
              <button
                onClick={openModule}
                className="mt-8 bg-navy hover:bg-navy/90 text-white px-5 py-3 rounded-xl text-sm font-bold"
              >
                Open Live Module →
              </button>
            )}
          </div>

          <div className="border-t border-navy/10 bg-ivory/60 px-6 md:px-10 py-4 flex justify-between">

            <button
              disabled={judgeModeStep === 0}
              onClick={previousStep}
              className="px-4 py-2.5 rounded-lg border border-navy/15 text-navy text-sm font-semibold disabled:opacity-30"
            >
              ← Previous
            </button>

            <button
              onClick={nextStep}
              className="px-5 py-2.5 rounded-lg bg-terracotta hover:bg-terracotta-hover text-white text-sm font-bold"
            >
              {judgeModeStep === steps.length - 1
                ? 'Finish Demo'
                : 'Next →'}
            </button>

          </div>
        </div>
      </div>
    );
  }

  /*
   * Persistent Judge Mode controller while viewing
   * a real ResQFlow module.
   */

return (
<div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-[9999] w-[min(900px,calc(100%-32px))]">
    <div className="bg-navy text-ivory rounded-2xl shadow-elevated border border-white/10 px-4 py-3">

        <div className="flex flex-col md:flex-row md:items-center gap-3">

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-terracotta animate-pulse" />

              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-light">
                Judge Mode
              </span>

              <span className="text-[10px] text-slate-light">
                Step {judgeModeStep + 1}/{steps.length}
              </span>
            </div>

            <div className="text-sm font-bold mt-1 truncate">
              {current.title}
            </div>

            <div className="text-[11px] text-slate-light truncate">
              {current.subtitle}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">

            <button
              disabled={judgeModeStep === 0}
              onClick={previousStep}
              className="px-3 py-2 rounded-lg border border-white/20 text-xs font-semibold disabled:opacity-30"
            >
              ← Back
            </button>

            <button
              onClick={nextStep}
              className="px-4 py-2 rounded-lg bg-terracotta hover:bg-terracotta-hover text-white text-xs font-bold"
            >
              {judgeModeStep === steps.length - 1
                ? 'Finish'
                : 'Next →'}
            </button>

            <button
              onClick={exitDemo}
              className="px-3 py-2 rounded-lg border border-white/20 text-xs font-semibold"
            >
              Exit
            </button>

          </div>
        </div>
      </div>
    </div>
  );
};

export default JudgeModePage;