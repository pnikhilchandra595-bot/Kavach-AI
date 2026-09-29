import React, { useState } from 'react';
import { 
  ClipboardList, 
  CheckCircle2, 
  Clock, 
  Flame, 
  Play, 
  AlertCircle, 
  ShieldCheck, 
  Cpu, 
  FileText, 
  Eye, 
  Filter, 
  Search,
  ExternalLink
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';
import type { TaskItem } from '../../types';

export const TaskDashboard: React.FC = () => {
  const { 
    tasks, 
    setApprovalGateOpen, 
    setDeliverableModalOpen, 
    setActiveView, 
    selectScenario 
  } = useWorkbench();

  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTasks = tasks.filter(task => {
    const matchesFilter = filterStatus === 'ALL' || task.status === filterStatus;
    const matchesSearch = 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.operator.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.assignedModel.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const totalTasks = tasks.length;
  const runningTasks = tasks.filter(t => t.status === 'RUNNING').length;
  const pendingTasks = tasks.filter(t => t.status === 'PENDING_APPROVAL').length;
  const completedTasks = tasks.filter(t => t.status === 'COMPLETED' || t.status === 'NEUTRALIZED').length;

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border border-industrial-700 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <ClipboardList className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Refinery Operator Task Dashboard
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
                  AUTONOMOUS DISPATCH
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Track real-time agentic workflows, execution progress, safety classifications, and supervisor checkpoints
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveView('chat')}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition shadow glow-cyan"
            >
              <span>+ New Task Prompt</span>
            </button>
          </div>
        </div>

        {/* Quick KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800">
            <span className="text-[10px] uppercase font-mono text-slate-400 block">Total Workflows</span>
            <div className="text-xl font-bold font-mono text-slate-100 mt-1">{totalTasks}</div>
          </div>
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800">
            <span className="text-[10px] uppercase font-mono text-cyan-400 block">Running In Sandbox</span>
            <div className="text-xl font-bold font-mono text-cyan-300 mt-1">{runningTasks}</div>
          </div>
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800">
            <span className="text-[10px] uppercase font-mono text-amber-400 block">Pending Sign-off</span>
            <div className="text-xl font-bold font-mono text-amber-300 mt-1">{pendingTasks}</div>
          </div>
          <div className="bg-industrial-950 p-3 rounded-lg border border-industrial-800">
            <span className="text-[10px] uppercase font-mono text-emerald-400 block">Completed & Filed</span>
            <div className="text-xl font-bold font-mono text-emerald-300 mt-1">{completedTasks}</div>
          </div>
        </div>
      </div>

      {/* Filter & Search Strip */}
      <div className="glass-panel rounded-xl p-4 border border-industrial-700 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by task title, ID, operator or model..."
            className="w-full bg-industrial-950 border border-industrial-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono outline-none focus:ring-1 focus:ring-cyan-400"
          />
        </div>

        {/* Filter pills */}
        <div className="flex flex-wrap items-center gap-2">
          {[
            { id: 'ALL', label: 'All Tasks' },
            { id: 'PENDING_APPROVAL', label: 'Pending Approval' },
            { id: 'RUNNING', label: 'Running' },
            { id: 'COMPLETED', label: 'Completed' },
            { id: 'NEUTRALIZED', label: 'Threat Neutralized' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilterStatus(f.id)}
              className={`px-3 py-1 rounded text-xs font-mono transition ${
                filterStatus === f.id
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 font-bold'
                  : 'bg-industrial-800 text-slate-400 hover:text-slate-200 border border-industrial-700'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Task List Table / Cards */}
      <div className="space-y-4">
        {filteredTasks.map((task) => {
          const isPending = task.status === 'PENDING_APPROVAL';
          const isRunning = task.status === 'RUNNING';
          const isCompleted = task.status === 'COMPLETED';
          const isNeutralized = task.status === 'NEUTRALIZED';

          return (
            <div
              key={task.id}
              className={`glass-card rounded-xl p-5 border transition-all ${
                isPending
                  ? 'border-amber-500/60 bg-amber-950/15 shadow-lg glow-amber'
                  : isRunning
                  ? 'border-cyan-500/50 bg-cyan-950/15'
                  : 'border-industrial-700 bg-industrial-900/80 hover:border-industrial-600'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-industrial-800 pb-3">
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-bold text-cyan-400">{task.id}</span>
                    <span className="text-slate-500">•</span>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-industrial-950 text-slate-300 border border-industrial-800">
                      {task.category}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${
                      task.safetyLevel === 'CRITICAL'
                        ? 'bg-red-950 text-red-300 border-red-800'
                        : task.safetyLevel === 'HIGH'
                        ? 'bg-amber-950 text-amber-300 border-amber-800'
                        : 'bg-blue-950 text-blue-300 border-blue-800'
                    }`}>
                      {task.safetyLevel} SAFETY
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-100 mt-1">
                    {task.title}
                  </h3>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${
                    isPending
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 animate-pulse'
                      : isRunning
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50'
                      : isNeutralized
                      ? 'bg-purple-950 text-purple-300 border-purple-800'
                      : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                  }`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {/* Summary description */}
              <p className="text-xs text-slate-300 mt-3 leading-relaxed">
                {task.summary}
              </p>

              {/* Progress bar */}
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Execution Progress</span>
                  <span>{task.progress}%</span>
                </div>
                <div className="w-full bg-industrial-950 h-2 rounded-full overflow-hidden border border-industrial-800">
                  <div
                    style={{ width: `${task.progress}%` }}
                    className={`h-full transition-all duration-300 ${
                      isPending
                        ? 'bg-amber-500'
                        : isCompleted
                        ? 'bg-emerald-500'
                        : 'bg-cyan-500'
                    }`}
                  />
                </div>
              </div>

              {/* Metadata Footer */}
              <div className="mt-4 pt-3 border-t border-industrial-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
                <div className="flex items-center gap-4 text-[11px]">
                  <span>Model: <strong className="text-slate-200">{task.assignedModel}</strong></span>
                  <span>Operator: <strong className="text-slate-200">{task.operator}</strong></span>
                  <span>Started: <strong className="text-slate-200">{task.startTime}</strong></span>
                  {task.duration && <span>Duration: <strong className="text-cyan-400">{task.duration}</strong></span>}
                </div>

                {/* Quick Actions */}
                <div className="flex items-center gap-2">
                  {isPending && (
                    <button
                      onClick={() => setApprovalGateOpen(true)}
                      className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs rounded-lg transition shadow glow-amber flex items-center gap-1.5"
                    >
                      <Flame className="w-3.5 h-3.5" />
                      <span>Review Approval Gate</span>
                    </button>
                  )}

                  {task.deliverableName && (
                    <button
                      onClick={() => setDeliverableModalOpen(true)}
                      className="px-3 py-1.5 bg-industrial-800 hover:bg-industrial-700 text-cyan-300 border border-industrial-600 font-semibold text-xs rounded-lg transition flex items-center gap-1.5"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>{task.deliverableName.split('.').pop()?.toUpperCase()} Deliverable</span>
                    </button>
                  )}

                  {task.associatedScenarioId && (
                    <button
                      onClick={() => {
                        selectScenario(task.associatedScenarioId!);
                        setActiveView('agent');
                      }}
                      className="px-3 py-1.5 bg-industrial-800 hover:bg-industrial-700 text-slate-200 border border-industrial-700 font-medium text-xs rounded-lg transition flex items-center gap-1.5"
                    >
                      <span>Inspect ReAct Trajectory</span>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                    </button>
                  )}
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
