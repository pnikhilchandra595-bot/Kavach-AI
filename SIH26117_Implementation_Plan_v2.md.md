# SIH26117 — Sovereign On-Premise Agentic AI Workbench
## Full Implementation Plan (2-Month Build) — v2 (Expanded)

**Sponsor:** Mangalore Refinery and Petrochemicals Limited (MRPL) | **Theme:** Smart Automation
**Core proof point:** everything runs air-gapped, on-prem, multi-model, agentic, multimodal — and you can *prove* no external calls happen.

---

## 1. System Architecture

```
sovereign-workbench/
├── model_router/
│   ├── router.py              # task classifier → model selection
│   ├── model_registry.yaml    # pluggable model configs (add new models here)
│   ├── fallback_policy.py     # NEW: what happens when the preferred model is unavailable/OOM
│   └── adapters/               # per-model inference adapters (vLLM/Ollama/llama.cpp)
├── agent_core/
│   ├── planner.py              # multi-step task planning (ReAct/plan-execute loop)
│   ├── tool_executor.py        # dispatches to local tools
│   ├── memory.py               # task state, scratchpad, iteration history
│   ├── approval_gate.py        # NEW: human-in-the-loop checkpoint before irreversible actions
│   └── guardrails.py           # NEW: input/output validation, prompt-injection screening
├── tools/
│   ├── file_io.py               # read/write local files
│   ├── code_sandbox.py          # isolated code execution (Docker/firejail)
│   ├── spreadsheet.py           # openpyxl-based Excel manipulation
│   ├── doc_generator.py         # Word/PPT/Excel output generation
│   └── knowledge_search.py      # local RAG over SOPs/manuals/correspondence
├── multimodal/
│   ├── ocr_engine.py             # on-device OCR (Tesseract/PaddleOCR/local vision model)
│   ├── vision_model.py           # local VLM for P&ID/drawing/handwriting understanding
│   └── document_ingest.py        # scanned PDF → structured text pipeline
├── knowledge_base/
│   ├── ingest.py                 # SOP/manual/correspondence ingestion
│   ├── vector_store/             # local embedding store (Chroma/Qdrant, self-hosted)
│   └── retriever.py
├── network_isolation/
│   ├── firewall_rules.sh         # deny-all-outbound enforcement
│   └── traffic_monitor.py        # live proof-of-sovereignty dashboard
├── observability/                 # NEW
│   ├── audit_log.py               # append-only, tamper-evident action log (every tool call, every file write)
│   ├── metrics.py                 # latency, token throughput, router accuracy, failure rates
│   └── eval_harness/              # scripted test suite run before every demo
│       ├── router_eval.py         # labeled task set → measures routing accuracy
│       ├── ocr_eval.py            # scanned doc ground truth → CER/WER
│       └── e2e_eval.py            # scripted end-to-end scenario runner
├── frontend/
│   └── src/                      # chat + task dashboard + traffic monitor UI + approval-gate UI
└── deployment/
    ├── docker-compose.yml
    ├── gpu_requirements.md
    └── backup_restore.md          # NEW: model weights, vector store, config snapshot/restore
```

---

## 2. Core Components, In Detail

### A. Multi-Model Router (the "not locked to one model" requirement)
- **Approach:** A lightweight classifier (rule-based first, upgradeable to a small fine-tuned router model) inspects incoming task type — coding, document summarization, vision/OCR, multi-step planning — and routes to the best-fit local model.
- **Model registry design:** each model entry in `model_registry.yaml` declares its strengths (`code`, `reasoning`, `vision`, `summarization`), context window, and adapter type — so adding a new open-weight model later is a config change, not a redesign.
- **Suggested starting models (swap for smaller variants if venue GPU is limited):**
  - Reasoning/planning: Qwen2.5-72B or a smaller Qwen2.5-32B/14B
  - Coding: Qwen2.5-Coder or DeepSeek-Coder
  - Vision/multimodal: Qwen2.5-VL or LLaVA-based model for P&ID/drawing/handwriting
  - Serving: vLLM or Ollama for local inference, with quantization (4-bit/8-bit via bitsandbytes) to fit consumer/mid-range GPUs
- **NEW — Fallback policy:** if the preferred model for a task type is unavailable (OOM, crashed, still loading), the router falls back to the next-best available model rather than failing the task outright. Log every fallback event — it's a good judge-facing resilience story ("the system degrades gracefully, it doesn't just break").
- **NEW — Router confidence threshold:** if the classifier's confidence in task type is below a threshold, ask a single clarifying question or route to the general reasoning model rather than guessing — avoids silently misrouting a coding task to the vision model.

