# SIH26117 — Task Assignment (P1–P6)
### Derived from Implementation Plan v2

**Sponsor:** Mangalore Refinery and Petrochemicals Limited (MRPL) | **Theme:** Smart Automation

---

## P1 — Agent Architecture Lead (Team Lead)
- Plan-execute (ReAct-style) agentic loop, multi-step reasoning, iteration logic
- Model router design + model registry architecture
- Iteration cap and loop-detection logic
- Owns the fallback-policy design decision (in collaboration with P2)
- Owns the judge narrative: "why this architecture scales to new models"

## P2 — Model Infrastructure Engineer
- Local model serving setup (vLLM/Ollama), quantization for GPU-constrained deployment
- Model adapter implementations per model type (coding, reasoning, vision)
- Fallback path implementation — kill/restart a model, verify router recovers cleanly
- Benchmarking model-selection accuracy across task types (feeds P6's eval harness)

## P3 — Multimodal & OCR Engineer
- On-device OCR pipeline (PaddleOCR/Tesseract)
- Local VLM integration for P&ID/drawing/handwriting understanding
- Scanned-document ingestion pipeline (PDF → OCR → structured text)
- Confidence-flagging for low-certainty extractions, surfaced in the UI

## P4 — Tools & Sandbox Engineer
- Code sandbox (Docker/firejail isolation, no network access)
- File I/O and spreadsheet manipulation tools
- Document/deliverable generation (python-docx/pptx/openpyxl), including letterhead/signature-block templates
- Guardrails module: path restrictions, destructive-action screening, wiring into the approval gate

## P5 — Knowledge Base & Frontend Engineer
- Local vector store + embedding pipeline (Chroma/Qdrant, local embeddings)
- Synthetic SOP/manual/correspondence corpus creation + ingestion/retrieval
- Frontend build: chat interface, task dashboard, network-traffic monitor UI, approval-gate UI, audit-log viewer

## P6 — Network Security & Presentation Lead
- Network isolation enforcement (firewall rules, deny-all-outbound) + kill-switch demo mechanism
- Traffic-monitoring dashboard backend (proof-of-sovereignty logging)
- Audit log design (tamper-evident, append-only)
- Eval harness scripts: router accuracy, OCR error rate, scripted end-to-end replay
- Demo script, PPT, judge Q&A prep, risk register ownership, deployment/GPU docs

---

## Cross-Cutting Dependencies (flag at kickoff)

| Dependency | Owners | Needed by |
|---|---|---|
| Fallback-policy contract agreed | P1 → P2 | Weeks 1–2 |
| Approval-gate UI hook available | P5 → P4 | Weeks 7–8 |
| Stable router/OCR interfaces for eval harness | P2, P3 → P6 | Week 9 |
