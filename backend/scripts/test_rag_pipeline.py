"""
End-to-end RAG pipeline validation test.
Run from the project root:  python backend/scripts/test_rag_pipeline.py
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add project root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.services.pdf_service import extract_text_from_pdf
from backend.rag.text_splitter import create_document_chunks
from backend.rag.embeddings import LocalSentenceTransformerEmbeddings
from backend.rag.vectorstore import FAISSVectorStoreManager


def run_tests():
    print("=" * 60)
    print("🧪  STUDY MATE AI – End-to-End RAG Pipeline Validation")
    print("=" * 60)

    pdf_path = os.path.join(root_dir, "sample_notes", "AI_and_Machine_Learning_Study_Notes.pdf")
    assert os.path.exists(pdf_path), f"Sample PDF missing at: {pdf_path}"
    print(f"✓ Found sample PDF: {pdf_path}")

    # ── Test 1: PDF Text Extraction ────────────────────────────────────────────
    print("\n──── Test 1: PDF Text Extraction ────")
    pages_data, total_pages = extract_text_from_pdf(pdf_path)
    print(f"  Pages extracted : {len(pages_data)}")
    print(f"  Total pages     : {total_pages}")
    assert total_pages == 3, f"Expected 3 pages, got {total_pages}"
    assert "Supervised Learning" in pages_data[0]["text"], "Page 1 missing ML content"
    assert "Attention" in pages_data[1]["text"],           "Page 2 missing Transformer content"
    assert "FAISS" in pages_data[2]["text"],               "Page 3 missing RAG content"
    print("  ✓ All page contents verified.")

    # ── Test 2: Text Chunking ──────────────────────────────────────────────────
    print("\n──── Test 2: Text Chunking & Metadata ────")
    doc_id   = "unit-test-doc-001"
    filename = "AI_and_Machine_Learning_Study_Notes.pdf"
    chunks = create_document_chunks(pages_data, doc_id=doc_id, filename=filename,
                                    chunk_size=600, chunk_overlap=100)
    print(f"  Chunks generated : {len(chunks)}")
    assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"
    for c in chunks:
        assert c["metadata"]["doc_id"] == doc_id
        assert c["metadata"]["filename"] == filename
        assert "page" in c["metadata"]
    print(f"  Sample metadata  : {chunks[0]['metadata']}")
    print("  ✓ Chunk metadata correct.")

    # ── Test 3: Embeddings ────────────────────────────────────────────────────
    print("\n──── Test 3: Sentence Transformers Embeddings ────")
    embedder = LocalSentenceTransformerEmbeddings.get_instance()
    sample   = ["Machine learning paradigms: supervised, unsupervised, reinforcement."]
    vectors  = embedder.embed_documents(sample)
    assert len(vectors) == 1
    assert len(vectors[0]) == 384, f"Expected 384-dim, got {len(vectors[0])}"
    print(f"  Vector dimension : {len(vectors[0])}")
    print("  ✓ Embeddings verified.")

    # ── Test 4: FAISS Indexing & Similarity Search ────────────────────────────
    print("\n──── Test 4: FAISS Indexing & Search ────")
    vm = FAISSVectorStoreManager.get_instance()
    # Clean any leftover state from this test doc
    vm.delete_document(doc_id)

    added = vm.add_chunks(chunks)
    print(f"  Chunks indexed   : {added}")
    assert added == len(chunks)

    # Semantic query → expects Page 2 (Transformer content)
    q1 = "What is the scaled dot product attention formula?"
    r1 = vm.search(q1, top_k=2)
    print(f"  Results for '{q1[:45]}...' : {len(r1)} results")
    assert len(r1) > 0, "Expected at least 1 result"
    top_doc, score = r1[0]
    print(f"    Top match – Page: {top_doc.metadata.get('page')}, Distance: {score:.4f}")
    print(f"    Snippet: {top_doc.page_content[:100]}…")
    assert top_doc.metadata.get("page") == 2, \
        f"Expected Page 2 for Attention query, got Page {top_doc.metadata.get('page')}"

    # Semantic query → expects Page 1 (ML taxonomy content)
    q2 = "Difference between supervised and unsupervised learning"
    r2 = vm.search(q2, top_k=1)
    assert len(r2) > 0
    assert r2[0][0].metadata.get("page") == 1, \
        f"Expected Page 1 for ML taxonomy, got Page {r2[0][0].metadata.get('page')}"
    print("  ✓ Semantic search routing verified (Page 2 → Attention, Page 1 → ML taxonomy).")

    # doc_id filter
    r3 = vm.search(q1, top_k=2, doc_id="nonexistent-doc")
    assert len(r3) == 0, "Filter by nonexistent doc_id should return empty list"
    print("  ✓ doc_id filtering works correctly.")

    # ── Test 5: Vector DB Clean Deletion ──────────────────────────────────────
    print("\n──── Test 5: Document Deletion & Vector Purge ────")
    removed = vm.delete_document(doc_id)
    print(f"  Vectors removed  : {removed}")
    assert removed == added, f"Expected {added} removals, got {removed}"
    r4 = vm.search(q1, top_k=2)
    assert len(r4) == 0, "Expected empty results after deletion"
    assert vm.get_total_chunks() == 0
    print("  ✓ FAISS clean purge verified – zero ghost vectors remain.")

    print("\n" + "=" * 60)
    print("🎉  ALL 5 RAG PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("    The core RAG engine is fully operational.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
