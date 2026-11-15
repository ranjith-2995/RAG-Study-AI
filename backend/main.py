import os
import sys
import warnings

# Suppress noisy deprecation warnings from google/langchain packages
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ensure the project root is in sys.path so imports like `from backend.xxx` work
# whether running as `python backend/main.py` or `uvicorn backend.main:app`
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.routes.documents import router as documents_router
from backend.routes.chat import router as chat_router
from backend.routes.summary import router as summary_router
from backend.models.schemas import StatsResponse
from backend.services.storage_service import get_all_documents
from backend.rag.vectorstore import FAISSVectorStoreManager
from backend.services.gemini_service import GeminiService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("STUDY MATE AI - Intelligent Study Notes Assistant")
    print("Retrieval-Augmented Generation (RAG) Backend")
    print("=" * 60)

    gemini = GeminiService.get_instance()
    if gemini.is_configured():
        print(f"Gemini AI connected (model: {gemini.model_name})")
    else:
        print("GEMINI_API_KEY not set in backend/.env - add it to enable AI answers.")

    try:
        vm = FAISSVectorStoreManager.get_instance()
        print(f"FAISS Vector DB ready (vectors: {vm.get_total_chunks()})")
    except Exception as e:
        print(f"FAISS initialization error: {e}")

    print("All services started. Listening for requests...")
    print("=" * 60)
    yield
    print("Shutting down Study Mate AI backend...")


app = FastAPI(
    title="STUDY MATE AI Backend",
    description="Intelligent AI Study Notes Assistant powered by RAG architecture",
    version="1.0.0",
    lifespan=lifespan
)

# CORS – allow Vite dev server on any port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(summary_router)


@app.get("/")
async def root():
    return {
        "project": "STUDY MATE AI",
        "tagline": "Intelligent AI Study Notes Assistant",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    gemini = GeminiService.get_instance()
    return {
        "status": "healthy",
        "gemini_configured": gemini.is_configured()
    }


@app.get("/api/stats", response_model=StatsResponse)
async def get_dashboard_stats():
    """Real-time dashboard statistics."""
    docs = get_all_documents()
    vm = FAISSVectorStoreManager.get_instance()
    gemini = GeminiService.get_instance()
    return StatsResponse(
        total_documents=len(docs),
        total_chunks=vm.get_total_chunks(),
        vector_index_ready=vm.get_total_chunks() > 0,
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        gemini_model=gemini.model_name
    )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting STUDY MATE AI backend on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
