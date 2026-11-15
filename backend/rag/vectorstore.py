import os
import json
import shutil
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import faiss
from langchain_core.documents import Document
from backend.rag.embeddings import LocalSentenceTransformerEmbeddings

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db")
INDEX_PATH = os.path.join(DB_DIR, "faiss_index.bin")
META_PATH  = os.path.join(DB_DIR, "faiss_meta.json")
CHUNKS_FILE = os.path.join(DB_DIR, "chunks_store.json")

class FAISSVectorStoreManager:
    """
    Pure FAISS vector store manager (no LangChain wrapper).
    
    Uses raw faiss-cpu directly:
    - IndexFlatL2 for exact L2 similarity search.
    - Persists index binary + metadata JSON to disk.
    - Supports incremental additions, per-document deletion with rebuild.
    """
    _instance = None

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.embeddings = LocalSentenceTransformerEmbeddings.get_instance()
        self.dim = 384          # all-MiniLM-L6-v2 dimension
        self.index: Optional[faiss.IndexFlatL2] = None
        self._meta: List[Dict[str, Any]] = []  # parallel list: meta[i] corresponds to index vector i
        self._load_or_init()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------ I/O --
    def _load_or_init(self) -> None:
        """Load persisted FAISS index + meta from disk, or start fresh."""
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            try:
                self.index = faiss.read_index(INDEX_PATH)
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self._meta = json.load(f)
                print(f"Loaded FAISS index from disk ({self.index.ntotal} vectors, {len(self._meta)} meta entries).")
            except Exception as e:
                print(f"Could not load existing index ({e}). Starting fresh.")
                self._reset()
        else:
            print("No existing FAISS index found. Ready for first document.")
            self._reset()

    def _reset(self) -> None:
        self.index = faiss.IndexFlatL2(self.dim)
        self._meta = []

    def _save(self) -> None:
        """Persist index binary and metadata to disk."""
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self._meta, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------- Chunk store (JSON) --
    def _load_chunks(self) -> List[Dict[str, Any]]:
        if not os.path.exists(CHUNKS_FILE):
            return []
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

    # ----------------------------------------------------------------- API ---
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and indexes new text chunks into FAISS.
        Each chunk dict: {"text": str, "metadata": {...}}
        """
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        vectors = self.embeddings.embed_documents(texts)
        matrix = np.array(vectors, dtype=np.float32)

        self.index.add(matrix)

        # Append meta entries (one per vector)
        for chunk in chunks:
            self._meta.append({
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            })

        self._save()

        # Update persistent chunk store (source of truth for rebuilds)
        all_chunks = self._load_chunks()
        all_chunks.extend(chunks)
        self._save_chunks(all_chunks)

        print(f"Added {len(chunks)} chunks to FAISS. Total vectors: {self.index.ntotal}")
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 4,
        doc_id: Optional[str] = None
    ) -> List[Tuple[Document, float]]:
        """
        Similarity search. Returns list of (LangChain Document, L2 distance).
        Lower distance = better match.
        Optionally filters to chunks belonging to `doc_id`.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vec = np.array([self.embeddings.embed_query(query)], dtype=np.float32)

        # Fetch more candidates when filtering, then trim to top_k
        fetch_k = min(self.index.ntotal, top_k * 5 if doc_id else top_k)
        distances, indices = self.index.search(query_vec, fetch_k)

        results: List[Tuple[Document, float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._meta):
                continue
            entry = self._meta[idx]
            meta = entry["metadata"]
            if doc_id and meta.get("doc_id") != doc_id:
                continue
            doc = Document(page_content=entry["text"], metadata=meta)
            results.append((doc, float(dist)))
            if len(results) >= top_k:
                break

        return results

    def delete_document(self, doc_id: str) -> int:
        """
        Removes all vectors belonging to `doc_id` and rebuilds the index.
        Returns the count of removed vectors.
        """
        all_chunks = self._load_chunks()
        remaining = [c for c in all_chunks if c.get("metadata", {}).get("doc_id") != doc_id]
        removed_count = len(all_chunks) - len(remaining)

        if removed_count == 0:
            print(f"No chunks found for doc_id={doc_id}.")
            return 0

        # Save updated chunk store
        self._save_chunks(remaining)

        # Rebuild index from scratch
        self._reset()
        if remaining:
            texts = [c["text"] for c in remaining]
            vectors = self.embeddings.embed_documents(texts)
            matrix = np.array(vectors, dtype=np.float32)
            self.index.add(matrix)
            self._meta = [{"text": c["text"], "metadata": c["metadata"]} for c in remaining]
            self._save()
            print(f"Rebuilt FAISS index with {len(remaining)} vectors after removing {removed_count} from doc {doc_id}.")
        else:
            # No documents left – remove files
            for path in [INDEX_PATH, META_PATH]:
                if os.path.exists(path):
                    os.remove(path)
            print("All documents removed. FAISS index cleared.")

        return removed_count

    def get_total_chunks(self) -> int:
        """Return total number of indexed vectors."""
        if self.index is None:
            return 0
        return self.index.ntotal
