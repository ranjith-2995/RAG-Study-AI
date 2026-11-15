from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from backend.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_with_docs(request: ChatRequest):
    """
    RAG Chatbot Endpoint:
    1. Embeds question using local Sentence Transformers
    2. Performs similarity search in FAISS
    3. Retrieves top relevant chunks & source citations
    4. Passes context to Gemini
    5. Returns grounded response with document citations
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    pipeline = RAGPipeline.get_instance()
    result = pipeline.answer_question(
        question=request.question,
        selected_doc_id=request.selected_doc_id
    )

    return ChatResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result["sources"],
        found_in_docs=result["found_in_docs"]
    )

