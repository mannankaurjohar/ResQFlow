import React from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  Database,
  FileSearch,
  GitBranch,
  HeartHandshake,
  History,
  House,
  LayoutDashboard,
  MapPin,
  Package,
  Radio,
  Settings,
  ShieldCheck,
  Truck,
  UserCog,
  Users,
  UserRound,
  Warehouse,
  Waves,
  Zap
} from 'lucide-react';
import { useApp } from '../context/AppContext';

type FlowNode = {
  label: string;
  sub?: string;
  icon: React.ElementType;
};

type JudgeStep = {
  title: string;
  subtitle: string;
  description: string;
  points: string[];
  tab?: string;
  icon: React.ElementType;
  accent: string;
  flow: FlowNode[];
};

const steps: JudgeStep[] = [
  {
    title: 'What is ResQFlow?',
    subtitle: 'AI-Powered Disaster Relief Coordination',
    description:
      'ResQFlow brings communities, authorities, AI-assisted resource allocation, emergency teams, NGOs and volunteers into one coordinated disaster-response platform.',
    points: [
      'One platform for the complete relief lifecycle',
      'AI-assisted decisions for faster resource allocation',
      'Dedicated emergency response workflows',
      'Traceable and transparent operations'
    ],
    icon: Waves,
    accent: 'Disaster coordination',
    flow: [
      { label: 'Community', sub: 'Report', icon: UserRound },
      { label: 'ResQFlow', sub: 'Coordinate', icon: LayoutDashboard },
      { label: 'Authority', sub: 'Decide', icon: ShieldCheck },
      { label: 'Response', sub: 'Act', icon: Zap },
      { label: 'Relief', sub: 'Deliver', icon: HeartHandshake }
    ]
  },
  {
    title: 'Community Reports a Need',
    subtitle: 'Turn Local Problems Into Actionable Requests',
    description:
      'Affected people can report urgent requirements such as food, medicine, shelter or evacuation support. The request becomes a structured case that can enter the response workflow.',
    points: [
      'Simple emergency reporting',
      'Supply and evacuation requests',
      'Location and priority information',
      'Request status tracking'
    ],
    tab: 'report',
    icon: Radio,
    accent: 'Community intake',
    flow: [
      { label: 'Affected Person', sub: 'Needs help', icon: UserRound },
      { label: 'Emergency Need', sub: 'Food / Shelter / Help', icon: AlertTriangle },
      { label: 'Location', sub: 'Where?', icon: MapPin },
      { label: 'ResQFlow', sub: 'Request created', icon: Radio }
    ]
  },
  {
    title: 'Authority Verifies & Prioritizes',
    subtitle: 'Turn Incoming Reports Into Decisions',
    description:
      'Authorities receive incoming cases through a centralized command center. They can review the request, verify its information and prioritize urgent situations for action.',
    points: [
      'Central command dashboard',
      'Request verification',
      'Priority-based handling',
      'Emergency escalation'
    ],
    tab: 'command',
    icon: ClipboardCheck,
    accent: 'Command center',
    flow: [
      { label: 'Incoming Requests', sub: 'Multiple cases', icon: ClipboardList },
      { label: 'Verify', sub: 'Check information', icon: FileSearch },
      { label: 'Prioritize', sub: 'Urgency', icon: AlertTriangle },
      { label: 'Action Queue', sub: 'Ready to respond', icon: CheckCircle2 }
    ]
  },
  {
    title: 'AI Matches Relief Resources',
    subtitle: 'Connect Demand With Available Resources',
    description:
      'For supply requests, the AI-assisted matching workflow connects community demand with available inventory and helps authorities identify suitable resources for allocation.',
    points: [
      'Demand analysis',
      'Available-stock matching',
      'Warehouse coordination',
      'Allocation approval'
    ],
    tab: 'warehouse',
    icon: Bot,
    accent: 'AI-assisted allocation',
    flow: [
      { label: 'Community Need', sub: 'Demand', icon: ClipboardList },
      { label: 'AI Matching', sub: 'Need ↔ Stock', icon: Bot },
      { label: 'Inventory', sub: 'Available resources', icon: Warehouse },
      { label: 'Allocation', sub: 'Approved', icon: CheckCircle2 }
    ]
  },
  {
    title: 'Create Response Team',
    subtitle: 'Prepare the Right Team for the Emergency',
    description:
      'Authorities can create operational response units such as NDRF, SDRF, Fire & Rescue and authorized local teams, then assign an appropriate operator.',
    points: [
      'Create emergency response teams',
      'Select response organization',
      'Assign a qualified operator',
      'Prepare teams for deployment'
    ],
    tab: 'response-units',
    icon: Users,
    accent: 'Team creation',
    flow: [
      { label: 'Emergency', sub: 'Response required', icon: AlertTriangle },
      { label: 'Team Type', sub: 'NDRF / SDRF / Fire', icon: Users },
      { label: 'Operator', sub: 'Assigned', icon: UserCog },
      { label: 'Ready', sub: 'Available for action', icon: CheckCircle2 }
    ]
  },
  {
    title: 'Response Unit Management',
    subtitle: 'Maintain Operational Readiness',
    description:
      'Once response units are registered, authorities can monitor their availability, assigned operators and readiness from a centralized operational view.',
    points: [
      'View registered response units',
      'Monitor availability',
      'Manage operator assignments',
      'Track operational readiness'
    ],
    tab: 'response-units',
    icon: ShieldCheck,
    accent: 'Operational readiness',
    flow: [
      { label: 'Response Units', sub: 'Registered teams', icon: Users },
      { label: 'Availability', sub: 'Ready / busy', icon: Activity },
      { label: 'Operator', sub: 'Assigned personnel', icon: UserCog },
      { label: 'Deployment', sub: 'Ready when needed', icon: Truck }
    ]
  },
  {
    title: 'Response Operator Tasks',
    subtitle: 'Turn Decisions Into Field Action',
    description:
      'Response operators receive operational tasks and manage their progress from the field, creating a direct connection between command decisions and execution.',
    points: [
      'View assigned tasks',
      'Accept and manage operations',
      'Update task progress',
      'Complete field activities'
    ],
    tab: 'response-tasks',
    icon: ClipboardList,
    accent: 'Field execution',
    flow: [
      { label: 'Command', sub: 'Assignment', icon: ShieldCheck },
      { label: 'Operator', sub: 'Receives task', icon: UserCog },
      { label: 'Field Action', sub: 'Execute', icon: Truck },
      { label: 'Completed', sub: 'Status updated', icon: CheckCircle2 }
    ]
  },
  {
    title: 'Evacuation & Emergency Response',
    subtitle: 'A Dedicated Workflow for Critical Situations',
    description:
      'Evacuation requests follow a dedicated emergency workflow rather than normal supply matching. Authorities can approve the case and coordinate an appropriate response team.',
    points: [
      'Dedicated evacuation approval',
      'Emergency prioritization',
      'Response-unit coordination',
      'Status tracking'
    ],
    tab: 'evacuation',
    icon: AlertTriangle,
    accent: 'Emergency response',
    flow: [
      { label: 'Evacuation Request', sub: 'Critical need', icon: AlertTriangle },
      { label: 'Approval', sub: 'Authority decision', icon: ShieldCheck },
      { label: 'Response Team', sub: 'Deploy', icon: Users },
      { label: 'Evacuation', sub: 'People moved to safety', icon: House }
    ]
  },
  {
    title: 'Relief Distribution',
    subtitle: 'Track Relief From Source to Destination',
    description:
      'After allocation, ResQFlow provides visibility into the movement of relief resources so that operations can be followed from their source through delivery.',
    points: [
      'Relief movement tracking',
      'Distribution status',
      'Request-to-delivery visibility',
      'Traceable operations'
    ],
    tab: 'trace',
    icon: Truck,
    accent: 'End-to-end traceability',
    flow: [
      { label: 'Warehouse', sub: 'Resource source', icon: Warehouse },
      { label: 'Dispatch', sub: 'Relief movement', icon: Package },
      { label: 'Distribution', sub: 'Destination', icon: Truck },
      { label: 'Delivered', sub: 'Community receives help', icon: CheckCircle2 }
    ]
  },
  {
    title: 'Volunteer & NGO Coordination',
    subtitle: 'Bring the Relief Network Together',
    description:
      'Disaster response extends beyond government teams. ResQFlow connects volunteers and NGOs with the wider operation so field support and relief activities can be coordinated.',
    points: [
      'Volunteer coordination',
      'NGO participation',
      'Field support',
      'Relief network collaboration'
    ],
    tab: 'volunteer',
    icon: HeartHandshake,
    accent: 'Relief network',
    flow: [
      { label: 'Authority', sub: 'Coordinate', icon: ShieldCheck },
      { label: 'NGOs', sub: 'Support', icon: HeartHandshake },
      { label: 'Volunteers', sub: 'Act locally', icon: Users },
      { label: 'Community', sub: 'Receive support', icon: UserRound }
    ]
  },
  {
    title: 'Analytics & Transparency',
    subtitle: 'Turn Operational Data Into Decisions',
    description:
      'ResQFlow converts operational activity into useful insights so decision-makers can understand response performance, resource usage and the overall state of relief operations.',
    points: [
      'Response statistics',
      'Resource and request insights',
      'Operational performance',
      'Decision support'
    ],
    tab: 'analytics',
    icon: BarChart3,
    accent: 'Operational intelligence',
    flow: [
      { label: 'Operations', sub: 'Live activity', icon: Activity },
      { label: 'Data', sub: 'Collected', icon: Database },
      { label: 'Analytics', sub: 'Patterns & metrics', icon: BarChart3 },
      { label: 'Decision', sub: 'Better response', icon: Zap }
    ]
  },
  {
    title: 'Audit Trail',
    subtitle: 'Make Every Important Action Traceable',
    description:
      'Disaster operations involve many users and critical decisions. The audit trail provides a chronological record of important actions, supporting accountability and operational transparency.',
    points: [
      'Action history',
      'User accountability',
      'Timestamped activity',
      'Transparent operational records'
    ],
    tab: 'audit',
    icon: History,
    accent: 'Accountability',
    flow: [
      { label: 'User', sub: 'Performs action', icon: UserRound },
      { label: 'Action', sub: 'System event', icon: Activity },
      { label: 'Timestamp', sub: 'When it happened', icon: History },
      { label: 'Audit Record', sub: 'Traceable history', icon: FileSearch }
    ]
  },
  {
    title: 'User Management',
    subtitle: 'Control Who Can Operate the Platform',
    description:
      'ResQFlow supports multiple operational roles. Administrators can manage platform users and maintain the right organizational access for each participant in the disaster-response ecosystem.',
    points: [
      'Manage platform users',
      'Assign operational roles',
      'Control organizational access',
      'Maintain active accounts'
    ],
    tab: 'admin-users',
    icon: UserCog,
    accent: 'Platform administration',
    flow: [
      { label: 'Administrator', sub: 'Platform control', icon: ShieldCheck },
      { label: 'Users', sub: 'Accounts', icon: Users },
      { label: 'Roles', sub: 'Permissions', icon: UserCog },
      { label: 'Access', sub: 'Controlled operation', icon: CheckCircle2 }
    ]
  },
  {
    title: 'System Settings',
    subtitle: 'Configure and Maintain ResQFlow',
    description:
      'System settings provide administrators with centralized control over platform configuration, allowing the application to remain consistent, controlled and ready for real-world deployment.',
    points: [
      'Centralized system configuration',
      'Administrative controls',
      'Platform maintenance',
      'Controlled operation'
    ],
    tab: 'admin-settings',
    icon: Settings,
    accent: 'System administration',
    flow: [
      { label: 'Administrator', sub: 'Authorized access', icon: ShieldCheck },
      { label: 'Settings', sub: 'Configuration', icon: Settings },
      { label: 'Platform', sub: 'Apply controls', icon: LayoutDashboard },
      { label: 'Ready', sub: 'Consistent operation', icon: CheckCircle2 }
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
  const CurrentIcon = current.icon;

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

  function exitDemo() {
    setJudgeMode(false);
    setJudgeModeStep(0);
    setActiveTab('landing');
  }

  /*
   * Full Judge Mode introduction screen.
   */
  if (!isViewingModule) {
    return (
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
        <div className="bg-white rounded-3xl border border-navy/10 shadow-elevated overflow-hidden">
          {/* Header */}
          <div className="px-6 md:px-10 pt-7 pb-5 border-b border-navy/10">
            <div className="flex items-start justify-between gap-5">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-navy flex items-center justify-center shrink-0">
                  <PresentationIcon />
                </div>

                <div>
                  <div className="text-[10px] md:text-xs font-bold uppercase tracking-[0.2em] text-terracotta">
                    Hackathon Judge Mode
                  </div>

                  <h1 className="text-2xl md:text-3xl font-bold text-navy mt-1">
                    ResQFlow
                  </h1>

                  <p className="text-sm text-slate mt-1">
                    Guided product demonstration • No login required
                  </p>
                </div>
              </div>

              <button
                onClick={exitDemo}
                className="px-4 py-2 rounded-xl border border-navy/15 text-navy text-xs md:text-sm font-semibold hover:bg-ivory transition-colors"
              >
                Exit Demo
              </button>
            </div>

            {/* Progress */}
            <div className="mt-7">
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate">
                  Demonstration Progress
                </span>

                <span className="text-navy">
                  {judgeModeStep + 1} / {steps.length}
                </span>
              </div>

              <div className="h-2 bg-navy/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-terracotta transition-all duration-500"
                  style={{
                    width: `${((judgeModeStep + 1) / steps.length) * 100}%`
                  }}
                />
              </div>

              {/* Step dots */}
              <div className="hidden md:flex items-center justify-between mt-3">
                {steps.map((step, index) => (
                  <button
                    key={step.title}
                    onClick={() => {
                      setJudgeModeStep(index);
                      setActiveTab('judge-mode');
                    }}
                    title={step.title}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === judgeModeStep
                        ? 'bg-terracotta scale-150'
                        : index < judgeModeStep
                          ? 'bg-navy'
                          : 'bg-navy/15'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Main content */}
          <div className="p-6 md:p-10">
            <div className="grid lg:grid-cols-[1fr_1.05fr] gap-8 lg:gap-12 items-center">
              {/* Left: explanation */}
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-terracotta/10 text-terracotta text-[10px] font-bold uppercase tracking-wider">
                  <CurrentIcon className="w-3.5 h-3.5" />
                  {current.accent}
                </div>

                <div className="mt-5 flex items-start gap-4">
                  <div className="text-5xl md:text-6xl font-black text-navy/10 leading-none">
                    {String(judgeModeStep + 1).padStart(2, '0')}
                  </div>

                  <div>
                    <h2 className="text-3xl md:text-4xl font-bold text-navy leading-tight">
                      {current.title}
                    </h2>

                    <p className="text-lg font-semibold text-terracotta mt-2">
                      {current.subtitle}
                    </p>
                  </div>
                </div>

                <p className="text-slate leading-7 mt-6 text-sm md:text-base max-w-2xl">
                  {current.description}
                </p>

                <div className="grid sm:grid-cols-2 gap-3 mt-6">
                  {current.points.map((point) => (
                    <div
                      key={point}
                      className="flex items-start gap-3 p-3.5 rounded-xl bg-ivory border border-navy/10"
                    >
                      <div className="w-5 h-5 shrink-0 rounded-full bg-terracotta text-white flex items-center justify-center">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </div>

                      <span className="text-xs md:text-sm font-medium text-navy leading-5">
                        {point}
                      </span>
                    </div>
                  ))}
                </div>

                {current.tab && (
                  <button
                    onClick={openModule}
                    className="mt-7 inline-flex items-center gap-2 bg-navy hover:bg-navy/90 text-white px-5 py-3 rounded-xl text-sm font-bold transition-all shadow-sm"
                  >
                    Open Live Module
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Right: visual flowchart */}
              <FlowVisualization
                flow={current.flow}
                step={judgeModeStep}
              />
            </div>
          </div>

          {/* Bottom navigation */}
          <div className="border-t border-navy/10 bg-ivory/70 px-6 md:px-10 py-4 flex items-center justify-between gap-4">
            <button
              disabled={judgeModeStep === 0}
              onClick={previousStep}
              className="px-4 py-2.5 rounded-xl border border-navy/15 text-navy text-sm font-semibold hover:bg-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              ← Previous
            </button>

            <div className="hidden sm:flex items-center gap-2 text-xs text-slate">
              <span className="font-semibold text-navy">
                {judgeModeStep + 1}
              </span>
              <span>of</span>
              <span>{steps.length}</span>
            </div>

            <button
              onClick={nextStep}
              className="px-5 py-2.5 rounded-xl bg-terracotta hover:bg-terracotta-hover text-white text-sm font-bold transition-colors"
            >
              {judgeModeStep === steps.length - 1
                ? 'Finish Demo'
                : 'Next Step →'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  /*
   * Persistent controller while the judge is viewing
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
              className="px-3 py-2 rounded-lg border border-white/20 text-xs font-semibold disabled:opacity-30 hover:bg-white/5"
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
              className="px-3 py-2 rounded-lg border border-white/20 text-xs font-semibold hover:bg-white/5"
            >
              Exit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* Flow visualization                                                          */
/* -------------------------------------------------------------------------- */

const FlowVisualization: React.FC<{
  flow: FlowNode[];
  step: number;
}> = ({ flow, step }) => {
  return (
    <div className="relative">
      <div className="absolute -inset-4 bg-terracotta/[0.03] rounded-[2rem] pointer-events-none" />

      <div className="relative bg-ivory border border-navy/10 rounded-3xl p-5 md:p-7 overflow-hidden">
        {/* Decorative grid */}
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(15,30,54,1) 1px, transparent 1px), linear-gradient(90deg, rgba(15,30,54,1) 1px, transparent 1px)',
            backgroundSize: '24px 24px'
          }}
        />

        <div className="relative">
          <div className="flex items-center justify-between mb-5">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate">
                Workflow
              </div>

              <div className="text-sm font-bold text-navy mt-1">
                How ResQFlow handles this stage
              </div>
            </div>

            <div className="w-9 h-9 rounded-xl bg-white border border-navy/10 flex items-center justify-center">
              <GitBranch className="w-4 h-4 text-terracotta" />
            </div>
          </div>

          <div className="space-y-2">
            {flow.map((node, index) => {
              const Icon = node.icon;
              const isLast = index === flow.length - 1;

              return (
                <React.Fragment key={`${node.label}-${index}`}>
                  <div
                    className="group bg-white rounded-2xl border border-navy/10 p-3.5 flex items-center gap-3.5 shadow-sm"
                  >
                    <div
                      className={`w-10 h-10 shrink-0 rounded-xl flex items-center justify-center ${
                        index === 0
                          ? 'bg-navy text-white'
                          : isLast
                            ? 'bg-terracotta text-white'
                            : 'bg-terracotta/10 text-terracotta'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>

                    <div className="min-w-0">
                      <div className="text-sm font-bold text-navy">
                        {node.label}
                      </div>

                      {node.sub && (
                        <div className="text-[11px] text-slate mt-0.5">
                          {node.sub}
                        </div>
                      )}
                    </div>

                    {isLast && (
                      <CheckCircle2 className="w-4 h-4 text-terracotta ml-auto shrink-0" />
                    )}
                  </div>

                  {!isLast && (
                    <div className="flex justify-center h-5">
                      <div className="flex flex-col items-center">
                        <div className="w-px h-3 bg-navy/20" />
                        <ArrowDown className="w-3.5 h-3.5 text-terracotta" />
                      </div>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          <div className="mt-5 p-3 rounded-xl bg-navy text-white">
            <div className="flex items-center gap-2">
              <Zap className="w-3.5 h-3.5 text-terracotta" />

              <span className="text-[10px] uppercase tracking-wider font-bold text-slate-light">
                ResQFlow principle
              </span>
            </div>

            <p className="text-xs font-medium mt-1.5 leading-5 text-ivory/90">
              Connect the right people, information and resources at the
              right point in the response.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* Presentation icon                                                           */
/* -------------------------------------------------------------------------- */

const PresentationIcon: React.FC = () => (
  <div className="relative w-6 h-6">
    <div className="absolute left-1 top-1 w-4 h-3.5 border-2 border-white rounded-sm" />
    <div className="absolute left-3 top-0 w-0.5 h-1 bg-white" />
    <div className="absolute left-1/2 bottom-1 w-0.5 h-1.5 bg-white" />
    <div className="absolute left-1.5 bottom-0 w-3 h-0.5 bg-white" />
  </div>
);

export default JudgeModePage;