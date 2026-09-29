# SIH26117 — Sovereign On-Premise Agentic AI Workbench
**Sponsor**: Mangalore Refinery and Petrochemicals Limited (MRPL) | **Theme**: Smart Automation  
**Core Proof Point**: Everything runs air-gapped, on-prem, multi-model, agentic, multimodal — with verifiable zero outbound connections.

---

## 1. System Architecture

```
sovereign-workbench/
├── model_router/
│   ├── router.py              # task classifier → model selection
│   ├── model_registry.yaml    # pluggable model configs, versioned with rollback support
│   ├── registry_manager.py    # hardware tier detection, snapshots, and version rollback
│   ├── provenance.py          # load-time cryptographic checksum & tamper rejection
│   ├── fallback_policy.py     # OOM / crash detection, automatic tiered failover, audit logs
│   ├── cascade.py             # [Stretch] draft-model → escalate-to-large-model optimization
│   └── adapters/              # per-model inference adapters (vLLM/Ollama/llama.cpp/Mock)
├── agent_core/
│   ├── planner.py             # multi-step task planning (ReAct/plan-execute loop)
│   ├── tool_executor.py       # dispatches to local tools, schema-constrained tool calls
│   ├── memory.py              # task state, scratchpad, iteration history
│   ├── approval_gate.py       # human-in-the-loop checkpoint, RBAC-aware
│   └── guardrails.py          # input/output validation, prompt-injection screening
├── tools/
│   ├── file_io.py              # read/write local files
│   ├── code_sandbox.py         # isolated code execution (Docker/firejail)
│   ├── spreadsheet.py          # openpyxl-based Excel manipulation
│   ├── doc_generator.py        # Word/PPT/Excel output generation
│   └── knowledge_search.py     # local RAG over SOPs/manuals/correspondence
├── multimodal/
│   ├── ocr_engine.py           # on-device OCR (Tesseract/PaddleOCR)
│   ├── vision_model.py         # local VLM for P&ID/drawing/handwriting understanding
│   └── document_ingest.py       # scanned PDF → structured text pipeline
├── knowledge_base/
│   ├── ingest.py               # SOP/manual ingestion, sensitivity tagging
│   ├── vector_store/           # local embedding store (Chroma/Qdrant, self-hosted)
│   └── drift_check.py          # flags stale chunks against newer source documents
├── network_isolation/
│   ├── firewall_rules.sh       # deny-all-outbound enforcement
│   └── traffic_monitor.py      # live proof-of-sovereignty dashboard
├── observability/
│   ├── audit_log.py            # append-only, tamper-evident action log
│   ├── metrics.py              # latency, throughput, router accuracy, SLA breach flags
│   └── eval_harness/
│       ├── router_eval.py      # labeled task set → measures routing accuracy
│       └── load_test.py        # [Stretch] concurrent-task latency/throughput profiling
└── tests/                      # automated unit and integration test suite
```

---

## 2. Role P2: Model Infrastructure Engineer

This repository implements the complete **P2 (Model Infrastructure Engineer)** tier of SIH26117:

### A. Local Inference Adapters (`model_router/adapters/`)
- **`BaseModelAdapter`**: Uniform abstract contract for completions, schema-constrained function/tool calling, vision/multimodal inference, token accounting, and liveness probing.
- **`VLLMAdapter`**: Local OpenAI-compatible REST adapter for high-throughput vLLM model serving.
- **`OllamaAdapter`**: Local REST adapter for quantized GGUF models.
- **`LlamaCppAdapter`**: GGUF server adapter with CPU offloading for edge nodes with constrained VRAM.
- **`MockAdapter`**: Deterministic air-gapped simulation adapter with realistic MRPL refinery domain context (P&ID diagram tag inspection `10-P-101A/B`, SCADA vibration anomaly script generation, Sulfur Recovery Unit SOP lookup) and fault-injection hooks (OOM, Process Crash, Latency) for offline testing and judge demonstrations.

### B. Versioned Model Registry with Rollback (`model_router/registry_manager.py`)
- Declarative `model_registry.yaml` covering 4 hardware tiers:
  - **Degraded**: 4GB VRAM (e.g. Laptop RTX 3050) — forces 4-bit quantized minimal models.
  - **Minimum**: 8–12GB VRAM — runs 14B Q4 / 7B unquantized.
  - **Recommended**: 16–24GB VRAM — runs 32B AWQ / 14B models.
  - **Stretch**: 48GB+ VRAM — 72B flagship models.
