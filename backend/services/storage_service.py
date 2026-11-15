import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

METADATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "metadata.json")

def load_metadata() -> Dict[str, Any]:
    """Load documents metadata from JSON file."""
    if not os.path.exists(METADATA_FILE):
        return {"documents": {}}
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return {"documents": {}}

def save_metadata(data: Dict[str, Any]) -> None:
    """Save documents metadata to JSON file."""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_all_documents() -> List[Dict[str, Any]]:
    """Retrieve list of all uploaded documents."""
    meta = load_metadata()
    return list(meta.get("documents", {}).values())

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a single document by doc_id."""
    meta = load_metadata()
    return meta.get("documents", {}).get(doc_id)

def add_document(doc_info: Dict[str, Any]) -> None:
    """Register or update a document in metadata."""
    meta = load_metadata()
    meta.setdefault("documents", {})[doc_info["id"]] = doc_info
    save_metadata(meta)

def delete_document_metadata(doc_id: str) -> Optional[Dict[str, Any]]:
    """Delete a document record from metadata."""
    meta = load_metadata()
    if doc_id in meta.get("documents", {}):
        doc = meta["documents"].pop(doc_id)
        save_metadata(meta)
        return doc
    return None

