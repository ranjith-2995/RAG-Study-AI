import os
from typing import Dict, Any, List, Optional
from backend.rag.vectorstore import FAISSVectorStoreManager
from backend.services.gemini_service import GeminiService
from backend.models.schemas import SourceCitation

class RAGPipeline:
    """
    Retrieval-Augmented Generation (RAG) Pipeline:
    Coordinates Vector Retrieval (Sentence Transformers + FAISS)
    with Context-Grounded Answer Generation (Google Gemini).
    """
    _instance = None

    def __init__(self):
        self.vector_manager = FAISSVectorStoreManager.get_instance()
        self.gemini_service = GeminiService.get_instance()
        self.top_k = int(os.getenv("TOP_K_RESULTS", "4"))

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def answer_question(self, question: str, selected_doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full RAG cycle:
        1. Query Vector Search in FAISS
        2. Filter and rank relevant chunks
        3. Extract source citations (doc name, page, snippet)
        4. Pass context to Gemini
        5. Return grounded answer and source citations
        """
        clean_question = question.strip()
        if not clean_question:
            return {
                "question": question,
                "answer": "Please ask a question about your study materials.",
                "sources": [],
                "found_in_docs": False
            }

        # Check if vector store has any documents
        total_chunks = self.vector_manager.get_total_chunks()
        if total_chunks == 0:
            return {
                "question": question,
                "answer": (
                    "📚 **No study materials uploaded yet!**\n\n"
                    "Please upload one or more PDF study documents using the upload section. "
                    "Once processed, you can ask questions and I will answer directly from your notes."
                ),
                "sources": [],
                "found_in_docs": False
            }

        # 1 & 2: Similarity search in FAISS
        search_results = self.vector_manager.search(
            query=clean_question,
            top_k=self.top_k,
            doc_id=selected_doc_id
        )

        if not search_results:
            return {
                "question": question,
                "answer": (
                    "I could not find relevant information in the uploaded study documents to answer this question. "
                    "Please ensure the topic is covered in your uploaded PDFs."
                ),
                "sources": [],
                "found_in_docs": False
            }

        # 3: Extract chunks and citations
        retrieved_chunks = []
        sources: List[SourceCitation] = []

        for doc, score in search_results:
            metadata = doc.metadata
            doc_id = metadata.get("doc_id", "")
            filename = metadata.get("filename", "Unknown Document")
            page = metadata.get("page", 1)
            chunk_id = metadata.get("chunk_id", "")
            text = doc.page_content

            retrieved_chunks.append({
                "text": text,
                "metadata": metadata
            })

            # Create clean snippet for UI source citation
            snippet = text[:220] + "..." if len(text) > 220 else text
            sources.append(
                SourceCitation(
                    doc_id=doc_id,
                    filename=filename,
                    page=page,
                    chunk_id=chunk_id,
                    snippet=snippet,
                    score=float(score) if score is not None else None
                )
            )

        # 4: Pass context to Gemini
        llm_response = self.gemini_service.generate_rag_answer(
            question=clean_question,
            retrieved_chunks=retrieved_chunks
        )

        return {
            "question": question,
            "answer": llm_response["answer"],
            "sources": sources,
            "found_in_docs": llm_response["found_in_docs"]
        }

