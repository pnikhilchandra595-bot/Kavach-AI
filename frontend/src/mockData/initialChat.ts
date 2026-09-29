import type { ChatMessage } from '../types';

export const INITIAL_CHAT_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-01',
    sender: 'user',
    content: 'Process the attached scanned UT thickness inspection report for Crude Distillation Column CRU-C-101. Verify against MRPL SOP limits, calculate remaining service life, and draft an official Inspection Approval Note for the Plant Operations Manager.',
    timestamp: '12:40:12 PM',
  },
  {
    id: 'msg-02',
    sender: 'assistant',
    modelUsed: 'Qwen2.5-32B-Instruct + Qwen2.5-VL-7B (100% On-Premise)',
    taskType: 'Multimodal Extraction & Regulatory Synthesis',
    status: 'completed',
    content: `I have completed the multimodal parsing of ultrasonic thickness inspection report **CRU_C101_UT_2026.pdf** and grounded the findings in **MRPL-SOP-CRU-402 Rev 4** and **API 510**.

### 🔍 Key Inspection Findings:
- **Top Shell (Tray 02):** 9.45 mm *(Coupling: 99%, High Confidence)*
- **Intermediate Shell (Tray 14):** **7.82 mm** *(Coupling: 74.3% — Flagged for Review)*
- **Bottom Sump Section:** 9.10 mm *(Coupling: 98%, High Confidence)*

### ⚙️ Calculations & Regulatory Compliance:
1. **Governing Retirement Thickness ($t_{min}$):** **6.20 mm** per ASME Section VIII Div 1 formula.
2. **Measured Corrosion Rate:** **0.222 mm/year** based on 9.8 years turnaround baseline.
3. **Remaining Useful Life (RUL):** **7.28 to 7.36 years** ($> 5.0\text{ year}$ safety minimum).

⚠️ **Mandatory Procedural Action per MRPL-SOP-CRU-402 Section 4.2:**
Because the measured residual thickness at Tray 14 (7.82 mm) has fallen below the **8.00 mm threshold**, the turnaround inspection cycle must be officially reduced from **36 months to 18 months**.`,
    timestamp: '12:40:18 PM',
    toolCalls: [
      { name: 'ocr_engine.py', status: 'completed', summary: 'Extracted 3 UT thickness points; Tray 14 flagged at 7.82mm' },
      { name: 'knowledge_search.py', status: 'completed', summary: 'Retrieved MRPL-SOP-CRU-402 Section 4.2 (Sim: 0.912)' },
      { name: 'code_sandbox.py', status: 'completed', summary: 'Computed RUL = 7.36 yrs, Corrosion Rate = 0.22 mm/yr' },
      { name: 'doc_generator.py', status: 'completed', summary: 'Drafted MRPL_Approval_Note_CRU_C101_2026.docx' }
    ],
    citations: [
      { document: 'MRPL-SOP-CRU-402 Rev 4', section: 'Section 4.2 (Intermediate Shell Thresholds)', similarity: 0.912 },
      { document: 'MRPL-STD-API-510', section: 'Section 1 (Remaining Life Formula)', similarity: 0.884 }
    ],
    requiresApproval: true,
    approvalAction: 'Formal filing of Inspection Approval Note with 18-month reduced turnaround cycle'
  }
];
