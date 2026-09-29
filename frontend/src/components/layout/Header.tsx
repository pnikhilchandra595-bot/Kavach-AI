import React from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Flame, 
  Play, 
  RotateCcw, 
  Power, 
  HardDrive,
  FileCheck2,
  AlertTriangle,
  Zap,
  UserCheck
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';
import { DEMO_SCENARIOS } from '../../mockData/demoScenarios';

export const Header: React.FC = () => {
  const {
    activeScenario,
    selectScenario,
    isRunning,
    currentStepIndex,
    runCurrentScenario,
    resetScenario,
    killSwitchActive,
    toggleKillSwitch,
    networkStats,
    setApprovalGateOpen,
    setDeliverableModalOpen,
    isDegradedMode,
    toggleDegradedMode,
    operatorRbac
  } = useWorkbench();

  return (
    <header className="border-b border-industrial-700 bg-industrial-900/95 backdrop-blur sticky top-0 z-40">
      
      {/* Top Telemetry Strip */}
      <div className="px-4 py-1.5 bg-industrial-950 border-b border-industrial-800 text-xs flex flex-wrap items-center justify-between gap-3 font-mono">
        <div className="flex items-center gap-4 text-slate-400">
          <span className="flex items-center gap-1.5 text-slate-200">
            <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <strong className="text-cyan-300 font-semibold tracking-wide">MRPL SOVEREIGN WORKBENCH</strong>
            <span className="text-slate-500">|</span>
            <span className="text-slate-300">SIH26117 Smart Automation</span>
          </span>

          <span className="hidden md:flex items-center gap-1 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>
              {isDegradedMode ? 'Venue Tier: Minimum 8-12GB GPU / CPU' : 'NVIDIA RTX 4090 24GB (100% On-Premise)'}
            </span>
          </span>

          <span className="hidden lg:flex items-center gap-1 text-slate-400">
            <HardDrive className="w-3.5 h-3.5 text-purple-400" />
            <span>IPC Loopback: <strong className="text-purple-300">{networkStats.loopbackMBs} MB/s</strong></span>
          </span>

          <span className="hidden xl:flex items-center gap-1 text-slate-400">
            <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>RBAC: <strong className="text-slate-200">{operatorRbac.currentUser}</strong> ({operatorRbac.currentRole})</span>
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Hardware Capacity Degraded Mode Toggle */}
          <button
            onClick={toggleDegradedMode}
            className={`flex items-center gap-1 px-2 py-0.5 rounded border text-[11px] font-mono transition ${
              isDegradedMode
                ? 'bg-amber-950/80 text-amber-300 border-amber-600 font-bold glow-amber animate-pulse'
                : 'bg-industrial-850 text-slate-300 border-industrial-700 hover:border-industrial-600'
            }`}
            title="Toggle between optimal GPU capacity and venue minimum hardware fallback tier"
          >
            <Zap className={`w-3 h-3 ${isDegradedMode ? 'text-amber-400' : 'text-slate-400'}`} />
            <span>{isDegradedMode ? 'CAPACITY: REDUCED (FALLBACK)' : 'CAPACITY: OPTIMAL'}</span>
          </button>

          {/* Real-time zero egress badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-bold">OUTBOUND EGRESS: 0 B/s</span>
          </div>

          {/* Kill Switch Toggle */}
          <button
            onClick={toggleKillSwitch}
            className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded border transition-all text-xs font-semibold ${
              killSwitchActive
                ? 'bg-red-600/90 text-white border-red-400 shadow-lg glow-red'
                : 'bg-industrial-800 hover:bg-industrial-700 text-slate-300 border-industrial-600'
            }`}
            title="Simulates venue network cable unplug to prove complete offline autonomy"
          >
            <Power className="w-3.5 h-3.5" />
            <span>{killSwitchActive ? 'KILL-SWITCH: DISCONNECTED' : 'KILL-SWITCH'}</span>
          </button>
        </div>
      </div>

      {/* DEGRADED-MODE INDICATOR BANNER (Requirement 6: Visible but not distracting) */}
      {isDegradedMode && (
        <div className="bg-gradient-to-r from-amber-950/90 via-industrial-900 to-amber-950/90 border-b border-amber-500/40 px-4 py-1.5 flex items-center justify-between text-xs font-mono text-amber-300 shadow-inner">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 animate-pulse" />
            <span>
              <strong>Running in reduced-capacity mode:</strong> Venue fallback tier engaged (Qwen2.5-14B 4-bit / CPU inference). Core agentic workflows & sovereignty proofs remain fully operational.
            </span>
          </div>

          <button
            onClick={toggleDegradedMode}
            className="text-[10px] px-2 py-0.5 rounded bg-amber-900/60 hover:bg-amber-800 text-amber-200 border border-amber-700 font-bold transition shrink-0 ml-3"
          >
            Restore Full Capacity
          </button>
        </div>
      )}

      {/* Main Bar */}
      <div className="px-4 py-2.5 flex flex-wrap items-center justify-between gap-4">
        {/* Logo / Title */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500/20 via-industrial-800 to-emerald-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-md">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm md:text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
                Sovereign Agentic AI Workbench
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-700">
                  MRPL Airgap
                </span>
              </h1>
            </div>
            <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <span>P5 Knowledge Base & Frontend</span>
              <span>•</span>
              <span>Multi-Model Router</span>
              <span>•</span>
              <span>Human Approval Gate</span>
              <span>•</span>
              <span>Zero-Leak Telemetry</span>
            </p>
          </div>
        </div>

        {/* Quick Demo Scenario Selector & Execution Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-slate-400 hidden sm:inline">Scenario:</label>
            <select
              value={activeScenario.id}
              onChange={(e) => selectScenario(e.target.value)}
              className="bg-industrial-800 text-slate-200 border border-industrial-600 rounded px-2.5 py-1.5 text-xs focus:ring-1 focus:ring-cyan-400 outline-none max-w-[260px] sm:max-w-xs font-mono"
            >
              {DEMO_SCENARIOS.map((s) => (
                <option key={s.id} value={s.id}>
                  #{s.number}: {s.title}
                </option>
              ))}
            </select>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={runCurrentScenario}
              disabled={isRunning}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-semibold shadow transition-all ${
                isRunning
                  ? 'bg-industrial-700 text-slate-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white glow-cyan'
              }`}
            >
              <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
              <span>{isRunning ? `Step ${currentStepIndex}/${activeScenario.steps.length}...` : 'Run Scenario'}</span>
            </button>

            <button
              onClick={resetScenario}
              className="p-1.5 rounded bg-industrial-800 hover:bg-industrial-700 text-slate-400 hover:text-slate-200 border border-industrial-700 text-xs"
              title="Reset Scenario"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            {/* Approval Gate Quick Indicator */}
            {activeScenario.approvalRequired && (
              <button
                onClick={() => setApprovalGateOpen(true)}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 hover:bg-amber-500/25 animate-pulse-subtle"
                title="Open Human-in-the-Loop Approval Gate"
              >
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                <span>Approval Gate</span>
              </button>
            )}

            {/* Deliverable preview button */}
            {activeScenario.deliverable && (
              <button
                onClick={() => setDeliverableModalOpen(true)}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded text-xs font-semibold bg-cyan-950 text-cyan-300 border border-cyan-800 hover:bg-cyan-900"
                title="View Generated Industrial Deliverable (.docx/.xlsx)"
              >
                <FileCheck2 className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden md:inline">Deliverable</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
