"""
API Integration Test Script.
Tests the running FastAPI backend with real HTTP requests.
Run from project root: python backend/scripts/test_api.py
"""
import os
import sys
import json
import time

# -- Try to use 'requests' if available, else fall back to urllib --
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    USE_REQUESTS = False

BASE_URL = "http://127.0.0.1:8000"
PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "sample_notes", "AI_and_Machine_Learning_Study_Notes.pdf"
)


def get(path):
    """HTTP GET helper."""
    if USE_REQUESTS:
        r = requests.get(f"{BASE_URL}{path}", timeout=30)
        return r.status_code, r.json()
    else:
        req = urllib.request.Request(f"{BASE_URL}{path}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.getcode(), json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())


def post_json(path, data):
    """HTTP POST with JSON body."""
    body = json.dumps(data).encode()
    if USE_REQUESTS:
        r = requests.post(f"{BASE_URL}{path}", json=data, timeout=30)
        return r.status_code, r.json()
    else:
        req = urllib.request.Request(
            f"{BASE_URL}{path}", data=body,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.getcode(), json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())


def upload_pdf(path):
    """Multipart PDF upload."""
    if USE_REQUESTS:
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f, "application/pdf")}
            r = requests.post(f"{BASE_URL}/api/documents/upload", files=files, timeout=60)
        return r.status_code, r.json()
    else:
        boundary = "----StudyMateTestBoundary"
        with open(path, "rb") as f:
            file_data = f.read()
        fname = os.path.basename(path).encode()
        body = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{os.path.basename(path)}\"\r\n"
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            f"{BASE_URL}/api/documents/upload", data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.getcode(), json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())


def delete(path):
    """HTTP DELETE helper."""
    if USE_REQUESTS:
        r = requests.delete(f"{BASE_URL}{path}", timeout=30)
        return r.status_code, r.json()
    else:
        req = urllib.request.Request(f"{BASE_URL}{path}", method="DELETE")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.getcode(), json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())


def run_api_tests():
    print("=" * 60)
    print("🌐  STUDY MATE AI – API Integration Tests")
    print("=" * 60)

    # ── Test 1: Root ─────────────────────────────────────────────────────────
    print("\n──── Test 1: Root endpoint ────")
    status, data = get("/")
    print(f"  GET /  →  {status}: {data}")
    assert status == 200
    assert data["status"] == "online"
    print("  ✓ Root endpoint OK")

    # ── Test 2: Health check ──────────────────────────────────────────────────
    print("\n──── Test 2: Health check ────")
    status, data = get("/api/health")
    print(f"  GET /api/health  →  {status}: {data}")
    assert status == 200
    assert data["status"] == "healthy"
    print(f"  ✓ Health OK (Gemini configured: {data['gemini_configured']})")

    # ── Test 3: Stats ─────────────────────────────────────────────────────────
    print("\n──── Test 3: Dashboard stats ────")
    status, data = get("/api/stats")
    print(f"  GET /api/stats  →  {status}: {data}")
    assert status == 200
    assert "total_documents" in data
    print(f"  ✓ Stats OK (docs: {data['total_documents']}, chunks: {data['total_chunks']})")

    # ── Test 4: PDF Upload ────────────────────────────────────────────────────
    print("\n──── Test 4: PDF Upload ────")
    assert os.path.exists(PDF_PATH), f"Sample PDF not found at {PDF_PATH}"
    print(f"  Uploading: {os.path.basename(PDF_PATH)}")
    status, data = upload_pdf(PDF_PATH)
    print(f"  POST /api/documents/upload  →  {status}")
    print(f"  Response: {json.dumps(data, indent=2)}")
    assert status == 200, f"Upload failed with {status}: {data}"
    doc = data.get("document", data)
    doc_id = doc.get("id") or doc.get("doc_id")
    assert doc_id, "No doc_id returned"
    total_chunks = doc.get("total_chunks", 0)
    assert total_chunks > 0, f"Expected chunks > 0, got {total_chunks}"
    assert doc.get("status") == "ready"
    print(f"  ✓ Upload OK (doc_id: {doc_id}, chunks: {total_chunks})")

    # ── Test 5: List Documents ────────────────────────────────────────────────
    print("\n──── Test 5: List documents ────")
    status, data = get("/api/documents")
    print(f"  GET /api/documents  →  {status}: found {len(data)} docs")
    assert status == 200
    assert len(data) >= 1
    print(f"  ✓ Documents listed OK")

    # ── Test 6: Stats (updated after upload) ─────────────────────────────────
    print("\n──── Test 6: Updated stats after upload ────")
    status, data = get("/api/stats")
    assert status == 200
    assert data["total_documents"] >= 1
    assert data["total_chunks"] > 0
    assert data["vector_index_ready"] == True
    print(f"  ✓ Stats updated (docs: {data['total_documents']}, chunks: {data['total_chunks']}, index_ready: {data['vector_index_ready']})")

    # ── Test 7: Chat (no Gemini key – graceful message) ───────────────────────
    print("\n──── Test 7: Chat endpoint (no Gemini key) ────")
    status, data = post_json("/api/chat", {"question": "What is supervised learning?"})
    print(f"  POST /api/chat  →  {status}: {data}")
    # Should return 200 or 503 with a helpful message (not a crash)
    assert status in (200, 503, 400)
    print(f"  ✓ Chat responded gracefully (no crash)")

    # ── Test 8: Summary (no Gemini key) ──────────────────────────────────────
    print("\n──── Test 8: Summary endpoint (no Gemini key) ────")
    status, data = post_json("/api/summary", {"doc_id": doc_id})
    print(f"  POST /api/summary  →  {status}")
    assert status in (200, 503, 400)
    print(f"  ✓ Summary responded gracefully (no crash)")

    # ── Test 9: Delete Document ───────────────────────────────────────────────
    print("\n──── Test 9: Document deletion ────")
    status, data = delete(f"/api/documents/{doc_id}")
    print(f"  DELETE /api/documents/{doc_id}  →  {status}: {data}")
    assert status == 200

    # Verify FAISS cleaned
    status2, stats2 = get("/api/stats")
    print(f"  Stats after deletion: {stats2}")
    assert stats2["total_documents"] == 0
    assert stats2["total_chunks"] == 0
    print(f"  ✓ Deletion OK – FAISS index cleared")

    print("\n" + "=" * 60)
    print("🎉  ALL API INTEGRATION TESTS PASSED!")
    print("    Backend is fully operational.")
    print("=" * 60)


if __name__ == "__main__":
    run_api_tests()
