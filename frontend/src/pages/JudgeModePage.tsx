import React from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BellRing,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Database,
  FileSearch,
  GitBranch,
  LayoutDashboard,
  MapPin,
  PackageCheck,
  Presentation,
  Radio,
  Settings,
  ShieldCheck,
  Truck,
  UserCog,
  Users,
  Warehouse,
  X,
} from 'lucide-react';

import { useApp } from '../context/AppContext';

type JudgeStep = {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  icon: React.ElementType;
  tab?: string;
  accent: string;
  points: string[];
  flow: string[];
};

const steps: JudgeStep[] = [
  {
    id: 1,
    title: 'What is ResQFlow?',
    subtitle: 'One platform for coordinated disaster relief',
    description:
      'ResQFlow connects affected communities, authorities, response teams, NGOs and relief resources through one transparent disaster-response ecosystem.',
    icon: Presentation,
    accent: 'terracotta',
    points: [
      'Connects the complete relief ecosystem',
      'Converts community needs into actionable requests',
      'Coordinates resources and emergency teams',
      'Provides traceability and accountability',
    ],
    flow: [
      'Community',
      'Authority',
      'AI Matching',
      'Response',
      'Distribution',
      'Transparency',
    ],
  },

  {
    id: 2,
    title: 'Community Reports a Need',
    subtitle: 'Capture real needs from affected people',
    description:
      'People affected by a disaster can submit their requirements through a structured reporting workflow. Each report becomes a trackable case for authorities.',
    icon: MapPin,
    tab: 'report',
    accent: 'blue',
    points: [
      'Simple community reporting',
      'Structured request information',
      'Location-aware disaster context',
      'Requests enter the authority workflow',
    ],
    flow: [
      'Affected Person',
      'Submit Request',
      'Request Created',
      'Authority Review',
    ],
  },

  {
    id: 3,
    title: 'Authority Command Center',
    subtitle: 'Verify, prioritize and coordinate',
    description:
      'The Command Center gives authorities a unified operational view of incoming requests so they can verify needs, determine priorities and initiate the right response.',
    icon: LayoutDashboard,
    tab: 'command',
    accent: 'navy',
    points: [
      'Centralized request monitoring',
      'Verification and prioritization',
      'Supply and evacuation decisions',
      'Operational status visibility',
    ],
    flow: [
      'Incoming Requests',
      'Verify',
      'Prioritize',
      'Take Action',
    ],
  },

  {
    id: 4,
    title: 'AI Resource Matching',
    subtitle: 'Match verified needs with available resources',
    description:
      'For supply requests, ResQFlow uses AI-assisted matching to connect verified community demand with suitable relief inventory and available resources.',
    icon: GitBranch,
    tab: 'warehouse',
    accent: 'purple',
    points: [
      'Demand-to-resource matching',
      'Warehouse inventory awareness',
      'Reduced manual coordination',
      'Faster allocation decisions',
    ],
    flow: [
      'Verified Need',
      'AI Matching',
      'Available Resources',
      'Allocation',
    ],
  },

  {
    id: 5,
    title: 'Response Unit Creation & Management',
    subtitle: 'Build authorized emergency response teams',
    description:
      'Authorities can create and manage response units such as NDRF, SDRF, Fire & Rescue and Police/Emergency teams, then assign suitable operators.',
    icon: Users,
    tab: 'response-units',
    accent: 'orange',
    points: [
      'Create authorized response units',
      'Select the appropriate unit type',
      'Assign response operators',
      'Track team availability',
    ],
    flow: [
      'Response Required',
      'Create Unit',
      'Assign Operator',
      'Ready for Deployment',
    ],
  },

  {
    id: 6,
    title: 'Response Operator Tasks',
    subtitle: 'Turn assignments into field action',
    description:
      'Response operators receive operational tasks and manage their assigned activities, giving the response organization a clear connection between command decisions and field execution.',
    icon: Truck,
    tab: 'response-tasks',
    accent: 'green',
    points: [
      'Receive assigned tasks',
      'View operational details',
      'Track task progress',
      'Complete field activities',
    ],
    flow: [
      'Command Assignment',
      'Operator',
      'Field Task',
      'Completion',
    ],
  },

  {
    id: 7,
    title: 'Live Alerts',
    subtitle: 'Monitor changing disaster conditions',
    description:
      'Live Alerts provides responders with immediate visibility into important disaster signals and emerging situations, helping authorities adapt their response as conditions change.',
    icon: BellRing,
    tab: 'flood-alerts',
    accent: 'red',
    points: [
      'Real-time disaster awareness',
      'High-priority alert visibility',
      'Rapid operational notification',
      'Supports proactive decisions',
    ],
    flow: [
      'Live Signal',
      'Alert Generated',
      'Authority Notified',
      'Response Adjusted',
    ],
  },

  {
    id: 8,
    title: 'Evacuation & Emergency Response',
    subtitle: 'Handle life-critical situations separately',
    description:
      'Evacuation requests follow a dedicated emergency workflow instead of supply matching, allowing authorities to approve evacuation and coordinate the appropriate response.',
    icon: AlertTriangle,
    tab: 'evacuation',
    accent: 'red',
    points: [
      'Dedicated evacuation workflow',
      'Authority approval',
      'Emergency response coordination',
      'Life-critical action tracking',
    ],
    flow: [
      'Evacuation Request',
      'Authority Approval',
      'Response Unit',
      'Emergency Action',
    ],
  },

  {
    id: 9,
    title: 'Relief Distribution & Traceability',
    subtitle: 'Track assistance from allocation to delivery',
    description:
      'After resources are allocated, ResQFlow provides visibility across dispatch and delivery so relief movement remains traceable and accountable.',
    icon: PackageCheck,
    tab: 'trace',
    accent: 'terracotta',
    points: [
      'Track allocated resources',
      'Monitor dispatch progress',
      'Maintain delivery traceability',
      'Improve accountability',
    ],
    flow: [
      'Allocation',
      'Manifest',
      'Dispatch',
      'Delivery',
    ],
  },

  {
    id: 10,
    title: 'Volunteer & NGO Coordination',
    subtitle: 'Bring the response ecosystem together',
    description:
      'ResQFlow allows volunteers and NGOs to participate in the larger relief operation, helping organizations contribute manpower, supplies and support where they are needed.',
    icon: Users,
    tab: 'volunteer',
    accent: 'blue',
    points: [
      'Volunteer coordination',
      'NGO participation',
      'Resource contribution',
      'Collaborative disaster response',
    ],
    flow: [
      'Need Identified',
      'NGO / Volunteer',
      'Contribution',
      'Relief Operation',
    ],
  },

  {
    id: 11,
    title: 'Analytics & Insights',
    subtitle: 'Turn response activity into actionable intelligence',
    description:
      'Operational analytics help decision-makers understand demand, response performance, resource movement and overall disaster-relief activity.',
    icon: BarChart3,
    tab: 'analytics',
    accent: 'purple',
    points: [
      'Operational performance insights',
      'Response and distribution statistics',
      'Resource utilization visibility',
      'Data-driven decision making',
    ],
    flow: [
      'Platform Activity',
      'Data Collection',
      'Analytics',
      'Decision Support',
    ],
  },

  {
    id: 12,
    title: 'Audit Trail',
    subtitle: 'Make important actions accountable',
    description:
      'The Audit Trail preserves a record of important platform actions, helping administrators and authorities understand what happened, when it happened and which workflow was involved.',
    icon: ClipboardCheck,
    tab: 'audit',
    accent: 'navy',
    points: [
      'Track important system actions',
      'Preserve operational history',
      'Support accountability',
      'Improve transparency',
    ],
    flow: [
      'User Action',
      'System Event',
      'Audit Record',
      'Accountability',
    ],
  },

  {
    id: 13,
    title: 'User Management',
    subtitle: 'Control participation and operational access',
    description:
      'Administrators can manage platform users and assign appropriate roles, ensuring each participant receives access aligned with their responsibility.',
    icon: UserCog,
    tab: 'admin-users',
    accent: 'navy',
    points: [
      'Manage platform users',
      'Assign operational roles',
      'Support role-based workflows',
      'Maintain controlled access',
    ],
    flow: [
      'User',
      'Role',
      'Permissions',
      'Platform Access',
    ],
  },

  {
    id: 14,
    title: 'System Settings',
    subtitle: 'Configure the platform for reliable operations',
    description:
      'System administrators can configure core platform behaviour and operational settings so ResQFlow can adapt to different disaster-response environments.',
    icon: Settings,
    tab: 'admin-settings',
    accent: 'slate',
    points: [
      'Configure system behaviour',
      'Maintain operational settings',
      'Support deployment readiness',
      'Prepare for scale',
    ],
    flow: [
      'Configuration',
      'System Rules',
      'Operational Environment',
      'Ready for Response',
    ],
  },

  {
    id: 15,
    title: 'Complete End-to-End Workflow',
    subtitle: 'From first report to accountable relief',
    description:
      'ResQFlow brings every major stage together: community reporting, authority action, intelligent matching, emergency response, relief distribution and transparent monitoring.',
    icon: ShieldCheck,
    accent: 'terracotta',
    points: [
      'One connected disaster-response workflow',
      'Human decisions supported by technology',
      'Emergency and supply workflows remain distinct',
      'Every major action can be tracked',
    ],
    flow: [
      'Report',
      'Verify',
      'Match',
      'Respond',
      'Distribute',
      'Track',
    ],
  },
];

