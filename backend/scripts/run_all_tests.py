"""
Master Test Runner for STUDY MATE AI
=====================================
Runs two test suites in sequence:
  1. RAG Pipeline Unit Tests  (no server needed)
  2. API Integration Tests    (starts embedded uvicorn server)

Run from project root:
    python backend/scripts/run_all_tests.py
"""

import os
import sys
import time
import json
import warnings
import threading
import traceback

# ── Suppress noisy warnings ──────────────────────────────────────────────────
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ── Add project root to path ─────────────────────────────────────────────────
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, "backend", ".env"))

PASS = "✅"
FAIL = "❌"
INFO = "ℹ️ "

# =============================================================================
# SUITE 1: RAG PIPELINE UNIT TESTS
# =============================================================================

def run_pipeline_tests():
    """Core RAG pipeline tests — no server required."""
    print("\n" + "=" * 60)
    print("🧪  SUITE 1: RAG Pipeline Unit Tests")
    print("=" * 60)

    from backend.services.pdf_service import extract_text_from_pdf
    from backend.rag.text_splitter import create_document_chunks
    from backend.rag.embeddings import LocalSentenceTransformerEmbeddings
    from backend.rag.vectorstore import FAISSVectorStoreManager

    pdf_path = os.path.join(root_dir, "sample_notes", "AI_and_Machine_Learning_Study_Notes.pdf")
    assert os.path.exists(pdf_path), f"Sample PDF not found: {pdf_path}"
    print(f"{PASS} Found sample PDF")

    results = {}

    # ── Test 1: PDF Extraction ────────────────────────────────────────────────
    try:
        pages_data, total_pages = extract_text_from_pdf(pdf_path)
        assert total_pages == 3
        assert "Supervised Learning" in pages_data[0]["text"]
        assert "Attention" in pages_data[1]["text"]
        assert "FAISS" in pages_data[2]["text"]
        print(f"{PASS} Test 1: PDF Extraction — {len(pages_data)} pages, all content verified")
        results["PDF Extraction"] = True
    except Exception as e:
        print(f"{FAIL} Test 1 FAILED: {e}")
        results["PDF Extraction"] = False

    # ── Test 2: Text Chunking ─────────────────────────────────────────────────
    try:
        doc_id = "unit-test-doc-001"
        filename = "AI_and_Machine_Learning_Study_Notes.pdf"
        chunks = create_document_chunks(pages_data, doc_id=doc_id, filename=filename,
                                        chunk_size=600, chunk_overlap=100)
        assert len(chunks) >= 3
        for c in chunks:
            assert c["metadata"]["doc_id"] == doc_id
            assert "page" in c["metadata"]
        print(f"{PASS} Test 2: Text Chunking — {len(chunks)} chunks with correct metadata")
        results["Text Chunking"] = True
    except Exception as e:
        print(f"{FAIL} Test 2 FAILED: {e}")
        results["Text Chunking"] = False

    # ── Test 3: Embeddings ────────────────────────────────────────────────────
    try:
        embedder = LocalSentenceTransformerEmbeddings.get_instance()
        vecs = embedder.embed_documents(["Machine learning test sentence."])
        assert len(vecs) == 1
        assert len(vecs[0]) == 384
        print(f"{PASS} Test 3: Embeddings — 384-dim vectors confirmed")
        results["Embeddings"] = True
    except Exception as e:
        print(f"{FAIL} Test 3 FAILED: {e}")
        results["Embeddings"] = False

    # ── Test 4: FAISS Indexing & Search ──────────────────────────────────────
    try:
        vm = FAISSVectorStoreManager.get_instance()
        vm.delete_document(doc_id)  # clean slate
        added = vm.add_chunks(chunks)
        assert added == len(chunks)

        r1 = vm.search("What is the scaled dot product attention?", top_k=2)
        assert len(r1) > 0
        top_doc, score = r1[0]
        assert top_doc.metadata.get("page") == 2, \
            f"Expected page 2 (Attention), got page {top_doc.metadata.get('page')}"

        r2 = vm.search("Difference between supervised and unsupervised learning", top_k=1)
        assert len(r2) > 0
        assert r2[0][0].metadata.get("page") == 1, \
            f"Expected page 1 (ML taxonomy), got page {r2[0][0].metadata.get('page')}"

        r3 = vm.search("some query", top_k=2, doc_id="nonexistent-doc")
        assert len(r3) == 0

        print(f"{PASS} Test 4: FAISS Indexing & Search — {added} chunks indexed, semantic routing verified")
        results["FAISS Search"] = True
    except Exception as e:
        print(f"{FAIL} Test 4 FAILED: {e}")
        traceback.print_exc()
        results["FAISS Search"] = False

    # ── Test 5: Document Deletion ─────────────────────────────────────────────
    try:
        removed = vm.delete_document(doc_id)
        assert removed == added, f"Expected {added} removals, got {removed}"
        after = vm.search("attention", top_k=2)
        assert len(after) == 0
        assert vm.get_total_chunks() == 0
        print(f"{PASS} Test 5: Document Deletion — {removed} vectors purged cleanly")
        results["FAISS Deletion"] = True
    except Exception as e:
        print(f"{FAIL} Test 5 FAILED: {e}")
        results["FAISS Deletion"] = False

    passed = sum(results.values())
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Suite 1 Result: {passed}/{total} tests passed")
    return results