- Hardware auto-detection: checks available GPU VRAM and sets `reduced_capacity_mode = True` when VRAM < 8GB.
- Version history ledger with instant rollback (`rollback_to_version()`).

### C. Cryptographic Model Provenance (`model_router/provenance.py`)
- Streaming SHA-256 / SHA-512 model weight checksum verification at load time.
- Enforces Zero-Trust policy: immediately raises `TamperedModelWeightError` and refuses execution if weights are modified.

### D. Resilient Fallback Policy Engine (`model_router/fallback_policy.py`)
- Automatic failover upon model crash, endpoint timeout, or CUDA Out-Of-Memory (OOM).
- Cascades requests down an ordered, task-appropriate chain (e.g. 14B -> 1.5B -> 7B).
- Precisely tracks two distinct latency metrics:
  - **Failover Decision Time** (0.015 ms – 0.12 ms): Circuit-breaker detection, tier filtering, and fallback dispatch.
  - **Total Recovery + Generation Time**: Cold start (~4,413 ms including weight loading) vs. Warm resident (286 ms – 725 ms).
- Emits immutable audit log events recording original model, failed model, failover model, timestamp, and root cause (Demo Scenario 6).

### E. Master Benchmark & Failover Performance Matrix

| Task Type | Primary Model | Fallback Target | Failover Trigger | Trigger Mode | Failover Decision Time | Total Recovery + Gen (Cold) | Total Recovery + Gen (Warm) | Runtime Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Coding** | `qwen2.5-coder-14b` | `qwen2.5-coder:1.5b` | Process Kill / Crash | Programmatic Fault Injection | **0.015 – 0.020 ms** | 4,413 ms (VRAM load + gen) | **286 – 725 ms** | ✅ Verified Live on RTX 3050 |
| **Coding** | `qwen2.5-coder-14b` | `qwen2.5-coder:1.5b` | CUDA OutOfMemory (OOM) | Programmatic Fault Injection | **0.120 ms** | 4,413 ms | **1,028 ms** | ✅ Verified Live on RTX 3050 |
| **Coding** | `qwen2.5-coder-14b` | `qwen2.5-coder:1.5b` | Missing/Unloaded Model | Live Runtime HTTP Probe (404) | **33.200 ms** (HTTP RTT) | 4,413 ms | **769 ms** | ✅ Verified Live on RTX 3050 |
| **Planning** | `qwen2.5-32b-awq` | `qwen2.5-7b-q4` | Process Kill (SIGKILL) | Programmatic Fault Injection | **0.025 ms** | N/A (Simulated tier) | **50.36 ms** | ✅ Verified (Scenario 6) |

> **Audit Transparency Note**: The OOM test was verified via *Programmatic Fault Injection* (raising `OutOfMemoryError` representing GPU allocation exhaustion to validate circuit-breaker behavior) rather than physically crashing hardware. Real endpoint failures were tested via unpulled models (HTTP 404), and live inference was executed on the NVIDIA RTX 3050 Laptop GPU.

### F. Speculative Model Cascading (`model_router/cascade.py`) [Stretch]
- Submits prompts first to a fast 7B/1.5B draft model (~65% GPU compute saved).
- Escalates directly to the 32B/72B flagship model upon safety-critical triggers (e.g. emergency shutdown interlocks, stoichiometric ratio calculations) or low confidence.

### G. Observability & Eval Harness (`observability/eval_harness/`)
- **`router_eval.py`**: Benchmarking task classification and routing accuracy across 5 refinery operational categories (100% accuracy, 0.009 ms routing latency).
- **`load_test.py`**: Concurrent multi-operator load profiling measuring P50/P95/P99 latency, throughput, and SLA budget compliance.

---

## 3. Quick Start & Verification

### Prerequisites
Python 3.10+ (Standard library only; optional `pyyaml` for YAML parsing).

### Run Automated Unit Tests (100% Pass Rate)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Live Judge-Defense Demonstration
```bash
python run_p2_demo.py
```

### Run Router Benchmark & Load Profiler
```bash
python observability/eval_harness/router_eval.py
python observability/eval_harness/load_test.py
```
