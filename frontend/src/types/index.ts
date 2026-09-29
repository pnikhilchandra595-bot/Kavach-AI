export type ActiveView = 
  | 'chat'
  | 'tasks'
  | 'agent'
  | 'traffic'
  | 'router'
  | 'multimodal'
  | 'knowledge'
  | 'audit'
  | 'eval'
  | 'guardrails';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  modelUsed?: string;
  taskType?: string;
  status?: 'sending' | 'thinking' | 'streaming' | 'completed' | 'error';
  toolCalls?: Array<{
    name: string;
    status: 'running' | 'completed' | 'blocked';
    summary: string;
  }>;
  citations?: Array<{
    document: string;
    section: string;
    similarity: number;
  }>;
  requiresApproval?: boolean;
  approvalAction?: string;
}

export interface TaskItem {
  id: string;
  title: string;
  category: string;
  status: 'QUEUED' | 'RUNNING' | 'PENDING_APPROVAL' | 'COMPLETED' | 'FAILED' | 'NEUTRALIZED';
  progress: number; // 0 to 100
  assignedModel: string;
  operator: string;
  startTime: string;
  endTime?: string;
  duration?: string;
  safetyLevel: 'CRITICAL' | 'HIGH' | 'STANDARD';
  deliverableName?: string;
  associatedScenarioId?: string;
  summary: string;
}

export interface AgentStep {
  id: string;
  stepNumber: number;
  phase: 'plan' | 'act' | 'observe' | 'iterate' | 'complete' | 'paused_approval';
  thought: string;
  toolName?: string;
  toolInput?: Record<string, any> | string;
  toolOutput?: Record<string, any> | string;
  status: 'pending' | 'running' | 'completed' | 'flagged' | 'blocked';
  durationMs: number;
  confidence?: number;
  citation?: {
    document: string;
    section: string;
    similarity: number;
  };
}

export interface ApprovalDetails {
  actionTitle: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  affectedResource: string;
  targetPath: string;
  diffSummary: string;
  safetyHash: string;
  justification: string;
  operatorRequiredRole: string;
  twoPersonRequired?: boolean;
  primaryApprover?: {
    name: string;
    role: string;
    signed: boolean;
    timestamp?: string;
  };
  secondaryApprover?: {
    name: string;
    role: string;
    signed: boolean;
    timestamp?: string;
  };
  operatorRbac?: {
    currentUser: string;
    currentRole: string;
    canSignPrimary: boolean;
    canSignSecondary: boolean;
  };
}

export interface DeliverableFile {
  name: string;
  type: 'docx' | 'xlsx' | 'pptx' | 'pdf';
  title: string;
  size: string;
  sha256: string;
  metadata: {
    refineryUnit: string;
    preparedBy: string;
    approvedBy: string;
    standard: string;
    date: string;
  };
  tableData?: Array<Record<string, string | number>>;
  executiveSummary: string;
}

export interface DemoScenario {
  id: string;
  number: number;
  title: string;
  category: string;
  description: string;
  inputPrompt: string;
  routedModel: string;
  routingReason: string;
  routingConfidence: number;
  steps: AgentStep[];
  deliverable?: DeliverableFile;
  approvalRequired?: boolean;
  approvalDetails?: ApprovalDetails;
  isFallbackDemo?: boolean;
  isGuardrailDemo?: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  role: string;
  primaryTasks: string[];
  quantization: string;
  adapter: 'vLLM' | 'Ollama' | 'llama.cpp' | 'Torch (Airgapped)';
  vramUsageGb: number;
  allocatedVramGb: number;
  contextWindow: string;
  status: 'READY' | 'ACTIVE' | 'STANDBY' | 'CRASHED_SIMULATED';
  accuracyRate: number;
  isFallbackFor?: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  actor: string;
  modelUsed: string;
  eventType: 
    | 'TASK_INIT'
    | 'TOOL_CALL'
    | 'APPROVAL_REQUEST'
    | 'APPROVAL_GRANTED'
    | 'APPROVAL_REJECTED'
    | 'FILE_WRITE'
    | 'ROUTER_FALLBACK'
    | 'GUARDRAIL_INTERCEPTION'
    | 'AIRGAP_PROVE';
  actionDescription: string;
  toolName?: string;
  egressBytes: 0;
  sha256Hash: string;
  prevHash: string;
  status: 'VERIFIED' | 'FLAGGED' | 'RESOLVED';
  taskId?: string;
  userRole?: string;
}

export interface SOPDocument {
  id: string;
  code: string;
  title: string;
  category: 'SOP' | 'Inspection Code' | 'Hazardous Permit' | 'Equipment Manual';
  unit: string;
  updatedAt: string;
  chunksCount: number;
  summary: string;
  sensitivity?: 'INTERNAL CONFIDENTIAL' | 'PROCESS SAFETY CRITICAL' | 'STANDARD OPERATING' | 'RESTRICTED';
  driftStatus?: 'CURRENT' | 'DRIFT_WARNING' | 'SUPERSEDED';
  staleWarning?: string;
  sampleChunks: Array<{
    id: string;
    section: string;
    content: string;
    relevanceTag?: string;
  }>;
}

export interface OCRFieldExtraction {
  id: string;
  field: string;
  rawText: string;
  normalizedValue: string;
  confidence: number;
  status: 'high_confidence' | 'flagged_review' | 'manual_override';
  location: { x: number; y: number; width: number; height: number };
}

export interface EvalBenchmarkResult {
  suiteId: string;
  suiteName: string;
  testsCount: number;
  passedCount: number;
  score: string;
  executionTime: string;
  status: 'PASSED' | 'WARNING' | 'FAILED';
  details: Array<{
    name: string;
    metric: string;
    expected: string;
    actual: string;
    passed: boolean;
  }>;
}
