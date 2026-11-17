from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentInfo(BaseModel):
    id: str = Field(..., description="Unique ID for the document")
    filename: str = Field(..., description="Original filename")
    upload_time: str = Field(..., description="ISO formatted upload timestamp")
    total_pages: int = Field(default=0, description="Total number of pages in the PDF")
    total_chunks: int = Field(default=0, description="Total number of text chunks generated")
    file_size_kb: float = Field(default=0.0, description="File size in kilobytes")
    status: str = Field(default="ready", description="Processing status: processing, ready, error")

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_documents: int

class UploadResponse(BaseModel):
    message: str
    document: DocumentInfo

class SourceCitation(BaseModel):
    doc_id: str
    filename: str
    page: int
    chunk_id: str
    snippet: str
    score: Optional[float] = None

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    selected_doc_id: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "English"
    history: List[ChatTurn] = Field(default_factory=list)

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    found_in_docs: bool

class SummaryRequest(BaseModel):
    doc_id: Optional[str] = None
    language: str = "English"

class SummaryResponse(BaseModel):
    doc_id: Optional[str] = None
    filename: Optional[str] = None
    summary: str
    key_topics: List[str]
    study_points: List[str]

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    vector_index_ready: bool
    embedding_model: str
    gemini_model: str

class DeleteResponse(BaseModel):
    message: str
    doc_id: str

class QuizGenerateRequest(BaseModel):
    doc_id: str
    difficulty: str = "Medium"
    count: int = Field(default=5, ge=1, le=10)

class QuizSubmitRequest(BaseModel):
    answers: dict[str, int]

class FlashcardGenerateRequest(BaseModel):
    doc_id: str
    count: int = Field(default=8, ge=1, le=20)

class FlashcardRatingRequest(BaseModel):
    rating: str

class MindMapRequest(BaseModel):
    doc_id: str

class PlannerGenerateRequest(BaseModel):
    doc_id: str
    goal: str = Field(min_length=1, max_length=300)

class PlannerTopicUpdateRequest(BaseModel):
    completed: bool

class StudyTimeRequest(BaseModel):
    seconds: int = Field(ge=1, le=86400)

