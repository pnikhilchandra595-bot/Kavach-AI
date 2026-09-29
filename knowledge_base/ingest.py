"""
Corpus Ingestion Pipeline for MRPL Sovereign AI Workbench.
Reads synthetic refinery SOPs, chunks by technical sections, generates embeddings,
and indexes into the persistent local vector store.
"""

import os
import re
from typing import List, Dict, Any
from .embeddings import LocalEmbeddings
from .vector_store import LocalVectorStore, ChunkRecord

def parse_markdown_metadata(content: str) -> Dict[str, str]:
    meta = {
        "code": "UNKNOWN",
        "title": "Untitled Document",
        "unit": "General Refinery",
        "revision": "1.0",
        "date": "2026-01-01"
    }
    
    code_match = re.search(r'\*\*Document Code:\*\*\s*([^\n\r]+)', content)
    if code_match:
        meta["code"] = code_match.group(1).strip()

    title_match = re.search(r'##\s*([^\n\r]+)', content)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    unit_match = re.search(r'\*\*Refinery Unit:\*\*\s*([^\n\r]+)', content)
    if unit_match:
        meta["unit"] = unit_match.group(1).strip()

    rev_match = re.search(r'\*\*Revision:\*\*\s*([^\n\r]+)', content)
    if rev_match:
        meta["revision"] = rev_match.group(1).strip()

    date_match = re.search(r'\*\*Effective Date:\*\*\s*([^\n\r]+)', content)
    if date_match:
        meta["date"] = date_match.group(1).strip()

    return meta

def chunk_document(content: str, meta: Dict[str, str]) -> List[Dict[str, Any]]:
    # Split document by sections
    sections = re.split(r'(###\s+Section\s+[^:\n]+:[^\n]+)', content)
    chunks_data = []

    if len(sections) <= 1:
        # No section markers, split by double newlines
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        for idx, p in enumerate(paragraphs):
            chunks_data.append({
                "section": "General Overview",
                "text": p,
                "index": idx + 1
            })
        return chunks_data

    # Pair headings with their bodies
    # sections[0] is preamble before first section
    if sections[0].strip():
        chunks_data.append({
            "section": "Document Header & Scope",
            "text": sections[0].strip(),
            "index": 1
        })

    for i in range(1, len(sections), 2):
        heading = sections[i].replace('###', '').strip()
        body = sections[i+1].strip() if i+1 < len(sections) else ""
        
        full_text = f"{heading}\n{body}"
        
        # If body is very long, break into paragraph chunks
        paras = [p.strip() for p in body.split('\n\n') if p.strip()]
        if len(paras) > 2 and len(body.split()) > 250:
            for p_idx, p in enumerate(paras):
                chunks_data.append({
                    "section": f"{heading} (Part {p_idx+1})",
                    "text": f"{heading}\n\n{p}",
                    "index": len(chunks_data) + 1
                })
        else:
            chunks_data.append({
                "section": heading,
                "text": full_text,
                "index": len(chunks_data) + 1
            })

    return chunks_data

def run_ingestion(corpus_dir: str = None, storage_dir: str = None) -> LocalVectorStore:
    base_dir = os.path.dirname(__file__)
    corpus_path = corpus_dir or os.path.join(base_dir, "synthetic_corpus")
    
    embedder = LocalEmbeddings(dimension=384)
    vector_store = LocalVectorStore(storage_dir=storage_dir)
    vector_store.clear()

    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus directory not found: {corpus_path}")

    files = sorted([f for f in os.listdir(corpus_path) if f.endswith(".md")])
    print(f"=== Starting Ingestion for {len(files)} Synthetic SOP Documents ===")

    total_chunks = 0

    for fname in files:
        fpath = os.path.join(corpus_path, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        meta = parse_markdown_metadata(content)
        chunks = chunk_document(content, meta)

        for c in chunks:
            chunk_id = f"{meta['code'].lower().replace('-', '_')}_chk_{c['index']:02d}"
            # Compute dense embedding
            vector = embedder.embed_text(c["text"])

            record = ChunkRecord(
                chunk_id=chunk_id,
                document_code=meta["code"],
                document_title=meta["title"],
                refinery_unit=meta["unit"],
                section_title=c["section"],
                text_content=c["text"],
                embedding=vector,
                metadata={
                    "filename": fname,
                    "revision": meta["revision"],
                    "effective_date": meta["date"],
                    "word_count": len(c["text"].split())
                }
            )
            vector_store.add_chunk(record)
            total_chunks += 1

        print(f"  [+] Ingested {meta['code']}: {len(chunks)} chunks from {fname}")

    saved_path = vector_store.save()
    print(f"\n[SUCCESS] Ingestion complete: {total_chunks} total chunks indexed.")
    print(f"[STORED] Persistent index saved to: {saved_path}")
    return vector_store

if __name__ == "__main__":
    run_ingestion()
