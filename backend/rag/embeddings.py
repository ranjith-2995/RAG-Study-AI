import os
from typing import List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class LocalSentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible Embeddings wrapper around SentenceTransformer.
    Uses 'all-MiniLM-L6-v2' (fast, lightweight, 384-dimensional dense vectors).
    
    Extends langchain_core.embeddings.Embeddings so that FAISS can use it
    natively via embed_documents() and embed_query().
    Also supports __call__ for backward compatibility with older LangChain builds.
    """
    _instance = None

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model_name = model_name
        print(f"Loading local embedding model: {self.model_name}...")
        self.client = SentenceTransformer(self.model_name)
        print(f"Embedding model '{self.model_name}' loaded successfully.")

    @classmethod
    def get_instance(cls, model_name: str = None):
        """Singleton: load the model once and reuse across the application."""
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document text chunks."""
        if not texts:
            return []
        embeddings = self.client.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        embedding = self.client.encode(text, show_progress_bar=False, normalize_embeddings=True)
        return embedding.tolist()

    def __call__(self, text: str) -> List[float]:
        """Allow the object to be called as a function (required by older LangChain FAISS)."""
        return self.embed_query(text)