### B. Agentic Core (plan → act → iterate, not one-shot chat)
- **Approach:** A plan-execute loop (ReAct-style) — the agent breaks a task into steps, calls tools, observes results, and revises the plan rather than stopping after one response.
- **Tool interface:** each tool (file I/O, code sandbox, spreadsheet, knowledge search, doc generation) exposes a simple function-call schema the router model can invoke.
- **Sandboxed code execution:** run generated code in a Docker container or `firejail` with no network access and resource limits — this is both a technical requirement and part of your sovereignty story (code execution that could theoretically exfiltrate data must also be air-gapped).
- **NEW — Iteration cap and loop detection:** cap the plan-execute loop at N steps (e.g., 15) and detect repeated identical tool calls, so a confused agent fails loudly and visibly instead of spinning silently — much better for a live demo than an infinite loop.
- **NEW — Human-in-the-loop approval gate:** for any action with real-world consequence in a refinery context — e.g., drafting a document that will be filed, overwriting an existing file, or anything framed as an "approval note" — the agent pauses and shows the proposed action in the UI for explicit operator confirmation before executing. This is both a genuine safety requirement for an industrial setting and a strong differentiator from "just an autonomous agent that does whatever it wants."

### C. Multimodal Pipeline
- **On-device OCR:** PaddleOCR or Tesseract for scanned documents/handwritten notes — no cloud OCR APIs.
- **Vision understanding:** a local VLM (Qwen2.5-VL or similar) for interpreting P&ID diagrams, engineering drawings, and photographs — extract key findings, annotations, and structured data from images.
- **Document ingestion pipeline:** scanned PDF → OCR → structured text → fed into the agent's working context.
- **NEW — Confidence-flagged extraction:** OCR/VLM output includes per-field confidence; low-confidence extractions are visually flagged in the UI rather than silently presented as fact — important for anything that feeds an approval note in a refinery setting.

### D. Deliverable Generation (real files, not just chat replies)
- **Stack:** `python-docx` (Word), `python-pptx` (PowerPoint), `openpyxl` (Excel).
- **Approach:** the agent's final output step always produces an actual file artifact — an approval note as a `.docx`, calculations with shown steps in an Excel sheet, not a chat transcript.
- **NEW — Template-driven generation:** use pre-built `.docx`/`.pptx` templates matching a plausible refinery document style (letterhead placeholder, approval signature block) rather than generic formatting — makes the demo artifact look like something that could actually be filed.

