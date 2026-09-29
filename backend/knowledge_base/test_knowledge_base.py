"""
Unit and Integration Tests for MRPL Knowledge Base & Vector Store Engine (P5).
"""

import math
import pytest
from starlette.testclient import TestClient
from knowledge_base.embeddings import LocalEmbeddings
from knowledge_base.vector_store import LocalVectorStore, ChunkRecord
from knowledge_base.ingest import parse_markdown_metadata, chunk_document
from knowledge_base.retriever import SovereignRetriever
from knowledge_base.server import app

def test_embeddings_dimensions_and_normalization():
    embedder = LocalEmbeddings(dimension=384)
    vec1 = embedder.embed_text("Ultrasonic thickness inspection for Column CRU-C-101")
    
    assert len(vec1) == 384
    norm = math.sqrt(sum(x * x for x in vec1))
    assert abs(norm - 1.0) < 1e-4

    sim_self = LocalEmbeddings.cosine_similarity(vec1, vec1)
    assert abs(sim_self - 1.0) < 1e-4

    vec2 = embedder.embed_text("Crude distillation column UT wall thickness inspection")
    sim_related = LocalEmbeddings.cosine_similarity(vec1, vec2)
    assert sim_related > 0.40

def test_metadata_parsing():
    sample_text = """# Mangalore Refinery and Petrochemicals Limited
## Standard Operating Procedure: Hot Work Permit
**Document Code:** MRPL-SOP-HWP-108
**Refinery Unit:** Refinery Wide / HSE
**Revision:** 6.0
**Effective Date:** 2026-01-10
"""
    meta = parse_markdown_metadata(sample_text)
    assert meta["code"] == "MRPL-SOP-HWP-108"
    assert "Hot Work Permit" in meta["title"]
    assert "Refinery Wide" in meta["unit"]
    assert meta["revision"] == "6.0"

def test_chunking():
    sample_doc = """### Section 1: Scope
This is the scope section.

### Section 2: Temperature Limits
Maximum allowable temperature is 385 deg C.
"""
    meta = {"code": "TEST-01", "title": "Test Doc", "unit": "CDU", "revision": "1.0", "date": "2026"}
    chunks = chunk_document(sample_doc, meta)
    assert len(chunks) == 2
    assert "Scope" in chunks[0]["section"]
    assert "Temperature Limits" in chunks[1]["section"]

def test_retrieval_accuracy_cru_c101():
    retriever = SovereignRetriever()
    citations = retriever.query(
        query_text="minimum retirement thickness for CRU-C-101 intermediate shell",
        top_k=3
    )
    
    assert len(citations) > 0
    top_hit = citations[0]
    assert top_hit["document_code"] == "MRPL-SOP-CRU-402"
    assert "Section 4" in top_hit["section"] or "Section" in top_hit["section"]
    assert top_hit["similarity_score"] >= 0.70

def test_retrieval_accuracy_api_510():
    retriever = SovereignRetriever()
    citations = retriever.query(
        query_text="Remaining useful life calculation formula API 510",
        top_k=3
    )
    
    assert len(citations) > 0
    codes = [c["document_code"] for c in citations]
    assert "MRPL-STD-API-510" in codes

def test_retrieval_accuracy_hot_work_lel():
    retriever = SovereignRetriever()
    citations = retriever.query(
        query_text="Hazardous hot work atmospheric LEL and H2S oxygen limits",
        top_k=3
    )
    
    assert len(citations) > 0
    codes = [c["document_code"] for c in citations]
    assert "MRPL-SOP-HWP-108" in codes

def test_fastapi_server_endpoints():
    client = TestClient(app)
    
    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] == "ONLINE"
    assert data["documents_indexed"] == 12
    assert data["chunks_indexed"] == 49
    assert data["network_posture"].startswith("AIRGAPPED")

    # 2. Query endpoint
    res_query = client.post("/query", json={
        "query": "CRU-C-101 minimum retirement thickness",
        "top_k": 2
    })
    assert res_query.status_code == 200
    query_data = res_query.json()
    assert query_data["total_hits"] >= 1
    assert "citations" in query_data
    assert query_data["citations"][0]["document_code"] == "MRPL-SOP-CRU-402"

    # 3. Documents list
    res_docs = client.get("/documents")
    assert res_docs.status_code == 200
    docs_data = res_docs.json()
    assert docs_data["count"] == 12
