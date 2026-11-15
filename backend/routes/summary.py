from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.models.schemas import SummaryRequest, SummaryResponse
from backend.services.storage_service import get_document, get_all_documents
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.gemini_service import GeminiService
from backend.rag.vectorstore import FAISSVectorStoreManager

router = APIRouter(prefix="/api/summary", tags=["summary"])

@router.post("", response_model=SummaryResponse)
async def summarize_study_material(request: SummaryRequest):
    """
    AI Study Summary Endpoint:
    Generates a structured overview, key topics, and essential study points
    from an uploaded document.
    """
    gemini = GeminiService.get_instance()
    
    # If a specific doc_id is provided
    if request.doc_id:
        doc = get_document(request.doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        
        file_path = doc.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="Document file path missing.")
            
        pages_data, _ = extract_text_from_pdf(file_path)
        full_text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages_data)
        
        res = gemini.generate_summary(full_text, doc.get("filename", "Study Notes"))
        return SummaryResponse(
            doc_id=request.doc_id,
            filename=doc.get("filename"),
            summary=res["summary"],
            key_topics=res["key_topics"],
            study_points=res["study_points"]
        )
    
    # If no doc_id is provided, summarize all available documents
    docs = get_all_documents()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents uploaded yet to summarize.")

    combined_text = []
    filenames = []
    for doc in docs[:3]:  # Summarize up to first 3 uploaded documents
        fp = doc.get("file_path")
        if fp:
            try:
                pages_data, _ = extract_text_from_pdf(fp)
                for p in pages_data[:4]:  # First few pages
                    combined_text.append(f"[{doc.get('filename')} - Page {p['page']}]\n{p['text']}")
                filenames.append(doc.get("filename"))
            except Exception:
                continue

    if not combined_text:
        raise HTTPException(status_code=400, detail="Could not read text from uploaded documents.")

    aggregated = "\n\n".join(combined_text)
    combined_name = ", ".join(filenames)
    res = gemini.generate_summary(aggregated, combined_name)

    return SummaryResponse(
        doc_id=None,
        filename=f"Combined ({len(filenames)} documents)",
        summary=res["summary"],
        key_topics=res["key_topics"],
        study_points=res["study_points"]
    )

