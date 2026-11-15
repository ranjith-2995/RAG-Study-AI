import os
import warnings
from typing import Dict, Any, List, Optional

# Suppress the deprecation noise for end-users
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_FILE)

class GeminiService:
    """
    Manages interaction with the Google Gemini API for:
    - Context-grounded Question Answering (strict anti-hallucination).
    - Document Summarization & Key Topics extraction.
    
    Uses the modern `google-genai` SDK (google.genai).
    Falls back gracefully when no API key is configured.
    """
    _instance = None

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        self._client = None
        self._is_configured = False
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key in ("your_gemini_api_key_here", ""):
            print("Notice: GEMINI_API_KEY is not set. Add it to backend/.env to enable AI generation.")
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._is_configured = True
            print(f"Gemini API configured successfully with model: {self.model_name}")
        except Exception as e:
            print(f"Warning: Failed to configure Gemini API: {e}")
            self._is_configured = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload_config(self) -> bool:
        """Reload API key and reinitialize client (e.g. after user edits .env)."""
        load_dotenv(ENV_FILE, override=True)
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        self._client = None
        self._is_configured = False
        self._init_client()
        return self._is_configured

    def is_configured(self) -> bool:
        return self._is_configured

    def _generate(self, prompt: str, max_tokens: int = 1200) -> Optional[str]:
        """
        Internal wrapper to call Gemini and return the text response.
        Tries multiple model names with graceful fallback.
        """
        if not self._is_configured:
            if not self.reload_config():
                return None

        models_to_try = list(dict.fromkeys([
            self.model_name,
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
        ]))

        from google import genai
        from google.genai import types

        for model in models_to_try:
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=max_tokens,
                    )
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as ex:
                print(f"Model '{model}' failed: {ex}")
                continue

        return None

    # ---------------------------------------------------------------- RAG Q&A --
    def generate_rag_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates an answer based STRICTLY on retrieved document chunks.
        Returns {"answer": str, "found_in_docs": bool}
        """
        if not self._is_configured:
            if not self.reload_config():
                return {
                    "answer": (
                        "⚠️ **Gemini API Key Required**\n\n"
                        "To generate answers, please provide your Google Gemini API key:\n"
                        "1. Open `backend/.env`\n"
                        "2. Set `GEMINI_API_KEY=your_actual_api_key`\n"
                        "3. Save the file and restart the backend server.\n\n"
                        "Get a **free** API key at [Google AI Studio](https://aistudio.google.com/)."
                    ),
                    "found_in_docs": False
                }

        # Build context from retrieved chunks
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            meta = chunk.get("metadata", {})
            filename = meta.get("filename", "Unknown Document")
            page = meta.get("page", 1)
            text = chunk.get("text", "")
            context_blocks.append(
                f"--- [Excerpt {i} | Document: {filename} | Page: {page}] ---\n{text}"
            )

        context_str = "\n\n".join(context_blocks)

        prompt = f"""You are STUDY MATE AI, an intelligent, helpful, and precise study notes assistant for students.

Your task is to answer the student's question accurately and objectively using ONLY the provided document excerpts below.

=== UPLOADED DOCUMENT CONTEXT ===
{context_str}
=== END CONTEXT ===

STUDENT QUESTION:
{question}

CRITICAL RULES:
1. GROUNDING: Answer ONLY based on the facts provided in the excerpts above.
2. ANTI-HALLUCINATION: If the context does not contain the answer, respond with EXACTLY:
   "I could not find relevant information in the uploaded study documents to answer this question. Please ensure the topic is covered in your uploaded PDFs."
3. CITATIONS: When citing facts, clearly mention the source document name and page number, e.g. [Document: Biology_Notes.pdf, Page: 4].
4. FORMATTING: Use markdown, bullet points, and bold text to structure the answer clearly for student studying.
5. TONE: Encouraging, academic, concise, and well-structured.
"""

        answer_text = self._generate(prompt, max_tokens=1200)

        if not answer_text:
            return {
                "answer": "Failed to generate answer. Please check your Gemini API key and network connection.",
                "found_in_docs": False
            }

        not_found_indicators = [
            "i could not find relevant information",
            "not found in the uploaded",
            "does not contain information",
            "no relevant information",
        ]
        found_in_docs = not any(ind in answer_text.lower() for ind in not_found_indicators)

        return {"answer": answer_text, "found_in_docs": found_in_docs}

    # ------------------------------------------------------------ Summarizer --
    def generate_summary(self, document_text: str, filename: str) -> Dict[str, Any]:
        """
        Generates a structured study summary, core topics, and flashcard points.
        """
        if not self._is_configured:
            if not self.reload_config():
                return {
                    "summary": "Gemini API key is required to generate summaries. Please set GEMINI_API_KEY in backend/.env.",
                    "key_topics": ["Configuration Needed"],
                    "study_points": ["Add your Gemini API key in backend/.env to generate AI summaries."]
                }

        # Limit input to avoid token overflow
        truncated_text = document_text[:18000]

        prompt = f"""You are STUDY MATE AI, an expert educational tutor.
Generate a structured study summary for the document: "{filename}".

DOCUMENT TEXT:
{truncated_text}

Provide your response in EXACTLY the following structured format:

### OVERVIEW
[Write a concise 2-3 paragraph high-level overview explaining what this document is about and its primary purpose.]

### KEY TOPICS
- Topic 1: [Short explanation]
- Topic 2: [Short explanation]
- Topic 3: [Short explanation]
- Topic 4: [Short explanation]
- Topic 5: [Short explanation]

### ESSENTIAL STUDY POINTS
- [Key point 1]
- [Key point 2]
- [Key point 3]
- [Key point 4]
- [Key point 5]
"""

        raw_output = self._generate(prompt, max_tokens=1500)

        if not raw_output:
            return {
                "summary": "Could not generate summary. Please check your Gemini API key and network connection.",
                "key_topics": ["Error"],
                "study_points": ["Check backend logs for details."]
            }

        # Parse the structured response
        topics: List[str] = []
        study_points: List[str] = []
        summary_lines: List[str] = []
        current_section = "overview"

        for line in raw_output.splitlines():
            clean_line = line.strip()
            upper = clean_line.upper()
            if "### KEY TOPICS" in upper:
                current_section = "topics"
                continue
            elif "### ESSENTIAL STUDY POINTS" in upper or "### STUDY POINTS" in upper:
                current_section = "study_points"
                continue
            elif "### OVERVIEW" in upper:
                current_section = "overview"
                continue

            if current_section == "topics" and clean_line.startswith(("-", "*", "•")):
                topics.append(clean_line.lstrip("-*• ").strip())
            elif current_section == "study_points" and clean_line.startswith(("-", "*", "•")):
                study_points.append(clean_line.lstrip("-*• ").strip())
            elif current_section == "overview" and clean_line:
                summary_lines.append(clean_line)

        overview_text = "\n\n".join(summary_lines) if summary_lines else raw_output
        if not topics:
            topics = ["Main Concepts", "Key Theories", "Practical Applications"]
        if not study_points:
            study_points = ["Review foundational definitions", "Understand key concepts"]

        return {
            "summary": overview_text,
            "key_topics": topics[:8],
            "study_points": study_points[:8]
        }