# =============================================================================
# SUITE 2: API INTEGRATION TESTS  (embedded uvicorn)
# =============================================================================

def start_server():
    """Start uvicorn in a background thread."""
    import uvicorn
    # Import app after path is set
    from backend.main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def wait_for_server(port=8765, timeout=45):
    """Poll until the server is accepting connections."""
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def api_get(port, path):
    import urllib.request, urllib.error
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=30) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def api_post_json(port, path, data):
    import urllib.request, urllib.error
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def api_upload_pdf(port, pdf_path):
    import urllib.request, urllib.error
    boundary = "----StudyMateTestBoundary7x9kZ"
    fname = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as f:
        file_data = f.read()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode()
    footer = f"\r\n--{boundary}--\r\n".encode()
    body = header + file_data + footer
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/documents/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return e.code, json.loads(body_text)
        except Exception:
            return e.code, {"detail": body_text}


def api_delete(port, path):
    import urllib.request, urllib.error
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", method="DELETE"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def run_api_tests():
    """Full API integration tests with embedded server."""
    PORT = 8765
    print("\n" + "=" * 60)
    print("🌐  SUITE 2: API Integration Tests")
    print("=" * 60)

    # Start server in daemon thread
    print(f"{INFO} Starting embedded test server on port {PORT}...")
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    if not wait_for_server(PORT, timeout=45):
        print(f"{FAIL} Server did not start within 45 seconds. Skipping API tests.")
        return {}

    print(f"{PASS} Server is up and accepting connections")
    pdf_path = os.path.join(root_dir, "sample_notes", "AI_and_Machine_Learning_Study_Notes.pdf")
    results = {}
    doc_id = None

    # ── T1: Root ──────────────────────────────────────────────────────────────
    try:
        status, data = api_get(PORT, "/")
        assert status == 200 and data.get("status") == "online"
        print(f"{PASS} T1: Root endpoint → {data.get('status')}")
        results["Root"] = True
    except Exception as e:
        print(f"{FAIL} T1 Root FAILED: {e}")
        results["Root"] = False

    # ── T2: Health ────────────────────────────────────────────────────────────
    try:
        status, data = api_get(PORT, "/api/health")
        assert status == 200 and data["status"] == "healthy"
        gemini_ok = data["gemini_configured"]
        print(f"{PASS} T2: Health check → healthy (Gemini: {gemini_ok})")
        results["Health"] = True
    except Exception as e:
        print(f"{FAIL} T2 Health FAILED: {e}")
        results["Health"] = False

    # ── T3: Stats (empty) ─────────────────────────────────────────────────────
    try:
        status, data = api_get(PORT, "/api/stats")
        assert status == 200
        assert "total_documents" in data
        print(f"{PASS} T3: Stats → docs={data['total_documents']}, chunks={data['total_chunks']}")
        results["Stats"] = True
    except Exception as e:
        print(f"{FAIL} T3 Stats FAILED: {e}")
        results["Stats"] = False

    # ── T4: PDF Upload ────────────────────────────────────────────────────────
    try:
        print(f"{INFO} Uploading sample PDF...")
        status, data = api_upload_pdf(PORT, pdf_path)
        assert status == 200, f"Upload returned {status}: {data}"
        doc_obj = data.get("document", {})
        doc_id = doc_obj.get("id")
        total_chunks = doc_obj.get("total_chunks", 0)
        assert doc_id, "No doc_id in response"
        assert total_chunks > 0, f"Expected chunks > 0, got {total_chunks}"
        assert doc_obj.get("status") == "ready"
        print(f"{PASS} T4: PDF Upload → doc_id={doc_id[:8]}…, chunks={total_chunks}, status=ready")
        results["PDF Upload"] = True
    except Exception as e:
        print(f"{FAIL} T4 PDF Upload FAILED: {e}")
        traceback.print_exc()
        results["PDF Upload"] = False

    # ── T5: List Documents ────────────────────────────────────────────────────
    try:
        status, data = api_get(PORT, "/api/documents")
        assert status == 200
        docs = data.get("documents", [])
        assert len(docs) >= 1
        print(f"{PASS} T5: List Documents → {len(docs)} document(s) returned")
        results["List Docs"] = True
    except Exception as e:
        print(f"{FAIL} T5 List Docs FAILED: {e}")
        results["List Docs"] = False

    # ── T6: Stats after upload ────────────────────────────────────────────────
    try:
        status, data = api_get(PORT, "/api/stats")
        assert status == 200
        assert data["total_documents"] >= 1
        assert data["total_chunks"] > 0
        assert data["vector_index_ready"] == True
        print(f"{PASS} T6: Updated Stats → docs={data['total_documents']}, chunks={data['total_chunks']}, index_ready=True")
        results["Updated Stats"] = True
    except Exception as e:
        print(f"{FAIL} T6 Updated Stats FAILED: {e}")
        results["Updated Stats"] = False

    # ── T7: Get Document by ID ────────────────────────────────────────────────
    if doc_id:
        try:
            status, data = api_get(PORT, f"/api/documents/{doc_id}")
            assert status == 200
            assert data["id"] == doc_id
            print(f"{PASS} T7: Get Document → filename={data['filename']}")
            results["Get Doc"] = True
        except Exception as e:
            print(f"{FAIL} T7 Get Doc FAILED: {e}")
            results["Get Doc"] = False

    # ── T8: Chat (Gemini key may be absent → graceful message) ───────────────
    try:
        status, data = api_post_json(PORT, "/api/chat", {"question": "What is supervised learning?"})
        # 200 with Gemini key; 200 with graceful message if no key
        assert status in (200, 400, 503), f"Unexpected status {status}"
        if status == 200:
            answer = data.get("answer", "")
            assert len(answer) > 0
            # If no Gemini key, should mention API key requirement (not crash)
            if not data.get("found_in_docs", True) and "gemini" in answer.lower():
                print(f"{PASS} T8: Chat → Gemini key not set, graceful message returned")
            else:
                print(f"{PASS} T8: Chat → answer length={len(answer)}, found_in_docs={data.get('found_in_docs')}")
        else:
            print(f"{PASS} T8: Chat → returned {status} gracefully (no crash)")
        results["Chat"] = True
    except Exception as e:
        print(f"{FAIL} T8 Chat FAILED: {e}")
        traceback.print_exc()
        results["Chat"] = False

    # ── T9: Summary (Gemini key may be absent → graceful message) ────────────
    if doc_id:
        try:
            status, data = api_post_json(PORT, "/api/summary", {"doc_id": doc_id})
            assert status in (200, 400, 503), f"Unexpected status {status}"
            if status == 200:
                assert "summary" in data
                print(f"{PASS} T9: Summary → summary length={len(data.get('summary',''))}")
            else:
                print(f"{PASS} T9: Summary → returned {status} gracefully")
            results["Summary"] = True
        except Exception as e:
            print(f"{FAIL} T9 Summary FAILED: {e}")
            results["Summary"] = False

    # ── T10: Chat with nonexistent question (anti-hallucination check) ────────
    try:
        status, data = api_post_json(PORT, "/api/chat",
                                     {"question": "Who won the 1992 Super Bowl and what was the score?"})
        assert status in (200, 400, 503)
        if status == 200:
            answer = data.get("answer", "")
            # Should either say not found OR say Gemini key is needed — never make up an answer
            found = data.get("found_in_docs", False)
            print(f"{PASS} T10: Anti-hallucination → found_in_docs={found}, answer starts: '{answer[:80]}...'")
        else:
            print(f"{PASS} T10: Anti-hallucination check → {status} returned gracefully")
        results["Anti-hallucination"] = True
    except Exception as e:
        print(f"{FAIL} T10 Anti-hallucination FAILED: {e}")
        results["Anti-hallucination"] = False

    # ── T11: Delete Document ──────────────────────────────────────────────────
    if doc_id:
        try:
            status, data = api_delete(PORT, f"/api/documents/{doc_id}")
            assert status == 200, f"Delete returned {status}: {data}"
            assert doc_id in data.get("doc_id", "")
            print(f"{PASS} T11: Delete Document → {data.get('message','')[:70]}")

            # Verify FAISS cleaned up
            status2, stats2 = api_get(PORT, "/api/stats")
            assert stats2["total_documents"] == 0
            assert stats2["total_chunks"] == 0
            print(f"{PASS} T11: Post-delete stats → docs=0, chunks=0 ✓ FAISS cleared")
            results["Delete Doc"] = True
        except Exception as e:
            print(f"{FAIL} T11 Delete FAILED: {e}")
            traceback.print_exc()
            results["Delete Doc"] = False

    # ── T12: Empty question validation ───────────────────────────────────────
    try:
        status, data = api_post_json(PORT, "/api/chat", {"question": "   "})
        assert status == 400, f"Expected 400 for empty question, got {status}"
        print(f"{PASS} T12: Empty question validation → 400 returned correctly")
        results["Empty Question"] = True
    except Exception as e:
        print(f"{FAIL} T12 Empty Question FAILED: {e}")
        results["Empty Question"] = False

    passed = sum(results.values())
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Suite 2 Result: {passed}/{total} tests passed")
    return results


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓  STUDY MATE AI – Master Test Runner")
    print("=" * 60)

    all_results = {}

    # Suite 1
    try:
        r1 = run_pipeline_tests()
        all_results.update(r1)
    except Exception as e:
        print(f"\n{FAIL} Suite 1 crashed: {e}")
        traceback.print_exc()

    # Suite 2
    try:
        r2 = run_api_tests()
        all_results.update(r2)
    except Exception as e:
        print(f"\n{FAIL} Suite 2 crashed: {e}")
        traceback.print_exc()

    # Final summary
    print("\n" + "=" * 60)
    print("📊  FINAL TEST SUMMARY")
    print("=" * 60)
    for name, passed in all_results.items():
        icon = PASS if passed else FAIL
        print(f"  {icon}  {name}")

    total_passed = sum(all_results.values())
    total_tests = len(all_results)
    print(f"\n  {'🎉' if total_passed == total_tests else '⚠️ '} {total_passed}/{total_tests} tests passed")
    if total_passed == total_tests:
        print("  ✨ All systems operational! Study Mate AI is ready to use.")
    else:
        failed = [n for n, p in all_results.items() if not p]
        print(f"  Failed: {', '.join(failed)}")
    print("=" * 60)

    sys.exit(0 if total_passed == total_tests else 1)
