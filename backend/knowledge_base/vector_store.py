"""
Persistent Offline Vector Store for MRPL Sovereign AI Workbench.
Stores chunk vectors, metadata, and performs indexed cosine similarity queries.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from .embeddings import LocalEmbeddings

@dataclass
class ChunkRecord:
    chunk_id: str
    document_code: str
    document_title: str
    refinery_unit: str
    section_title: str
    text_content: str
    embedding: List[float]
    metadata: Dict[str, Any]

class LocalVectorStore:
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), "storage")
        self.storage_dir = storage_dir
        self.index_file = os.path.join(self.storage_dir, "vector_index.json")
        self.chunks: List[ChunkRecord] = []
        os.makedirs(self.storage_dir, exist_ok=True)

    def add_chunk(self, chunk: ChunkRecord):
        self.chunks.append(chunk)

    def add_chunks(self, chunks: List[ChunkRecord]):
        self.chunks.extend(chunks)

    def clear(self):
        self.chunks.clear()

    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 3, 
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search chunks by cosine similarity against query vector."""
        results = []
        for chunk in self.chunks:
            sim = LocalEmbeddings.cosine_similarity(query_vector, chunk.embedding)
            if sim >= min_similarity:
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "document_code": chunk.document_code,
                    "document_title": chunk.document_title,
                    "refinery_unit": chunk.refinery_unit,
                    "section_title": chunk.section_title,
                    "text_content": chunk.text_content,
                    "similarity": round(sim, 4),
                    "metadata": chunk.metadata,
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def save(self, filepath: Optional[str] = None) -> str:
        target_path = filepath or self.index_file
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        serialized = [asdict(c) for c in self.chunks]
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": "1.0",
                "engine": "Airgapped Local Vector Store",
                "total_chunks": len(self.chunks),
                "chunks": serialized
            }, f, indent=2)
        return target_path

    def load(self, filepath: Optional[str] = None) -> int:
        target_path = filepath or self.index_file
        if not os.path.exists(target_path):
            return 0

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.chunks = []
        for raw in data.get("chunks", []):
            self.chunks.append(ChunkRecord(
                chunk_id=raw["chunk_id"],
                document_code=raw["document_code"],
                document_title=raw["document_title"],
                refinery_unit=raw["refinery_unit"],
                section_title=raw["section_title"],
                text_content=raw["text_content"],
                embedding=raw["embedding"],
                metadata=raw.get("metadata", {})
            ))
        return len(self.chunks)

    def stats(self) -> Dict[str, Any]:
        docs = set(c.document_code for c in self.chunks)
        units = set(c.refinery_unit for c in self.chunks)
        return {
            "total_chunks": len(self.chunks),
            "total_documents": len(docs),
            "documents": sorted(list(docs)),
            "units": sorted(list(units)),
            "storage_path": self.index_file,
            "airgapped": True
        }
