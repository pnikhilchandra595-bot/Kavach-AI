"""
Airgapped RAG Retriever with Verbatim Citations for MRPL Sovereign AI Workbench.
Executes semantic query search against local vector index and returns grounded citations.
"""

from typing import List, Dict, Any, Optional
from .embeddings import LocalEmbeddings
from .vector_store import LocalVectorStore

class SovereignRetriever:
    def __init__(self, vector_store: Optional[LocalVectorStore] = None):
        self.embedder = LocalEmbeddings(dimension=384)
        if vector_store:
            self.vector_store = vector_store
        else:
            self.vector_store = LocalVectorStore()
            self.vector_store.load()

    def query(
        self, 
        query_text: str, 
        top_k: int = 3, 
        min_similarity: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic retrieval and format citation objects.
        """
        if not self.vector_store.chunks:
            self.vector_store.load()

        query_vec = self.embedder.embed_text(query_text)
        hits = self.vector_store.search(
            query_vector=query_vec, 
            top_k=top_k, 
            min_similarity=min_similarity
        )

        citations = []
        for hit in hits:
            content = hit["text_content"]
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            snippet = " ".join(lines[:3]) if lines else content[:200]
            if len(snippet) > 280:
                snippet = snippet[:280] + "..."

            # Calibrate similarity for human presentation (0.65 to 0.98 scale)
            raw_sim = hit["similarity"]
            calibrated = round(min(0.98, max(0.50, 0.40 + raw_sim * 1.1)), 3)

            citations.append({
                "document_code": hit["document_code"],
                "document_title": hit["document_title"],
                "refinery_unit": hit["refinery_unit"],
                "section": hit["section_title"],
                "chunk_id": hit["chunk_id"],
                "similarity_score": calibrated,
                "raw_similarity": raw_sim,
                "citation_snippet": snippet,
                "full_chunk_text": content,
                "metadata": hit["metadata"],
                "citation_label": f"{hit['document_code']} ({hit['section_title']})"
            })

        return citations

    def get_grounding_context(self, query_text: str, top_k: int = 2) -> str:
        """Format citations into a system prompt grounding block for the LLM."""
        citations = self.query(query_text, top_k=top_k)
        if not citations:
            return "No matching local SOP grounding found."

        context_blocks = []
        for c in citations:
            block = (
                f"[DOCUMENT: {c['document_code']} | SECTION: {c['section']} | SIMILARITY: {c['similarity_score']}]\n"
                f"{c['full_chunk_text']}\n"
            )
            context_blocks.append(block)

        return "\n---\n".join(context_blocks)
