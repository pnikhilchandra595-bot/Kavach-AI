import React, { createContext, useContext, useState, useEffect } from 'react';
import type { 
  ActiveView, 
  DemoScenario, 
  ModelInfo, 
  AuditLogEntry,
  TaskItem,
  ChatMessage
} from '../types';
import { DEMO_SCENARIOS } from '../mockData/demoScenarios';
import { INITIAL_MODELS } from '../mockData/modelRegistry';
import { INITIAL_AUDIT_LOGS } from '../mockData/auditLogs';
import { INITIAL_TASKS } from '../mockData/initialTasks';
import { INITIAL_CHAT_MESSAGES } from '../mockData/initialChat';

interface WorkbenchContextType {
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;
  activeScenario: DemoScenario;
  selectScenario: (scenarioId: string) => void;
  isRunning: boolean;
  currentStepIndex: number;
  runCurrentScenario: () => void;
  resetScenario: () => void;
  approvalGateOpen: boolean;
  setApprovalGateOpen: (open: boolean) => void;
  approvalActionTaken: 'NONE' | 'APPROVED' | 'MODIFIED' | 'REJECTED';
  handleApproval: (decision: 'APPROVED' | 'MODIFIED' | 'REJECTED') => void;
  deliverableModalOpen: boolean;
  setDeliverableModalOpen: (open: boolean) => void;
  killSwitchActive: boolean;
  toggleKillSwitch: () => void;
  fallbackSimulated: boolean;
  isDegradedMode: boolean;
  toggleDegradedMode: () => void;
  models: ModelInfo[];
  simulateModelCrash: (modelId: string) => void;
  restoreModel: (modelId: string) => void;
  auditLogs: AuditLogEntry[];
  addAuditLog: (entry: Partial<AuditLogEntry>) => void;
  tasks: TaskItem[];
  updateTaskStatus: (taskId: string, status: TaskItem['status'], progress?: number) => void;
  chatMessages: ChatMessage[];
  sendChatMessage: (content: string) => void;
  operatorRbac: {
    currentUser: string;
    currentRole: string;
    department: string;
    accessTier: string;
  };
  twoPersonApproval: {
    primarySigned: boolean;
    primarySigner?: string;
    secondarySigned: boolean;
    secondarySigner?: string;
  };
  signPrimaryApproval: (signerName: string) => void;
  signSecondaryApproval: (signerName: string) => void;
  networkStats: {
    egressBytesSec: 0;
    loopbackMBs: number;
    blockedExternalPackets: number;
    firewallPolicy: string;
    nicPhysicalStatus: string;
  };
}

const WorkbenchContext = createContext<WorkbenchContextType | undefined>(undefined);

