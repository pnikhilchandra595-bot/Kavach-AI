import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Terminal, 
  Sparkles, 
  Cpu, 
  CheckCircle2, 
  Clock, 
  Paperclip, 
  Flame, 
  BookOpen, 
  Eye, 
  Layers, 
  AlertTriangle,
  RotateCcw
} from 'lucide-react';
import { useWorkbench } from '../../context/WorkbenchContext';

export const ChatInterface: React.FC = () => {
  const {
    chatMessages,
    sendChatMessage,
    activeScenario,
    setApprovalGateOpen,
    setDeliverableModalOpen,
    isDegradedMode,
    operatorRbac
  } = useWorkbench();

  const [inputVal, setInputVal] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    sendChatMessage(inputVal);
    setInputVal('');
  };

  const quickPrompts = [
    'Calculate ASME Section VIII Div 1 shell thickness for P = 2.5 MPa, R = 1200 mm, S = 138 MPa, E = 0.85',
    'Verify P&ID Line 34B relief valve tags and twin 100% redundancy against MRPL standard',
    'What is the mandatory atmospheric LEL and H2S limit for issuing a Class-A hot work permit?',
    'Evaluate Column CRU-C-101 UT thickness scan findings and calculate remaining service life'
  ];

  return (
    <div className="p-4 md:p-6 space-y-4 max-w-7xl mx-auto flex flex-col h-[calc(100vh-140px)]">
      
      {/* Top Banner: Chat Session Telemetry */}
      <div className="glass-panel rounded-xl px-5 py-3 border border-industrial-700 flex flex-wrap items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center shadow">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-100">
                Sovereign Agentic AI Chat Workbench
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono font-bold">
                AIRGAPPED SESSION
              </span>
              {isDegradedMode && (
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-mono animate-pulse">
                  REDUCED-CAPACITY
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Operator: {operatorRbac.currentUser} ({operatorRbac.currentRole}) • Ready for Backend API
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400 hidden sm:inline">Active Model:</span>
          <span className="px-2.5 py-1 rounded bg-industrial-950 text-cyan-300 border border-industrial-800 font-semibold">
            {activeScenario.routedModel.split('+')[0]}
          </span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 glass-card rounded-xl p-4 md:p-6 border border-industrial-700/70 overflow-y-auto space-y-6 scrollbar-thin">
        {chatMessages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center shrink-0 mt-1 shadow">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-2xl space-y-3 ${isUser ? 'items-end' : 'items-start'}`}>
                
                {/* Message Header */}
                <div className={`flex items-center gap-2 text-[11px] font-mono ${isUser ? 'justify-end text-slate-400' : 'text-slate-400'}`}>
                  <span className="font-semibold text-slate-300">
                    {isUser ? operatorRbac.currentUser : 'Sovereign Agent Core'}
                  </span>
                  <span>•</span>
                  <span>{msg.timestamp}</span>
                  {msg.modelUsed && (
                    <>
                      <span>•</span>
                      <span className="text-cyan-400 font-bold">{msg.modelUsed}</span>
                    </>
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed shadow-md ${
                    isUser
                      ? 'bg-gradient-to-r from-cyan-700 to-emerald-700 text-white rounded-tr-none'
                      : 'bg-industrial-900 border border-industrial-700/80 text-slate-200 rounded-tl-none space-y-3'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans text-xs space-y-2">
                    {msg.content}
                  </div>

                  {/* Tool Invocations Accordion / Badges */}
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="pt-3 border-t border-industrial-800 space-y-1.5 font-mono text-[11px]">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block flex items-center gap-1">
                        <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                        Airgapped Tool Dispatches ({msg.toolCalls.length}):
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                        {msg.toolCalls.map((tc, idx) => (
                          <div
                            key={idx}
                            className="bg-industrial-950 p-2 rounded border border-industrial-800 flex items-center justify-between"
                          >
                            <span className="text-cyan-300 truncate max-w-[150px]">{tc.name}</span>
                            <span className="text-emerald-400 text-[9px] font-bold uppercase">
                              {tc.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* RAG Grounding Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 border-t border-industrial-800 space-y-1 font-mono text-[11px]">
                      <span className="text-[10px] uppercase font-bold text-purple-400 block flex items-center gap-1">
                        <BookOpen className="w-3.5 h-3.5" />
                        Grounded Sources ({msg.citations.length}):
                      </span>
                      {msg.citations.map((c, idx) => (
                        <div key={idx} className="text-purple-300 text-[10px] bg-purple-950/30 p-1.5 rounded border border-purple-800/40 flex items-center justify-between">
                          <span>{c.document} — {c.section}</span>
                          <span className="text-purple-400">Sim: {c.similarity}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Human Approval Callout */}
                  {msg.requiresApproval && (
                    <div className="mt-3 bg-amber-500/15 border border-amber-500/40 rounded-lg p-2.5 flex items-center justify-between gap-3 text-xs text-amber-300 font-mono">
                      <div className="flex items-center gap-2">
                        <Flame className="w-4 h-4 text-amber-400 shrink-0" />
                        <span className="text-[11px]">
                          <strong>Action Held at Approval Gate:</strong> {msg.approvalAction}
                        </span>
                      </div>
                      <button
                        onClick={() => setApprovalGateOpen(true)}
                        className="px-3 py-1 bg-amber-500 hover:bg-amber-400 text-black font-bold text-[10px] rounded transition shadow shrink-0"
                      >
                        Inspect & Sign
                      </button>
                    </div>
                  )}
                </div>

              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-lg bg-emerald-900/80 text-emerald-300 border border-emerald-700 flex items-center justify-center shrink-0 mt-1 shadow">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Strip */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-[11px] font-mono">
        <span className="text-slate-400 shrink-0">Preset Queries:</span>
        {quickPrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => setInputVal(p)}
            className="px-2.5 py-1 bg-industrial-900 hover:bg-industrial-800 text-slate-300 rounded border border-industrial-700 whitespace-nowrap transition text-[11px]"
          >
            {p.slice(0, 42)}...
          </button>
        ))}
      </div>

      {/* Chat Input Bar */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Type task prompt or ask about refinery SOPs, ASME calculations, or P&ID schematics..."
            className="w-full bg-industrial-900 border border-industrial-700 rounded-xl py-3 pl-4 pr-24 text-xs font-mono text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-cyan-400 outline-none shadow-lg"
          />

          <div className="absolute right-2 flex items-center gap-1.5">
            <button
              type="submit"
              disabled={!inputVal.trim()}
              className={`p-2 rounded-lg transition ${
                inputVal.trim()
                  ? 'bg-gradient-to-r from-cyan-600 to-emerald-600 text-white shadow glow-cyan'
                  : 'bg-industrial-800 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </form>

    </div>
  );
};
