import React from 'react';
import { 
  MessageSquare,
  ClipboardList,
  Bot, 
  Activity, 
  GitFork, 
  Eye, 
  BookOpen, 
  FileText, 
  TestTube2, 
  ShieldAlert 
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';
import type { ActiveView } from '../../types';

export const Navigation: React.FC = () => {
  const { activeView, setActiveView, fallbackSimulated, approvalActionTaken, tasks } = useWorkbench();
  const pendingCount = tasks.filter(t => t.status === 'PENDING_APPROVAL').length;

  const navItems: Array<{
    id: ActiveView;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string;
    badgeColor?: string;
  }> = [
    {
      id: 'chat',
      label: 'AI Workbench Chat',
      icon: MessageSquare,
      badge: 'Interactive',
      badgeColor: 'bg-cyan-950 text-cyan-300 border-cyan-700',
    },
    {
      id: 'tasks',
      label: 'Task Dashboard',
      icon: ClipboardList,
      badge: pendingCount > 0 ? `${pendingCount} Pending` : `${tasks.length} Tasks`,
      badgeColor: pendingCount > 0 ? 'bg-amber-950 text-amber-300 border-amber-700 animate-pulse' : 'bg-industrial-800 text-slate-300 border-industrial-700',
    },
    {
      id: 'agent',
      label: 'ReAct Trajectory',
      icon: Bot,
      badge: approvalActionTaken === 'APPROVED' ? 'Signed' : undefined,
      badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-700',
    },
    {
      id: 'traffic',
      label: 'Airgap Network Monitor',
      icon: Activity,
      badge: '0 Egress',
      badgeColor: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    },
    {
      id: 'router',
      label: 'Model Router & Fleet',
      icon: GitFork,
      badge: fallbackSimulated ? 'Fallback Active' : '4 Models',
      badgeColor: fallbackSimulated ? 'bg-amber-950 text-amber-300 border-amber-700 animate-pulse' : 'bg-industrial-800 text-slate-300 border-industrial-700',
    },
    {
      id: 'multimodal',
      label: 'Multimodal OCR & P&ID',
      icon: Eye,
    },
    {
      id: 'knowledge',
      label: 'Refinery SOP RAG',
      icon: BookOpen,
      badge: '12 SOPs',
      badgeColor: 'bg-purple-950 text-purple-300 border-purple-800',
    },
    {
      id: 'audit',
      label: 'Tamper-Evident Audit Log',
      icon: FileText,
      badge: 'SHA-256 Chained',
      badgeColor: 'bg-cyan-950 text-cyan-400 border-cyan-800',
    },
    {
      id: 'eval',
      label: 'Pre-Demo Eval Harness',
      icon: TestTube2,
      badge: '100% Pass',
      badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-700',
    },
    {
      id: 'guardrails',
      label: 'Guardrails & Injection',
      icon: ShieldAlert,
    },
  ];

  return (
    <nav className="bg-industrial-900 border-b border-industrial-800 px-4">
      <div className="flex items-center space-x-1 overflow-x-auto py-2 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-industrial-800/60 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono ${item.badgeColor || 'bg-industrial-800 text-slate-300 border-industrial-700'}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
