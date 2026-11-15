import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from backend.models.schemas import (
    DocumentInfo, 
    DocumentListResponse, 
    UploadResponse, 
    DeleteResponse,
    StatsResponse
)
from backend.services.storage_service import (
    get_all_documents, 
    get_document, 
    add_document, 
    delete_document_metadata
)
from backend.services.pdf_service import extract_text_from_pdf
from backend.rag.text_splitter import create_document_chunks
from backend.rag.vectorstore import FAISSVectorStoreManager
from backend.services.gemini_service import GeminiService

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Handles PDF file upload:
    1. Validates file extension
    2. Saves file to disk
    3. Extracts text per page
    4. Splits text into contextual chunks
    5. Generates embeddings and saves to FAISS
    6. Stores metadata for dashboard management
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    safe_filename = file.filename.replace(" ", "_")
    saved_filename = f"{doc_id}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)

        # Step 1: Text extraction
        pages_data, total_pages = extract_text_from_pdf(file_path)

        if not pages_data:
            # Cleanup file if no extractable text
            os.remove(file_path)
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from this PDF. Please ensure it contains selectable text and is not an image-only scan."
            )

        # Step 2: Text chunking
        chunks = create_document_chunks(
            pages_data=pages_data,
            doc_id=doc_id,
            filename=file.filename
        )

        # Step 3: Embed & Store in FAISS
        vector_manager = FAISSVectorStoreManager.get_instance()
        total_chunks = vector_manager.add_chunks(chunks)

        # Step 4: Save Document Metadata
        doc_info = {
            "id": doc_id,
            "filename": file.filename,
            "saved_filename": saved_filename,
            "file_path": file_path,
            "upload_time": datetime.utcnow().isoformat(),
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "file_size_kb": file_size_kb,
            "status": "ready"
        }
        add_document(doc_info)

        return UploadResponse(
            message=f"Document '{file.filename}' processed and indexed successfully ({total_chunks} chunks).",
            document=DocumentInfo(**doc_info)
        )

    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """Retrieve all uploaded documents for the dashboard."""
    docs = get_all_documents()
    doc_infos = [DocumentInfo(**d) for d in docs]
    return DocumentListResponse(
        documents=doc_infos,
        total_documents=len(doc_infos)
    )

@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document_by_id(doc_id: str):
    """Retrieve a single document's metadata."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentInfo(**doc)

@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    """
    Deletes a document:
    1. Removes file from disk
    2. Removes metadata record
    3. Purges all document chunks from FAISS vector store
    """
    doc = delete_document_metadata(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove physical file
    file_path = doc.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: could not delete file {file_path}: {e}")

    # Remove from FAISS vector store
    vector_manager = FAISSVectorStoreManager.get_instance()
    removed_chunks = vector_manager.delete_document(doc_id)

    return DeleteResponse(
        message=f"Document '{doc.get('filename')}' and its {removed_chunks} vector chunks were deleted successfully.",
        doc_id=doc_id
    )