### E. Local Knowledge Base (grounding in SOPs/manuals/correspondence)
- **Stack:** self-hosted vector store (Chroma or Qdrant, both runnable fully offline) + a local embedding model (e.g., `bge-large` or `nomic-embed-text` run locally, not via API).
- **Approach:** ingest sample SOPs/manuals/correspondence (public/synthetic for demo, since real MRPL documents aren't available to you), chunk and embed locally, retrieve relevant context for agent grounding.
- **NEW — Synthetic data plan:** since real MRPL SOPs aren't available, generate a small synthetic corpus (10–20 documents) styled as refinery SOPs/inspection reports/correspondence, clearly labeled as synthetic in the demo narrative ("for this demo we use representative synthetic SOPs; in production this ingests MRPL's actual document repository"). This avoids any implication that real proprietary MRPL data was used without authorization.
- **NEW — Citation in retrieval:** every RAG-grounded answer cites which source document/chunk it drew from, shown in the UI — makes hallucination visibly checkable by judges.

### F. Sovereignty Proof (the actual differentiator)
- **Approach:** this is explicitly called out in the PS as "the actual proof of the sovereign claim, not just a statement of it" — build this as a first-class feature, not an afterthought.
- **Implementation:** a live network traffic monitor (e.g., using `psutil`/`scapy` to watch outbound connections) displayed in the UI during the demo, plus firewall rules (`iptables`/deny-all-outbound) enforced at the OS level so it's not just monitored but actually blocked.
- **Demo moment:** show the dashboard with zero outbound connections throughout an entire end-to-end task — this single visual is your strongest judge-facing proof point.
- **NEW — Kill-switch test:** as part of the demo, briefly unplug/disable the venue's network connection entirely and show the system continuing to work unaffected — a more visceral proof than a dashboard reading zero.

### G. Observability & Audit Trail — NEW SECTION
- **Approach:** every tool call, model invocation, and file write is logged to an append-only audit log (`observability/audit_log.py`) with timestamp, actor (which model/agent step), and action — this is standard practice for any system operating in a regulated industrial environment and directly supports the "trustworthy automation" framing.
- **Metrics dashboard:** router accuracy over time, per-task latency, tool call success/failure rate — gives judges a second, quantitative proof surface beyond the live demo.
- **Eval harness:** a small scripted test suite (`observability/eval_harness/`) run before every demo/rehearsal to catch regressions — router accuracy on a labeled task set, OCR character/word error rate on a labeled scanned-doc set, and a scripted end-to-end scenario runner that replays the demo path headlessly. This turns "trust us, it works" into a repeatable, re-runnable check.

### H. Guardrails & Prompt-Injection Defense — NEW SECTION
- **Why it matters here specifically:** this system ingests untrusted content (scanned documents, OCR'd handwriting, retrieved SOP text) directly into an agent that can execute code and write files — that's exactly the shape of pipeline where injected instructions hidden in a document ("ignore previous instructions and...") could hijack the agent.
- **Approach:**
  - Treat all OCR/RAG-retrieved content as **data**, not as instructions — pass it to the model clearly demarcated (e.g., inside tagged blocks) with an explicit system-level instruction that content inside those tags is untrusted input to reason about, not commands to follow.
  - The `guardrails.py` module screens tool-call arguments before execution (e.g., a file-write tool refuses paths outside the designated workspace directory; the code sandbox has no network access regardless of what code is generated).
  - Any tool call that would overwrite an existing file or execute a destructive operation routes through the human-in-the-loop approval gate (Section B) regardless of how the agent arrived at that decision.
- **Demo moment (optional, high-impact):** feed a scanned document containing a hidden injected instruction and show the agent correctly ignoring it while still extracting the legitimate content — a strong, concrete trust demonstration for judges familiar with LLM security.

---

## 3. Demo Scenarios (map directly to "Expected Solution")

1. **Model auto-selection across ≥2 task types** — show the router picking a coding model for a code task and a reasoning/vision model for a document task, live, with the routing decision visible in logs.
2. **End-to-end agentic task** — scanned inspection report → OCR/vision extraction → key findings pulled out → approval note drafted as a real `.docx` file, paused at the human-in-the-loop gate for operator sign-off.
3. **Coding task, run and verified in sandbox** — agent writes code, executes it in the isolated sandbox, shows verified output.
4. **Multimodal task** — image or scanned document understanding (e.g., reading a P&ID diagram and answering a question about it).
5. **Sovereignty proof** — network monitor showing zero external calls throughout all of the above, plus the kill-switch moment.
6. **NEW — Graceful failure & recovery** — deliberately trigger a fallback (kill the preferred model process mid-task) and show the router failing over to a backup model with the event visible in the audit log, rather than the whole system crashing. This demo scenario is often what separates "a demo that only works on the happy path" from a system judges believe is real engineering.
7. **NEW — Guardrail demonstration** — the prompt-injection-in-a-scanned-document scenario from Section H, if time allows; strong differentiator, optional if the team is time-constrained.

---

## 4. Team Task Division (P1–P6), 2-Month Timeline

### P1 — Agent Architecture Lead (Team Lead)
- Agentic core: plan-execute loop, multi-step reasoning, iteration logic
- Model router design and model registry architecture
- Iteration cap / loop detection, fallback policy
- Owns the "why this architecture scales to new models" narrative for judges

### P2 — Model Infrastructure Engineer
- Local model serving (vLLM/Ollama setup), quantization for GPU-constrained deployment
- Model adapter implementations per model type (coding, reasoning, vision)
- Benchmarking model selection accuracy across task types
- Fallback path implementation and testing (kill/restart a model, verify router recovers)

### P3 — Multimodal & OCR Engineer
- On-device OCR pipeline (PaddleOCR/Tesseract)
- Local vision model integration for P&ID/drawing/handwriting understanding
- Scanned-document ingestion pipeline
- Confidence-flagging for low-certainty extractions

### P4 — Tools & Sandbox Engineer
- Code sandbox (Docker/firejail isolation)
- File I/O, spreadsheet manipulation tools
- Document/deliverable generation (Word/PPT/Excel via python-docx/pptx/openpyxl)
- Guardrails module: path restrictions, destructive-action screening, approval-gate wiring

### P5 — Knowledge Base & Frontend Engineer
- Local vector store + embedding pipeline (Chroma/Qdrant, local embeddings)
- SOP/manual/correspondence ingestion and retrieval, synthetic corpus creation
- Frontend: chat interface, task dashboard, live network-traffic monitor UI, approval-gate UI, audit-log viewer

### P6 — Network Security & Presentation Lead
- Network isolation enforcement (firewall rules, deny-all-outbound)
- Traffic monitoring dashboard backend (proof-of-sovereignty logging)
- Audit log design (tamper-evident append-only log)
- Eval harness scripts (router accuracy, OCR error rate, scripted end-to-end runner)
- Demo script, PPT, judge Q&A prep, deployment/GPU setup documentation, risk register ownership

---

## 5. Two-Month Milestone Timeline

| Phase | Weeks | Focus |
|---|---|---|
| Architecture & setup | 1–2 | Model registry design, GPU/serving infra, repo scaffold, tool interface spec, synthetic data generation started |
| Core build | 3–6 | Agent loop, model router, tools (sandbox, file I/O, doc gen), OCR/vision pipeline, iteration cap + fallback policy |
| Knowledge base + guardrails | 7–8 | Local RAG, knowledge base ingestion, guardrails module, approval-gate UI, wiring agent to tools end-to-end |
| Network isolation + sovereignty proof | 9 | Firewall enforcement, traffic monitor, audit log, verify zero-leak across all demo paths |
| Eval harness + observability | 9–10 | Router/OCR eval scripts, metrics dashboard, run eval suite and fix regressions before polish |
| Demo scenarios + polish | 10–11 | Build and rehearse all 6–7 demo scenarios, frontend polish, PPT |
| Final rehearsal + hardening | 12 | Full dry-run, edge-case testing, backup offline demo, deployment docs, buffer for the inevitable last-minute GPU driver issue |

---

## 6. Judge-Defense Cheat Sheet

| Question | Answer from this build |
|---|---|
| How do we know nothing leaves the premises? | Live network traffic monitor showing zero outbound calls during the full demo, enforced by OS-level firewall rules, not just claimed — plus a literal kill-switch moment |
| Why not just use one strong model? | Task-type routing benchmarks showing coding vs. reasoning vs. vision models perform differently per task |
| How does this scale to new models? | Model registry config-based design — adding a model is a YAML entry, not a redesign |
| Is this really agentic, or just chat? | End-to-end demo: scanned report → extraction → drafted approval note as a real file, multi-step, paused at a human approval gate, not single-turn |
| What about hardware constraints at the venue? | Quantized smaller model fallback path (documented), same architecture scales up or down |
| Is generated code safe to run? | Sandboxed execution (Docker/firejail) with no network access, resource-limited |
| NEW: What happens if a model crashes mid-task? | Router failover to a backup model, logged in the audit trail — demoed live as a deliberate failure scenario |
| NEW: How do you stop a hidden instruction in a scanned document from hijacking the agent? | Untrusted content is passed as clearly demarcated data, not instructions; destructive/irreversible tool calls always route through the human approval gate regardless |
| NEW: How do you know the router/OCR actually work, not just in this one demo run? | Scripted eval harness with labeled test sets (router accuracy, OCR error rate) re-run before every rehearsal — numbers, not vibes |
| NEW: What data did you train/ground this on, given MRPL's real documents aren't available? | Explicitly synthetic SOP/inspection-report corpus, clearly labeled as representative rather than real MRPL data |

---

## 7. Risk Register — NEW SECTION

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Venue GPU is smaller/older than expected | Medium | High | Quantized fallback models pre-tested and documented; rehearse on the smallest plausible hardware, not just the dev machine |
| Live demo network/model failure | Medium | High | Scripted offline backup demo (pre-recorded run-through or headless eval-harness replay) as a fallback if live demo breaks |
| OCR/VLM misreads handwriting badly in front of judges | Medium | Medium | Confidence-flagging shown in UI turns a misread into "the system correctly flagged uncertainty" rather than a silent failure |
| Agent loops or hangs mid-demo | Low–Medium | High | Iteration cap + loop detection (Section B) turns a hang into a visible, explainable failure state |
| Team runs out of time before all 6–7 demo scenarios are polished | Medium | Medium | Prioritize scenarios 1–5 (core PS requirements) as must-have; scenarios 6–7 are stretch goals, cut first if behind schedule |
| Judges question whether "sovereignty" is really proven vs. just claimed | Low | High | Kill-switch demo moment + audit log + firewall enforcement (not just monitoring) directly pre-empts this |

---

## 8. Hardware Sizing Guide — NEW SECTION

| Tier | GPU | Models | Notes |
|---|---|---|---|
| Minimum (venue fallback) | 8–12GB VRAM (e.g., RTX 3060/4060) | Qwen2.5-14B (4-bit), Qwen2.5-Coder-7B, small VLM | Slower but fully functional; this is the tier to rehearse on at least once |
| Recommended (dev/demo) | 16–24GB VRAM (e.g., RTX 4090, A10) | Qwen2.5-32B (4-bit/8-bit), Qwen2.5-Coder-14B+, Qwen2.5-VL-7B | Comfortable headroom for the full demo script |
| Stretch | 48GB+ (e.g., A100) | Qwen2.5-72B, larger coder/VL variants | Only if available — don't design the judge-facing story around hardware the team can't guarantee at the venue |

---

## 9. Stretch Goals (if ahead of schedule)

- Fine-tune a small dedicated router classifier on a labeled task-type dataset instead of relying purely on rule-based/prompt-based routing, and show the accuracy improvement as a metric.
- Add a second language (e.g., Hindi/Kannada handwriting OCR) to the multimodal pipeline, relevant to a Mangalore-based refinery's actual correspondence mix.
- Extend the audit log into a simple tamper-evidence check (hash-chaining log entries) — a small addition that meaningfully strengthens the "provable" part of the sovereignty claim.
