# STUDY MATE AI – Intelligent AI Study Notes Assistant

An educational, beginner-friendly **Retrieval-Augmented Generation (RAG)** application designed for students and educators. Upload PDF study materials, textbooks, or lecture slides, and interact with a modern AI chatbot that generates accurate, grounded answers strictly derived from the uploaded documents—complete with source citations and page numbers.

---

## 🎯 Project Objective

Traditional LLMs often hallucinate facts or lack access to a student's specific course notes and textbooks. **STUDY MATE AI** solves this problem by using a **Retrieval-Augmented Generation (RAG)** architecture:
1. It processes and indexes uploaded PDF documents into semantic vector representations using local **Sentence Transformers**.
2. It stores vector embeddings in a fast, in-memory & disk-persisted **FAISS** index.
3. When a student asks a question, it retrieves only the most relevant text chunks and provides them as context to **Google Gemini**.
4. Gemini synthesizes a direct answer citing the exact source document and page number. If the answer is not present in the notes, it honestly states that the information was not found.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React.js 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (Professional Blue & White SaaS theme)
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown Rendering**: React-Markdown

### Backend
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Server**: Uvicorn
- **PDF Processing**: PyPDF
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database**: FAISS (`faiss-cpu`)
- **Orchestration**: LangChain & LangChain Community
- **LLM**: Google Gemini API (`gemini-3.5-flash-lite`)

---

## 📐 RAG Architecture & Pipeline Workflow

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                       DOCUMENT INGESTION                        │
   └─────────────────────────────────────────────────────────────────┘
                                   │
                           [Upload PDF File]
                                   │
                                   ▼
                    [Text Extraction via PyPDF]
                        (Page-by-page text)
                                   │
                                   ▼
                    [Recursive Character Splitting]
                   (~800 chars, 150 overlap + metadata)
                                   │
                                   ▼
                   [Sentence Transformers Embeddings]
                    (Dense 384-dimensional vectors)
                                   │
                                   ▼
                      [FAISS Vector Store (Disk)]
                     (Indexed vectors + chunk store)

   ┌─────────────────────────────────────────────────────────────────┐
   │                       QUESTION ANSWERING                        │
   └─────────────────────────────────────────────────────────────────┘
                                   │
                          [Student Question]
                                   │
                                   ▼
                       [Query Vector Embedding]
                    (Local Sentence Transformers)
                                   │
                                   ▼
                      [FAISS Similarity Search]
                       (Top-K nearest neighbors)
                                   │
                                   ▼
                   [Retrieved Document Excerpts & Citations]
                         (Filename, Page, Snippet)
                                   │
                                   ▼
                   [Strict Grounding Prompt to Gemini]
                    (Answers strictly based on context)
                                   │
                                   ▼
                     [Grounded Answer + Citations]
```

---

## 📂 Project Structure

```
RAG project/
├── backend/
│   ├── main.py                     # FastAPI server entry point & CORS configuration
│   ├── .env.example                # Example environment configuration
│   ├── .env                        # Active environment variables (API keys)
│   ├── requirements.txt            # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic models for requests and responses
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py            # Upload, list, and delete documents
│   │   ├── chat.py                 # RAG Question-Answering endpoint
│   │   └── summary.py              # AI study notes summary generator
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py           # Sentence Transformers embedding wrapper
│   │   ├── text_splitter.py        # Chunking with page and document metadata
│   │   ├── vectorstore.py          # FAISS index manager with disk persistence
│   │   └── pipeline.py             # RAG retrieval and synthesis orchestrator
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py          # PyPDF text extraction
│   │   ├── storage_service.py      # JSON metadata persistence
│   │   └── gemini_service.py       # Google Gemini LLM caller with anti-hallucination prompt
│   ├── uploads/
│   │   ├── files/                  # Stored PDF files
│   │   └── metadata.json           # Document registry
│   └── vector_db/
│       ├── faiss_index/            # FAISS binary index
│       └── chunks_store.json       # Indexed chunk repository
├── frontend/
│   ├── package.json                # Frontend dependencies and scripts
│   ├── vite.config.js              # Vite bundler configuration
│   ├── tailwind.config.js          # Tailwind CSS styling configuration
│   ├── postcss.config.js           # PostCSS configuration
│   ├── index.html                  # HTML entry point
│   └── src/
│       ├── main.jsx                # React root mount
│       ├── App.jsx                 # Main layout & state coordination
│       ├── index.css               # Global Tailwind directives and custom scrollbar
│       ├── services/
│       │   └── api.js              # Axios API client functions
│       ├── components/
│       │   ├── Sidebar.jsx         # Navigation sidebar with RAG architecture specs
│       │   ├── Header.jsx          # Top bar with Gemini status indicator
│       │   ├── FileUpload.jsx      # Drag-and-drop PDF upload with progress animation
│       │   ├── ChatInterface.jsx   # ChatGPT-like chat with citations and history
│       │   ├── DocumentCard.jsx    # Document card with stats and actions
│       │   └── StatCard.jsx        # Attractive KPI cards
│       └── pages/
│           ├── Dashboard.jsx       # Overview, workflow diagram, quick actions
│           ├── ChatPage.jsx        # Dedicated AI Q&A assistant page
│           ├── DocumentsPage.jsx   # Document library management & deletion
│           └── SummaryPage.jsx     # AI study notes & flashcards summarizer
├── sample_notes/
│   └── AI_and_Machine_Learning_Study_Notes.pdf # Sample PDF for immediate testing
└── README.md                       # Comprehensive project documentation
```

---

## ⚡ Quick Start & Installation

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12 installed.
- **Node.js**: v18+ or v20+ installed.
- **Google Gemini API Key**: Free API key from [Google AI Studio](https://aistudio.google.com/).

---

### Step 1: Configure Backend Environment

1. Navigate to the `backend/` folder:
   ```bash
   cd backend
   ```
2. Copy the template `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `backend/.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   CHUNK_SIZE=800
   CHUNK_OVERLAP=150
   TOP_K_RESULTS=4
   HOST=127.0.0.1
   PORT=8000
   ```

