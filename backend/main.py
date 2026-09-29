"""
Kavach-AI Sovereign Backend API
FastAPI entrypoint serving:
- Health Checks & Airgap Telemetry
- Knowledge Base / Sovereign Local Vector Store & Retrieval (RAG)
- Model Router & Registry Engine
- ReAct Agent Core & Tool Execution
"""

import os
import sys
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure backend root is in python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from knowledge_base.vector_store import LocalVectorStore
from knowledge_base.retriever import SovereignRetriever
from knowledge_base.ingest import run_ingestion
from model_router.registry import ModelRegistry
from model_router.router import ModelRouter
from agent_core.planner import ReActPlanner

app = FastAPI(
    title="Kavach-AI Sovereign Backend API",
    description="Unified API server for Kavach-AI Sovereign Workbench (RAG, Model Router, Agent Core)",
    version="1.0.0"
)

# Enable CORS for local dev and cloud frontend deployments (Render, Vercel, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
vector_store = LocalVectorStore()
try:
    vector_store.load()
except Exception as e:
    print(f"Vector store initial load notice: {e}")

retriever = SovereignRetriever(vector_store=vector_store)
model_registry = ModelRegistry()
model_router = ModelRouter(registry=model_registry)


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    min_similarity: Optional[float] = 0.15


class QueryResponse(BaseModel):
    query: str
    total_hits: int
    execution_time_ms: float
    citations: List[Dict[str, Any]]


class RouteRequest(BaseModel):
    task: str


class PlanRequest(BaseModel):
    objective: str
    max_steps: Optional[int] = 5


@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "service": "Kavach-AI Sovereign Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    stats = vector_store.stats() if hasattr(vector_store, "stats") else {}
    return {
        "status": "ONLINE",
        "service": "Kavach-AI Sovereign Backend API",
        "network_posture": "AIRGAPPED_READY",
        "vector_store": {
            "documents_indexed": stats.get("total_documents", 0),
            "chunks_indexed": stats.get("total_chunks", 0),
        },
        "models_registered": len(model_registry.models) if hasattr(model_registry, "models") else 0
    }


# ==========================================
# Knowledge Base & RAG Endpoints
# ==========================================

@app.post("/query", response_model=QueryResponse)
@app.post("/api/kb/query", response_model=QueryResponse)
def query_knowledge_base(req: QueryRequest):
    start = time.time()
    min_sim = req.min_similarity if req.min_similarity is not None else 0.15
    citations = retriever.query(
        query_text=req.query,
        top_k=req.top_k or 3,
        min_similarity=min_sim
    )
    elapsed_ms = round((time.time() - start) * 1000, 2)
    return {
        "query": req.query,
        "total_hits": len(citations),
        "execution_time_ms": elapsed_ms,
        "citations": citations
    }


@app.get("/documents")
@app.get("/api/kb/documents")
def list_documents():
    stats = vector_store.stats() if hasattr(vector_store, "stats") else {}
    doc_details = []
    seen = set()
    for c in getattr(vector_store, "chunks", []):
        if c.document_code not in seen:
            seen.add(c.document_code)
            doc_details.append({
                "code": c.document_code,
                "title": c.document_title,
                "unit": c.refinery_unit,
                "revision": c.metadata.get("revision", "1.0"),
                "effective_date": c.metadata.get("effective_date", "2026-01-01"),
                "filename": c.metadata.get("filename", "")
            })
    return {
        "count": len(doc_details),
        "documents": sorted(doc_details, key=lambda x: x["code"])
    }


@app.get("/documents/{doc_code}")
@app.get("/api/kb/documents/{doc_code}")
def get_document_content(doc_code: str):
    corpus_dir = os.path.join(CURRENT_DIR, "knowledge_base", "synthetic_corpus")
    target_code = doc_code.upper().strip()
    
    if os.path.exists(corpus_dir):
        for fname in os.listdir(corpus_dir):
            if fname.startswith(target_code) and fname.endswith(".md"):
                with open(os.path.join(corpus_dir, fname), "r", encoding="utf-8") as f:
                    return {
                        "document_code": target_code,
                        "filename": fname,
                        "content": f.read()
                    }
                    
    raise HTTPException(status_code=404, detail=f"Document {doc_code} not found in synthetic corpus.")


@app.post("/reingest")
@app.post("/api/kb/reingest")
def reingest():
    global vector_store, retriever
    vector_store = run_ingestion()
    retriever = SovereignRetriever(vector_store=vector_store)
    return {"status": "SUCCESS", "message": f"Re-indexed {len(vector_store.chunks)} chunks."}


# ==========================================
# Model Router Endpoints
# ==========================================

@app.get("/api/models")
def list_models():
    models = []
    for model_id, meta in model_registry.models.items():
        models.append({
            "model_id": meta.id,
            "name": meta.name,
            "capabilities": meta.capabilities,
            "adapter_type": meta.adapter_type,
            "quantization": meta.quantization,
            "priority": meta.priority,
            "vram_required_gb": meta.vram_required_gb,
            "status": meta.status,
            "fallback_targets": meta.fallback_targets
        })
    return {"count": len(models), "models": models}


@app.post("/api/route")
def route_task(req: RouteRequest):
    decision = model_router.route(req.task)
    return {
        "task": req.task,
        "selected_model_id": decision.selected_model_id,
        "task_type": decision.task_type,
        "confidence": decision.confidence,
        "rationale": decision.rationale,
        "fallback_chain": decision.fallback_chain
    }


# ==========================================
# Agent Planner Endpoints
# ==========================================

@app.post("/api/agent/plan")
def create_plan(req: PlanRequest):
    planner = ReActPlanner(objective=req.objective, max_steps=req.max_steps or 5)
    plan = planner.generate_initial_plan()
    return {
        "objective": req.objective,
        "steps": plan
    }


if __name__ == "__main__":
    import uvicorn
    # Render and other cloud platforms provide PORT env var, and require binding to 0.0.0.0
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