export const WorkbenchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeView, setActiveView] = useState<ActiveView>('chat'); // Default to AI Workbench Chat
  const [activeScenario, setActiveScenario] = useState<DemoScenario>(DEMO_SCENARIOS[0]); // Scenario 2 by default
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [approvalGateOpen, setApprovalGateOpen] = useState<boolean>(false);
  const [approvalActionTaken, setApprovalActionTaken] = useState<'NONE' | 'APPROVED' | 'MODIFIED' | 'REJECTED'>('NONE');
  const [deliverableModalOpen, setDeliverableModalOpen] = useState<boolean>(false);
  const [killSwitchActive, setKillSwitchActive] = useState<boolean>(false);
  const [fallbackSimulated, setFallbackSimulated] = useState<boolean>(false);
  const [isDegradedMode, setIsDegradedMode] = useState<boolean>(false);
  const [models, setModels] = useState<ModelInfo[]>(INITIAL_MODELS);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>(INITIAL_AUDIT_LOGS);
  const [tasks, setTasks] = useState<TaskItem[]>(INITIAL_TASKS);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(INITIAL_CHAT_MESSAGES);

  // Two-Person Approval state for critical refinery documents
  const [twoPersonApproval, setTwoPersonApproval] = useState({
    primarySigned: true, // Signed by NDT Level II inspector
    primarySigner: 'M. Sharma (NDT Level II)',
    secondarySigned: false, // Pending Plant Operations Manager
    secondarySigner: undefined as string | undefined,
  });

  const operatorRbac = {
    currentUser: 'M. Sharma',
    currentRole: 'Chief Plant Inspector (Level III NDT)',
    department: 'CDU-II Technical Inspection',
    accessTier: 'OPERATOR_SUPERVISOR_SIGN',
  };

  const [networkStats, setNetworkStats] = useState({
    egressBytesSec: 0 as const,
    loopbackMBs: 14.6,
    blockedExternalPackets: 284,
    firewallPolicy: 'iptables -P OUTPUT DROP (ACTIVE)',
    nicPhysicalStatus: 'AIRGAP_CONNECTED_ISOLATED',
  });

  // Simulated live loopback variations (always 0 egress)
  useEffect(() => {
    const interval = setInterval(() => {
      setNetworkStats(prev => ({
        ...prev,
        loopbackMBs: Number((12.5 + Math.random() * 4.2).toFixed(1)),
        blockedExternalPackets: prev.blockedExternalPackets + (Math.random() > 0.6 ? 1 : 0),
      }));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const selectScenario = (scenarioId: string) => {
    const found = DEMO_SCENARIOS.find(s => s.id === scenarioId);
    if (found) {
      setActiveScenario(found);
      setCurrentStepIndex(0);
      setIsRunning(false);
      setApprovalGateOpen(false);
      setApprovalActionTaken('NONE');
    }
  };

  const addAuditLog = (entry: Partial<AuditLogEntry>) => {
    const idNum = auditLogs.length + 1041;
    const prevLog = auditLogs[auditLogs.length - 1];
    const prevHash = prevLog ? prevLog.sha256Hash : '0000000000000000000000000000000000000000000000000000000000000000';
    const randomHashSuffix = Math.random().toString(16).substring(2, 10);
    const newHash = `sha256:7f81a${idNum}${randomHashSuffix}e901bca${Date.now().toString(16)}`;

    const fullEntry: AuditLogEntry = {
      id: `LOG-00${idNum}`,
      timestamp: new Date().toISOString(),
      actor: entry.actor || operatorRbac.currentUser,
      modelUsed: entry.modelUsed || activeScenario.routedModel,
      eventType: entry.eventType || 'TOOL_CALL',
      actionDescription: entry.actionDescription || 'Executed agentic sub-action.',
      toolName: entry.toolName,
      egressBytes: 0,
      sha256Hash: newHash,
      prevHash: prevHash,
      status: entry.status || 'VERIFIED',
      taskId: entry.taskId || 'TSK-1042',
      userRole: operatorRbac.currentRole,
    };

    setAuditLogs(prev => [...prev, fullEntry]);
  };

  const updateTaskStatus = (taskId: string, status: TaskItem['status'], progress?: number) => {
    setTasks(prev =>
      prev.map(t =>
        t.id === taskId
          ? {
              ...t,
              status,
              progress: progress !== undefined ? progress : t.progress,
              endTime: status === 'COMPLETED' ? new Date().toLocaleTimeString() : t.endTime,
            }
          : t
      )
    );
  };

  const sendChatMessage = (content: string) => {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages(prev => [...prev, userMsg]);

    addAuditLog({
      eventType: 'TASK_INIT',
      actionDescription: `Operator prompted AI workbench: "${content.slice(0, 70)}..."`,
      modelUsed: activeScenario.routedModel,
    });

    // Simulated thinking assistant response
    setTimeout(() => {
      const isMath = content.toLowerCase().includes('asme') || content.toLowerCase().includes('thickness') || content.toLowerCase().includes('formula');
      const isDrawing = content.toLowerCase().includes('p&id') || content.toLowerCase().includes('valve') || content.toLowerCase().includes('dwg');
      
      const routedModel = isDrawing 
        ? 'Qwen2.5-VL-7B (Local VLM)' 
        : isMath 
        ? 'Qwen2.5-Coder-14B (Sandboxed Engine)' 
        : 'Qwen2.5-32B-Instruct (Orchestrator Core)';
      
      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'assistant',
        content: `I have analyzed your query within the local airgap boundary using **${routedModel}**.\n\n### Task Processing Summary:\n- Checked local vector index for relevant refinery specifications.\n- Executed verification checks with **0 external network calls**.\n- All calculations and parameters comply with MRPL engineering baselines.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        modelUsed: routedModel,
        taskType: isDrawing ? 'Multimodal Diagram Extraction' : isMath ? 'Isolated Code Execution' : 'Autonomous Reasoning',
        status: 'completed',
        citations: [
          { document: 'MRPL-SOP-CRU-402 Rev 4', section: 'Section 4: Minimum Retirement Thickness', similarity: 0.912 }
        ]
      };

      setChatMessages(prev => [...prev, assistantMsg]);
    }, 1200);
  };

  const runCurrentScenario = () => {
    setIsRunning(true);
    setCurrentStepIndex(1);
    setApprovalActionTaken('NONE');
    setApprovalGateOpen(false);

    updateTaskStatus('TSK-1042', 'RUNNING', 20);

    addAuditLog({
      eventType: 'TASK_INIT',
      actionDescription: `Triggered execution for Demo Scenario #${activeScenario.number}: ${activeScenario.title}`,
      modelUsed: activeScenario.routedModel,
    });

    let current = 1;
    const totalSteps = activeScenario.steps.length;

    const stepInterval = setInterval(() => {
      current += 1;
      if (current <= totalSteps) {
        setCurrentStepIndex(current);
        const step = activeScenario.steps[current - 1];

        updateTaskStatus('TSK-1042', step.phase === 'paused_approval' ? 'PENDING_APPROVAL' : 'RUNNING', Math.round((current / totalSteps) * 100));

        addAuditLog({
          eventType: step.phase === 'paused_approval' ? 'APPROVAL_REQUEST' : 'TOOL_CALL',
          toolName: step.toolName,
          actionDescription: `Step ${step.stepNumber}: ${step.thought.slice(0, 90)}...`,
          modelUsed: activeScenario.routedModel,
          status: step.phase === 'paused_approval' ? 'FLAGGED' : 'VERIFIED',
        });

        if (step.phase === 'paused_approval' && activeScenario.approvalRequired) {
          clearInterval(stepInterval);
          setIsRunning(false);
          setApprovalGateOpen(true);
        }
      } else {
        clearInterval(stepInterval);
        setIsRunning(false);
        updateTaskStatus('TSK-1042', 'COMPLETED', 100);
        if (activeScenario.deliverable && !activeScenario.approvalRequired) {
          setDeliverableModalOpen(true);
        }
      }
    }, 1800);
  };

  const resetScenario = () => {
    setIsRunning(false);
    setCurrentStepIndex(0);
    setApprovalGateOpen(false);
    setApprovalActionTaken('NONE');
  };

  const signPrimaryApproval = (signerName: string) => {
    setTwoPersonApproval(prev => ({
      ...prev,
      primarySigned: true,
      primarySigner: signerName,
    }));
    addAuditLog({
      actor: signerName,
      eventType: 'APPROVAL_REQUEST',
      actionDescription: `Primary sign-off executed by ${signerName}. Pending secondary supervisor countersignature.`,
      status: 'VERIFIED',
    });
  };

  const signSecondaryApproval = (signerName: string) => {
    setTwoPersonApproval(prev => ({
      ...prev,
      secondarySigned: true,
      secondarySigner: signerName,
    }));
    addAuditLog({
      actor: signerName,
      eventType: 'APPROVAL_GRANTED',
      actionDescription: `Secondary sign-off executed by ${signerName}. Two-person rule SATISFIED. Action authorized.`,
      status: 'RESOLVED',
    });
  };

  const handleApproval = (decision: 'APPROVED' | 'MODIFIED' | 'REJECTED') => {
    setApprovalActionTaken(decision);
    setApprovalGateOpen(false);

    if (decision === 'APPROVED') {
      signSecondaryApproval('Plant Operations Manager (MRPL-OP-882)');
      updateTaskStatus('TSK-1042', 'COMPLETED', 100);

      // Complete next step if available
      setCurrentStepIndex(activeScenario.steps.length);
      setTimeout(() => {
        setDeliverableModalOpen(true);
      }, 500);
    } else if (decision === 'REJECTED') {
      updateTaskStatus('TSK-1042', 'FAILED');
      addAuditLog({
        actor: operatorRbac.currentUser,
        eventType: 'APPROVAL_REJECTED',
        actionDescription: `Supervisor REJECTED action for ${activeScenario.approvalDetails?.affectedResource}. Execution terminated cleanly.`,
        status: 'FLAGGED',
      });
    }
  };

  const toggleKillSwitch = () => {
    const nextState = !killSwitchActive;
    setKillSwitchActive(nextState);
    setNetworkStats(prev => ({
      ...prev,
      nicPhysicalStatus: nextState ? 'KILL_SWITCH_ENGAGED_HARDWARE_PULLED' : 'AIRGAP_CONNECTED_ISOLATED',
    }));

    addAuditLog({
      actor: 'security_lead_P6',
      eventType: 'AIRGAP_PROVE',
      actionDescription: nextState
        ? 'KILL-SWITCH ENGAGED: Hardware ethernet interface disabled. All external sockets dropped. Zero interruption in local model serving.'
        : 'Kill-switch disengaged: System returned to nominal airgap monitoring posture.',
      modelUsed: 'Physical NIC Monitor Daemon',
      status: 'VERIFIED',
    });
  };

  const toggleDegradedMode = () => {
    const nextState = !isDegradedMode;
    setIsDegradedMode(nextState);

    addAuditLog({
      actor: 'system_monitor_P2',
      eventType: 'ROUTER_FALLBACK',
      actionDescription: nextState
        ? 'Reduced-Capacity Degraded Mode engaged: Operating on minimum venue fallback tier (Qwen2.5-14B 4-bit / CPU inference).'
        : 'Restored optimal hardware capacity profile (NVIDIA RTX 4090 24GB VRAM).',
      status: nextState ? 'FLAGGED' : 'RESOLVED',
    });
  };

  const simulateModelCrash = (modelId: string) => {
    setFallbackSimulated(true);
    setIsDegradedMode(true);
    setModels(prev =>
      prev.map(m =>
        m.id === modelId
          ? { ...m, status: 'CRASHED_SIMULATED', vramUsageGb: 0 }
          : m.id === 'qwen-32b-reasoning'
          ? { ...m, vramUsageGb: m.vramUsageGb + 4.2 }
          : m
      )
    );

    addAuditLog({
      actor: 'model_infrastructure_P2',
      eventType: 'ROUTER_FALLBACK',
      actionDescription: `Model ${modelId} crashed (Simulated Out of Memory). Fallback Policy activated: Traffic rerouted to Qwen2.5-32B-Instruct.`,
      modelUsed: 'Router Fallback Handler',
      status: 'FLAGGED',
    });
  };

  const restoreModel = (modelId: string) => {
    setFallbackSimulated(false);
    setIsDegradedMode(false);
    setModels(INITIAL_MODELS);

    addAuditLog({
      actor: 'model_infrastructure_P2',
      eventType: 'TASK_INIT',
      actionDescription: `Model ${modelId} restarted and warm-loaded. Model weights restored in 4-bit VRAM.`,
      modelUsed: 'Inference Adapter Manager',
      status: 'VERIFIED',
    });
  };

  return (
    <WorkbenchContext.Provider
      value={{
        activeView,
        setActiveView,
        activeScenario,
        selectScenario,
        isRunning,
        currentStepIndex,
        runCurrentScenario,
        resetScenario,
        approvalGateOpen,
        setApprovalGateOpen,
        approvalActionTaken,
        handleApproval,
        deliverableModalOpen,
        setDeliverableModalOpen,
        killSwitchActive,
        toggleKillSwitch,
        fallbackSimulated,
        isDegradedMode,
        toggleDegradedMode,
        models,
        simulateModelCrash,
        restoreModel,
        auditLogs,
        addAuditLog,
        tasks,
        updateTaskStatus,
        chatMessages,
        sendChatMessage,
        operatorRbac,
        twoPersonApproval,
        signPrimaryApproval,
        signSecondaryApproval,
        networkStats,
      }}
    >
      {children}
    </WorkbenchContext.Provider>
  );
};

export const useWorkbench = () => {
  const context = useContext(WorkbenchContext);
  if (!context) {
    throw new Error('useWorkbench must be used within a WorkbenchProvider');
  }
  return context;
};
