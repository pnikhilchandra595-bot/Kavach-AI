"""
FastAPI Local Loopback Server for MRPL Knowledge Base & Vector Store (P5).
Binds to 127.0.0.1:8001 only (enforces airgap policy).
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .vector_store import LocalVectorStore
from .retriever import SovereignRetriever
from .ingest import run_ingestion

app = FastAPI(
    title="MRPL Sovereign Knowledge Base Service",
    description="Airgapped local RAG & vector retrieval service for SIH26117",
    version="2.0"
)

# Enable CORS for local Vite frontend on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global store and retriever instances
vector_store = LocalVectorStore()
vector_store.load()
retriever = SovereignRetriever(vector_store=vector_store)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    min_similarity: Optional[float] = 0.15

class QueryResponse(BaseModel):
    query: str
    total_hits: int
    execution_time_ms: float
    citations: List[Dict[str, Any]]

@app.get("/health")
def health_check():
    stats = vector_store.stats()
    return {
        "status": "ONLINE",
        "service": "MRPL Sovereign Local Vector Store (P5)",
        "network_posture": "AIRGAPPED (0 External Calls)",
        "binding": "127.0.0.1:8001 (Loopback Only)",
        "embedding_model": "On-Device Dense Vector Engine (384-dim)",
        "documents_indexed": stats["total_documents"],
        "chunks_indexed": stats["total_chunks"],
        "documents": stats["documents"]
    }

@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(req: QueryRequest):
    import time
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
def list_documents():
    stats = vector_store.stats()
    doc_details = []
    seen = set()
    for c in vector_store.chunks:
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
def get_document_content(doc_code: str):
    corpus_dir = os.path.join(os.path.dirname(__file__), "synthetic_corpus")
    target_code = doc_code.upper().strip()
    
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
def reingest():
    global vector_store, retriever
    vector_store = run_ingestion()
    retriever = SovereignRetriever(vector_store=vector_store)
    return {"status": "SUCCESS", "message": f"Re-indexed {len(vector_store.chunks)} chunks."}

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host=host, port=port, log_level="info")