---

### Step 2: Install Python Dependencies & Start Backend

In the `backend/` directory:
```bash
pip install -r requirements.txt
python main.py
```
*Or using uvicorn directly:*
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
The backend server will start at `http://127.0.0.1:8000`. You can inspect the interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

---

### Step 3: Install Frontend Dependencies & Start Frontend

In a separate terminal window, navigate to the `frontend/` directory:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173` to access the application.

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service status check |
| `GET` | `/api/health` | Health check & Gemini API key status |
| `GET` | `/api/stats` | Dashboard statistics (total docs, chunks, models) |
| `POST` | `/api/documents/upload` | Upload a PDF, chunk text, embed, and index in FAISS |
| `GET` | `/api/documents` | List all uploaded documents with metadata |
| `GET` | `/api/documents/{doc_id}` | Get metadata for a specific document |
| `DELETE` | `/api/documents/{doc_id}` | Delete document file, metadata, and remove vectors from FAISS |
| `POST` | `/api/chat` | Send a question; performs similarity search and returns grounded answer with page citations |
| `POST` | `/api/summary` | Generate study overview, key topics, and review points |

### Sample Chat Request (`POST /api/chat`)
```json
{
  "question": "What is the scaled dot-product attention formula?",
  "selected_doc_id": null
}
```

### Sample Chat Response
```json
{
  "question": "What is the scaled dot-product attention formula?",
  "answer": "Based on the provided document [AI_and_Machine_Learning_Study_Notes.pdf, Page: 2], the scaled dot-product attention formula is mathematically defined as:\n\n$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$\n\nDividing by $\\sqrt{d_k}$ prevents large dot products from pushing the softmax function into regions with extremely small gradients.",
  "sources": [
    {
      "doc_id": "9a38c-...",
      "filename": "AI_and_Machine_Learning_Study_Notes.pdf",
      "page": 2,
      "chunk_id": "9a38c_p2_c1",
      "snippet": "Introduced in 'Attention Is All You Need' (Vaswani et al., 2017), the Transformer architecture...",
      "score": 0.42
    }
  ],
  "found_in_docs": true
}
```

---

## 🧪 Testing the RAG Workflow

A pre-generated sample study notes document is included in the project:
`sample_notes/AI_and_Machine_Learning_Study_Notes.pdf`

### Test Steps:
1. **Upload**: Go to the **Dashboard** or **Study Materials** page and upload `sample_notes/AI_and_Machine_Learning_Study_Notes.pdf`.
2. **Observe Ingestion**: The system extracts pages 1, 2, and 3, splits them into semantic chunks, generates embeddings with Sentence Transformers, and creates the FAISS index.
3. **Ask In-Scope Questions**:
   - *"What are the three paradigms of machine learning?"*
   - *"Explain the scaled dot-product attention formula."*
   - *"Why is RAG used to prevent hallucinations in LLMs?"*
   Notice that the assistant answers accurately and lists the exact source file and page numbers.
4. **Ask Out-of-Scope Questions (Anti-Hallucination Test)**:
   - *"Who won the 2022 FIFA World Cup?"*
   - *"How do I bake a chocolate cake?"*
   Notice that the assistant adheres to the strict anti-hallucination constraint and replies:
   *"I could not find relevant information in the uploaded study documents to answer this question. Please ensure the topic is covered in your uploaded PDFs."*
5. **AI Summarizer**:
   Navigate to the **AI Summaries** tab and click **Generate AI Summary** to receive a structured overview with key topics and review flashcard highlights.
6. **Document Deletion**:
   Navigate to **Study Materials** and delete a document. The document file is removed from disk and its vector embeddings are pruned from FAISS, updating the dashboard statistics in real time.

---

## 🛡️ Anti-Hallucination & Security Features

- **Strict System Prompt**: Low temperature (0.2) and prompt engineering instruct Gemini to strictly cite and only use the retrieved context chunks.
- **Source Transparency**: Every answer includes an expandable citations panel displaying the exact page numbers and excerpts used to formulate the answer.
- **Frontend Key Security**: API keys are strictly stored on the server side (`backend/.env`) and never exposed to the client.
- **Clean Vector Management**: When a document is deleted, its chunks are purged from FAISS, preventing ghost retrievals.

---

## 📜 License

This project is open-source and intended for educational and personal study use.

#   R A G - S t u d y - A I  
 