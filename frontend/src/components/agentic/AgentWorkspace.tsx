import React, { useState } from 'react';
import { 
  Play, 
  RotateCcw, 
  Bot, 
  Cpu, 
  Terminal, 
  FileText, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  BookOpen, 
  Flame, 
  Layers, 
  AlertCircle,
  Eye,
  FileCheck2
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';

export const AgentWorkspace: React.FC = () => {
  const {
    activeScenario,
    isRunning,
    currentStepIndex,
    runCurrentScenario,
    resetScenario,
    approvalGateOpen,
    setApprovalGateOpen,
    approvalActionTaken,
    setDeliverableModalOpen,
  } = useWorkbench();

  const [customPrompt, setCustomPrompt] = useState(activeScenario.inputPrompt);

  // Sync custom prompt when active scenario changes
  React.useEffect(() => {
    setCustomPrompt(activeScenario.inputPrompt);
  }, [activeScenario]);

  const maxSteps = 15;
  const currentStepCount = currentStepIndex > 0 ? Math.min(currentStepIndex, activeScenario.steps.length) : 0;
  const visibleSteps = activeScenario.steps.slice(0, currentStepIndex);

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Top Banner: Scenario Context & Prompt Input */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700/80 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-industrial-800 pb-3">
          <div className="flex items-center gap-2.5">
            <span className="w-7 h-7 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono font-bold text-xs">
              #{activeScenario.number}
            </span>
            <div>
              <h2 className="text-sm md:text-base font-bold text-slate-100 flex items-center gap-2">
                {activeScenario.title}
              </h2>
              <p className="text-xs text-slate-400">
                {activeScenario.category}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400">Airgap Guard:</span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] font-mono font-bold">
              ZERO-EGRESS STRICT
            </span>
          </div>
        </div>

        {/* Input prompt box */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              Agent Task Prompt & Objective
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              ReAct Plan-Execute-Iterate Engine
            </span>
          </label>

          <div className="relative">
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              rows={2}
              className="w-full bg-industrial-950/80 border border-industrial-700 rounded-lg p-3 text-slate-200 text-xs font-mono focus:ring-1 focus:ring-cyan-400 outline-none leading-relaxed"
            />
          </div>
        </div>

        {/* Controls Bar & Router Badge */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          {/* Router Decision Badge */}
          <div className="flex items-center gap-2 text-xs bg-industrial-950/60 px-3 py-1.5 rounded-lg border border-industrial-800">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Routed Model:</span>
            <strong className="text-cyan-300 font-mono">{activeScenario.routedModel}</strong>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
              {activeScenario.routingConfidence}% Match
            </span>
          </div>

          {/* Action Trigger */}
          <div className="flex items-center gap-2">
            <button
              onClick={runCurrentScenario}
              disabled={isRunning}
              className={`flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-bold transition shadow ${
                isRunning
                  ? 'bg-industrial-800 text-slate-400 cursor-not-allowed border border-industrial-700'
                  : 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white glow-cyan'
              }`}
            >
              <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
              <span>{isRunning ? `Executing Step ${currentStepCount}...` : 'Start ReAct Agent Loop'}</span>
            </button>

            <button
              onClick={resetScenario}
              className="px-3 py-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-300 border border-industrial-700 text-xs font-medium flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      {/* Telemetry Strip: Loop Detection, Iteration Cap, Token Usage */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="glass-card rounded-lg p-3 border border-industrial-700/60">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Agentic Iteration Cap</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-lg font-bold font-mono text-slate-100">
              {currentStepCount} <span className="text-xs text-slate-400 font-normal">/ {maxSteps} steps</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
              HEALTHY
            </span>
          </div>
        </div>

        <div className="glass-card rounded-lg p-3 border border-industrial-700/60">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Loop Detection Guard</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-lg font-bold font-mono text-emerald-400">0% Repeat</span>
            <span className="text-[10px] text-slate-400 font-mono">No Spin</span>
          </div>
        </div>

        <div className="glass-card rounded-lg p-3 border border-industrial-700/60">
          <div className="text-[10px] font-mono text-slate-400 uppercase">On-Prem Context Window</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-lg font-bold font-mono text-cyan-300">
              {currentStepIndex > 0 ? (currentStepIndex * 620 + 840).toLocaleString() : '840'}
              <span className="text-xs text-slate-400 font-normal"> / 32k</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">vLLM KV</span>
          </div>
        </div>

        <div className="glass-card rounded-lg p-3 border border-industrial-700/60">
          <div className="text-[10px] font-mono text-slate-400 uppercase">Human Approval Status</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className={`text-sm font-bold font-mono ${
              approvalActionTaken === 'APPROVED' 
                ? 'text-emerald-400' 
                : approvalActionTaken === 'REJECTED'
                ? 'text-red-400'
                : 'text-amber-400'
            }`}>
              {approvalActionTaken === 'APPROVED' 
                ? 'OPERATOR SIGNED' 
                : approvalActionTaken === 'REJECTED'
                ? 'TERMINATED'
                : activeScenario.approvalRequired ? 'GATE PENDING' : 'NOT REQUIRED'}
            </span>
            {activeScenario.approvalRequired && (
              <button 
                onClick={() => setApprovalGateOpen(true)}
                className="text-[10px] underline text-amber-300 hover:text-amber-200"
              >
                Inspect
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Prominent Approval Gate Trigger Banner (if step reached or gate pending) */}
      {activeScenario.approvalRequired && currentStepIndex >= 4 && approvalActionTaken === 'NONE' && (
        <div className="bg-amber-500/10 border-2 border-amber-500/60 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-lg glow-amber animate-pulse-subtle">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/40">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-amber-300 tracking-wide">
                ATTENTION: AGENT PAUSED AT HUMAN-IN-THE-LOOP APPROVAL GATE
              </h3>
              <p className="text-xs text-slate-300">
                Action: {activeScenario.approvalDetails?.actionTitle}. Refinery protocol requires explicit supervisor confirmation.
              </p>
            </div>
          </div>

          <button
            onClick={() => setApprovalGateOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs shadow-lg transition"
          >
            <span>Review & Authorize Action</span>
          </button>
        </div>
      )}

      {/* Deliverable Available Banner */}
      {activeScenario.deliverable && (approvalActionTaken === 'APPROVED' || !activeScenario.approvalRequired) && currentStepIndex >= activeScenario.steps.length && (
        <div className="bg-emerald-950/40 border border-emerald-500/40 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-lg glow-emerald">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
              <FileCheck2 className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-emerald-300 tracking-wide">
                DELIVERABLE ARTIFACT READY: {activeScenario.deliverable.name}
              </h3>
              <p className="text-xs text-slate-300 font-mono">
                Official MRPL document generated locally via {activeScenario.deliverable.type.toUpperCase()} template with zero cloud transmission.
              </p>
            </div>
          </div>

          <button
            onClick={() => setDeliverableModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow glow-cyan transition"
          >
            <Eye className="w-4 h-4" />
            <span>Open Deliverable Preview</span>
          </button>
        </div>
      )}

      {/* Main ReAct Execution Timeline */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            ReAct Step-by-Step Execution Trajectory
          </h3>

          <span className="text-xs text-slate-400 font-mono">
            {currentStepIndex === 0 
              ? 'Ready to execute' 
              : `Showing ${visibleSteps.length} of ${activeScenario.steps.length} steps`}
          </span>
        </div>

        {currentStepIndex === 0 ? (
          <div className="text-center py-12 border border-dashed border-industrial-800 rounded-xl bg-industrial-950/40 space-y-3">
            <Bot className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-slate-400 text-xs">
              Click <strong className="text-cyan-400">"Start ReAct Agent Loop"</strong> above to observe the multi-step plan, tool dispatches, local models, and regulatory approval checkpoint.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {visibleSteps.map((step, idx) => {
              const isApprovalStep = step.phase === 'paused_approval';
              const isBlocked = step.status === 'blocked';
              const isFlagged = step.status === 'flagged';

              return (
                <div
                  key={step.id}
                  className={`glass-card rounded-xl p-4 border transition-all duration-300 animate-in fade-in slide-in-from-top-2 ${
                    isApprovalStep
                      ? 'border-amber-500/50 bg-amber-950/10'
                      : isBlocked
                      ? 'border-red-500/50 bg-red-950/10'
                      : isFlagged
                      ? 'border-amber-500/40 bg-industrial-900'
                      : 'border-industrial-700 bg-industrial-900/90'
                  }`}
                >
                  {/* Step Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-industrial-800 pb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-industrial-800 border border-industrial-600 text-slate-300 font-mono font-bold text-xs flex items-center justify-center">
                        {step.stepNumber}
                      </span>
                      <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${
                        step.phase === 'plan'
                          ? 'bg-blue-950 text-blue-300 border-blue-800'
                          : step.phase === 'act'
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                          : step.phase === 'observe'
                          ? 'bg-purple-950 text-purple-300 border-purple-800'
                          : step.phase === 'paused_approval'
                          ? 'bg-amber-950 text-amber-300 border-amber-800'
                          : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                      }`}>
                        PHASE: {step.phase.toUpperCase()}
                      </span>
                      {step.toolName && (
                        <span className="text-xs font-mono text-cyan-300 flex items-center gap-1">
                          <Terminal className="w-3.5 h-3.5 text-slate-400" />
                          {step.toolName}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                      {step.confidence && (
                        <span className={`px-2 py-0.5 rounded border ${
                          step.confidence > 95
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                            : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}>
                          Conf: {step.confidence}%
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {step.durationMs}ms
                      </span>
                    </div>
                  </div>

                  {/* Agent Thought */}
                  <div className="py-2.5">
                    <div className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">Agent Internal Reasoning</div>
                    <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                      {step.thought}
                    </p>
                  </div>

                  {/* Tool Input / Output Boxes */}
                  {(step.toolInput || step.toolOutput) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs font-mono">
                      {step.toolInput && (
                        <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800 space-y-1">
                          <div className="text-[10px] text-slate-400 flex items-center justify-between">
                            <span>TOOL INPUT ARGS</span>
                            <span className="text-slate-500">Airgap Sanitized</span>
                          </div>
                          <pre className="text-[11px] text-slate-300 overflow-x-auto whitespace-pre-wrap">
                            {typeof step.toolInput === 'string'
                              ? step.toolInput
                              : JSON.stringify(step.toolInput, null, 2)}
                          </pre>
                        </div>
                      )}

                      {step.toolOutput && (
                        <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800 space-y-1">
                          <div className="text-[10px] text-slate-400 flex items-center justify-between">
                            <span>TOOL EXECUTION OBSERVED</span>
                            <span className="text-emerald-400 font-bold">0 Egress</span>
                          </div>
                          <pre className="text-[11px] text-emerald-300/90 overflow-x-auto whitespace-pre-wrap">
                            {typeof step.toolOutput === 'string'
                              ? step.toolOutput
                              : JSON.stringify(step.toolOutput, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}

                  {/* RAG Grounding Citation */}
                  {step.citation && (
                    <div className="mt-3 p-2.5 rounded-lg bg-purple-950/20 border border-purple-800/40 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2 text-purple-300">
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>RAG Grounding: <strong>{step.citation.document}</strong> ({step.citation.section})</span>
                      </div>
                      <span className="text-[10px] text-purple-400">Cosine Sim: {step.citation.similarity}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
};