const accentClasses: Record<string, string> = {
  terracotta: 'bg-terracotta text-white',
  blue: 'bg-blue-600 text-white',
  navy: 'bg-navy text-white',
  purple: 'bg-purple-600 text-white',
  orange: 'bg-orange-500 text-white',
  green: 'bg-green-600 text-white',
  red: 'bg-red-600 text-white',
  slate: 'bg-slate-600 text-white',
};

function FlowVisualization({ items }: { items: string[] }) {
  return (
    <div className="mt-8 rounded-2xl border border-slate-200 bg-white/80 p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <GitBranch className="h-4 w-4 text-terracotta" />

        <span className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
          Workflow
        </span>
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-center">
        {items.map((item, index) => (
          <React.Fragment key={item}>
            <div className="flex min-h-[58px] flex-1 items-center justify-center rounded-xl border border-slate-200 bg-ivory px-4 py-3 text-center text-sm font-semibold text-navy shadow-sm">
              {item}
            </div>

            {index < items.length - 1 && (
              <>
                <ArrowRight className="hidden h-4 w-4 shrink-0 text-slate-400 md:block" />

                <div className="flex justify-center md:hidden">
                  <ChevronRight className="h-4 w-4 rotate-90 text-slate-400" />
                </div>
              </>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default function JudgeModePage() {
  const {
    judgeModeStep,
    setJudgeModeStep,
    setJudgeMode,
    activeTab,
    setActiveTab,
  } = useApp();

  const safeStep = Math.min(
    Math.max(judgeModeStep, 0),
    steps.length - 1
  );

  const step = steps[safeStep];
  const StepIcon = step.icon;

  const isViewingModule =
    activeTab !== 'judge-mode' &&
    activeTab !== 'landing';

  const nextStep = () => {
    if (safeStep < steps.length - 1) {
      setJudgeModeStep(safeStep + 1);
      setActiveTab('judge-mode');
    } else {
      setJudgeMode(false);
      setJudgeModeStep(0);
      setActiveTab('landing');
    }
  };

  const previousStep = () => {
    if (safeStep > 0) {
      setJudgeModeStep(safeStep - 1);
      setActiveTab('judge-mode');
    }
  };

  const openModule = () => {
    if (!step.tab) return;

    setActiveTab(step.tab);
  };

  const exitDemo = () => {
    setJudgeMode(false);
    setJudgeModeStep(0);
    setActiveTab('landing');
  };

  /*
   * When a judge opens a real module, keep the Judge Mode
   * controller visible above the page/map.
   */
  if (isViewingModule) {
    return (
      <div className="fixed bottom-5 left-1/2 z-[9999] w-[min(920px,calc(100%-32px))] -translate-x-1/2">
        <div className="rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-2xl backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div
              className={`hidden h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:flex ${
                accentClasses[step.accent]
              }`}
            >
              <StepIcon className="h-5 w-5" />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-terracotta">
                  Judge Mode
                </span>

                <span className="text-[10px] text-slate-400">
                  {safeStep + 1} / {steps.length}
                </span>
              </div>

              <p className="truncate text-sm font-bold text-navy">
                {step.title}
              </p>
            </div>

            <button
              type="button"
              onClick={() => setActiveTab('judge-mode')}
              className="hidden rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-50 sm:block"
            >
              Back to Explanation
            </button>

            <button
              type="button"
              onClick={previousStep}
              disabled={safeStep === 0}
              className="rounded-lg border border-slate-200 p-2 text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              title="Previous"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={nextStep}
              className="flex items-center gap-1.5 rounded-lg bg-navy px-3 py-2 text-xs font-bold text-white transition-colors hover:opacity-90"
            >
              {safeStep === steps.length - 1 ? 'Finish' : 'Next'}

              <ChevronRight className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={exitDemo}
              className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
              title="Exit Judge Mode"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-terracotta transition-all duration-300"
              style={{
                width: `${((safeStep + 1) / steps.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-ivory px-4 py-6 md:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">

        {/* Header */}
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-navy">
                <Presentation className="h-5 w-5 text-white" />
              </div>

              <span className="text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
                Hackathon Judge Mode
              </span>
            </div>

            <h1 className="text-2xl font-black tracking-tight text-navy md:text-3xl">
              ResQFlow
            </h1>

            <p className="mt-1 max-w-2xl text-sm text-slate-500">
              A guided walkthrough of the complete disaster-relief response
              ecosystem.
            </p>
          </div>

          <button
            type="button"
            onClick={exitDemo}
            className="flex w-fit items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-600 shadow-sm transition-colors hover:bg-slate-50"
          >
            <X className="h-4 w-4" />
            Exit Demo
          </button>
        </div>

        {/* Progress */}
        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">
              DEMO PROGRESS
            </span>

            <span className="text-xs font-bold text-navy">
              {safeStep + 1} / {steps.length}
            </span>
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-terracotta transition-all duration-500"
              style={{
                width: `${((safeStep + 1) / steps.length) * 100}%`,
              }}
            />
          </div>

          <div className="mt-4 flex gap-1.5 overflow-x-auto pb-1">
            {steps.map((item, index) => (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  setJudgeModeStep(index);
                  setActiveTab('judge-mode');
                }}
                className={`h-2 min-w-[24px] flex-1 rounded-full transition-all ${
                  index === safeStep
                    ? 'bg-terracotta'
                    : index < safeStep
                      ? 'bg-navy'
                      : 'bg-slate-200'
                }`}
                title={`${index + 1}. ${item.title}`}
              />
            ))}
          </div>
        </div>

        {/* Main Slide */}
        <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl">
          <div className="grid lg:grid-cols-[1.05fr_0.95fr]">

            {/* Left content */}
            <div className="p-6 md:p-9 lg:p-12">
              <div className="mb-7 flex items-start justify-between">
                <div
                  className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
                    accentClasses[step.accent]
                  } shadow-lg`}
                >
                  <StepIcon className="h-7 w-7" />
                </div>

                <div className="text-right">
                  <div className="text-4xl font-black leading-none text-slate-100">
                    {String(step.id).padStart(2, '0')}
                  </div>

                  <div className="mt-1 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                    Step
                  </div>
                </div>
              </div>

              <div className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
                {step.subtitle}
              </div>

              <h2 className="max-w-2xl text-3xl font-black tracking-tight text-navy md:text-4xl">
                {step.title}
              </h2>

              <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-600 md:text-base">
                {step.description}
              </p>

              <div className="mt-7 grid gap-3 sm:grid-cols-2">
                {step.points.map((point) => (
                  <div
                    key={point}
                    className="flex items-start gap-3 rounded-xl border border-slate-100 bg-ivory/70 p-3"
                  >
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-terracotta" />

                    <span className="text-xs font-medium leading-5 text-slate-600">
                      {point}
                    </span>
                  </div>
                ))}
              </div>

              {step.tab && (
                <button
                  type="button"
                  onClick={openModule}
                  className="mt-8 flex items-center gap-2 rounded-xl bg-navy px-5 py-3 text-sm font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 hover:shadow-xl"
                >
                  Open Live Module
                  <ArrowRight className="h-4 w-4" />
                </button>
              )}

              {!step.tab && safeStep === 0 && (
                <div className="mt-8 flex items-center gap-2 rounded-xl border border-terracotta/20 bg-terracotta/5 px-4 py-3 text-xs font-semibold text-navy">
                  <ShieldCheck className="h-4 w-4 text-terracotta" />
                  Guided system overview
                </div>
              )}

              {!step.tab && safeStep === steps.length - 1 && (
                <div className="mt-8 flex items-center gap-2 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-xs font-semibold text-green-800">
                  <CheckCircle2 className="h-4 w-4" />
                  Complete ResQFlow workflow
                </div>
              )}
            </div>

            {/* Right visual */}
            <div className="relative overflow-hidden bg-navy p-6 md:p-9 lg:p-10">
              {/* Grid background */}
              <div className="absolute inset-0 opacity-[0.08]">
                <div
                  className="h-full w-full"
                  style={{
                    backgroundImage:
                      'linear-gradient(rgba(255,255,255,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.35) 1px, transparent 1px)',
                    backgroundSize: '32px 32px',
                  }}
                />
              </div>

              <div className="relative">
                <div className="mb-7 flex items-center justify-between">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                      ResQFlow Architecture
                    </p>

                    <p className="mt-1 text-lg font-bold text-white">
                      How this module fits
                    </p>
                  </div>

                  <div className="rounded-xl bg-white/10 p-3">
                    <Activity className="h-5 w-5 text-white" />
                  </div>
                </div>

                {/* Flow */}
                <div className="space-y-3">
                  {step.flow.map((item, index) => (
                    <React.Fragment key={item}>
                      <div className="group flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.07] p-4 backdrop-blur-sm transition-all hover:bg-white/[0.12]">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/10 text-sm font-black text-white">
                          {index + 1}
                        </div>

                        <div className="flex-1">
                          <div className="text-sm font-bold text-white">
                            {item}
                          </div>

                          <div className="mt-1 text-[10px] uppercase tracking-wider text-slate-400">
                            Workflow stage
                          </div>
                        </div>

                        {index === step.flow.length - 1 ? (
                          <CheckCircle2 className="h-5 w-5 text-green-400" />
                        ) : (
                          <ArrowRight className="h-4 w-4 text-slate-500" />
                        )}
                      </div>
                    </React.Fragment>
                  ))}
                </div>

                {/* System capability card */}
                <div className="mt-7 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
                  <div className="mb-4 flex items-center gap-2">
                    <Database className="h-4 w-4 text-terracotta" />

                    <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
                      System Capability
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-xl bg-white/[0.06] p-3">
                      <Radio className="mb-2 h-4 w-4 text-white" />

                      <p className="text-xs font-bold text-white">
                        Connected
                      </p>

                      <p className="mt-1 text-[10px] text-slate-400">
                        Shared operational workflow
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/[0.06] p-3">
                      <ShieldCheck className="mb-2 h-4 w-4 text-white" />

                      <p className="text-xs font-bold text-white">
                        Accountable
                      </p>

                      <p className="mt-1 text-[10px] text-slate-400">
                        Traceable response actions
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom navigation */}
          <div className="flex flex-col gap-4 border-t border-slate-200 bg-slate-50 px-6 py-4 sm:flex-row sm:items-center sm:justify-between md:px-9">
            <button
              type="button"
              onClick={previousStep}
              disabled={safeStep === 0}
              className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>

            <div className="order-first text-center sm:order-none">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                Next
              </p>

              <p className="mt-1 text-xs font-bold text-navy">
                {safeStep < steps.length - 1
                  ? steps[safeStep + 1].title
                  : 'Return to ResQFlow'}
              </p>
            </div>

            <button
              type="button"
              onClick={nextStep}
              className="flex items-center justify-center gap-2 rounded-xl bg-navy px-5 py-3 text-sm font-bold text-white shadow-md transition-all hover:-translate-y-0.5 hover:shadow-lg"
            >
              {safeStep === steps.length - 1
                ? 'Finish Demo'
                : 'Next Step'}

              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Module navigation strip */}
        <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-8">
          {steps.slice(1, -1).map((item, index) => {
            const Icon = item.icon;
            const actualIndex = index + 1;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  setJudgeModeStep(actualIndex);
                  setActiveTab('judge-mode');
                }}
                className={`group rounded-xl border p-3 text-left transition-all ${
                  actualIndex === safeStep
                    ? 'border-terracotta bg-terracotta/5'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
                }`}
              >
                <Icon
                  className={`mb-2 h-4 w-4 ${
                    actualIndex === safeStep
                      ? 'text-terracotta'
                      : 'text-slate-400 group-hover:text-navy'
                  }`}
                />

                <p className="line-clamp-2 text-[10px] font-bold leading-4 text-navy">
                  {item.title}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}