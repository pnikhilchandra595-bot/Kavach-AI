import React from 'react';
import { WorkbenchProvider, useWorkbench } from './context/WorkbenchContext';
import { Header } from './components/layout/Header';
import { Navigation } from './components/layout/Navigation';
import { ChatInterface } from './components/chat/ChatInterface';
import { TaskDashboard } from './components/tasks/TaskDashboard';
import { AgentWorkspace } from './components/agentic/AgentWorkspace';
import { ApprovalGateModal } from './components/agentic/ApprovalGateModal';
import { DeliverableModal } from './components/agentic/DeliverableModal';
import { TrafficMonitor } from './components/sovereignty/TrafficMonitor';
import { ModelRouterView } from './components/router/ModelRouterView';
import { MultimodalView } from './components/multimodal/MultimodalView';
import { KnowledgeBaseView } from './components/knowledge/KnowledgeBaseView';
import { AuditLogView } from './components/audit/AuditLogView';
import { EvalHarnessView } from './components/eval/EvalHarnessView';
import { GuardrailsView } from './components/guardrails/GuardrailsView';

const MainContent: React.FC = () => {
  const { activeView } = useWorkbench();

  return (
    <main className="flex-1 pb-16">
      {activeView === 'chat' && <ChatInterface />}
      {activeView === 'tasks' && <TaskDashboard />}
      {activeView === 'agent' && <AgentWorkspace />}
      {activeView === 'traffic' && <TrafficMonitor />}
      {activeView === 'router' && <ModelRouterView />}
      {activeView === 'multimodal' && <MultimodalView />}
      {activeView === 'knowledge' && <KnowledgeBaseView />}
      {activeView === 'audit' && <AuditLogView />}
      {activeView === 'eval' && <EvalHarnessView />}
      {activeView === 'guardrails' && <GuardrailsView />}

      {/* Global Modals */}
      <ApprovalGateModal />
      <DeliverableModal />
    </main>
  );
};

export function App() {
  return (
    <WorkbenchProvider>
      <div className="min-h-screen bg-industrial-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
        {/* Navigation & Header */}
        <Header />
        <Navigation />

        {/* Dynamic Main Views */}
        <MainContent />

        {/* Industrial Footer */}
        <footer className="mt-auto border-t border-industrial-800 bg-industrial-950 px-6 py-3.5 text-xs font-mono text-slate-500 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Mangalore Refinery and Petrochemicals Limited (MRPL) • SIH26117 Smart Automation</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span>Airgapped Host: 127.0.0.1</span>
            <span>•</span>
            <span className="text-cyan-400">Zero Cloud APIs</span>
            <span>•</span>
            <span className="text-emerald-400 font-bold">P5 Knowledge Base & Frontend</span>
          </div>
        </footer>
      </div>
    </WorkbenchProvider>
  );
}

export default App;
