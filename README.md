
# STUDY MATE AI – Intelligent AI Study Notes Assistant

An educational, beginner-friendly **Retrieval-Augmented Generation (RAG)** application designed for students and educators. Upload PDF study materials, textbooks, or lecture slides and interact with an AI chatbot that generates accurate, document-grounded answers with source citations and page numbers.

---

## 🎯 Project Objective

Traditional LLMs can hallucinate facts or lack access to a student's specific course notes and textbooks. **STUDY MATE AI** addresses this using a **Retrieval-Augmented Generation (RAG)** architecture:

1. Processes and indexes uploaded PDF documents into semantic vector representations using local **Sentence Transformers**.
2. Stores vector embeddings in a fast, in-memory and disk-persisted **FAISS** index.
3. Retrieves the most relevant text chunks when a student asks a question and provides them as context to **Google Gemini**.
4. Generates direct answers with citations to the source document and page number.
5. If the answer is not available in the uploaded notes, the assistant states that the information was not found.

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React.js 18
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **Markdown Rendering:** React-Markdown

### Backend
- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **Server:** Uvicorn
- **PDF Processing:** PyPDF
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Database:** FAISS (`faiss-cpu`)
- **Orchestration:** LangChain and LangChain Community
- **LLM:** Google Gemini API (`gemini-3.5-flash-lite`)

---

## 📐 RAG Architecture & Pipeline Workflow

### Document Ingestion

```text
             DOCUMENT INGESTION
                     |
                     v
               Upload PDF File
                     |
                     v
             Text Extraction (PyPDF)
               (Page-by-page text)
                     |
                     v
           Recursive Character Splitting
             (~800 chars, 150 overlap)
                     |
                     v
          Sentence Transformers Embeddings
              (384-dimensional vectors)
                     |
                     v
               FAISS Vector Store
             (Indexed vectors + chunks)
```

### Question Answering

```text
              QUESTION ANSWERING
                     |
                     v
               Student Question
                     |
                     v
             Query Vector Embedding
             (Sentence Transformers)
                     |
                     v
              FAISS Similarity Search
               (Top-K nearest results)
                     |
                     v
          Retrieved Document Excerpts
             (Filename, Page, Snippet)
                     |
                     v
            Strict Grounding Prompt
                  (Gemini)
                     |
                     v
             Grounded Answer
              + Citations
```

---

## 📂 Project Structure

```text
RAG project/
│
├── backend/
│   ├── main.py
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   └── summary.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── text_splitter.py
│   │   ├── vectorstore.py
│   │   └── pipeline.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py
│   │   ├── storage_service.py
│   │   └── gemini_service.py
│   │
│   ├── uploads/
│   │   ├── files/
│   │   └── metadata.json
│   │
│   └── vector_db/
│       ├── faiss_index/
│       └── chunks_store.json
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       │
│       ├── services/
│       │   └── api.js
│       │
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── Header.jsx
│       │   ├── FileUpload.jsx
│       │   ├── ChatInterface.jsx
│       │   ├── DocumentCard.jsx
│       │   └── StatCard.jsx
│       │
│       └── pages/
│           ├── Dashboard.jsx
│           ├── ChatPage.jsx
│           ├── DocumentsPage.jsx
│           └── SummaryPage.jsx
│
├── sample_notes/
│   └── AI_and_Machine_Learning_Study_Notes.pdf
│
└── README.md
```

---

## ⚡ Quick Start & Installation

### Prerequisites

Install the following before running the project:

- **Python:** 3.10, 3.11, or 3.12
- **Node.js:** v18+ or v20+
- **Google Gemini API Key:** Get a free API key from [Google AI Studio](https://aistudio.google.com/).

### Step 1: Configure Backend Environment

Navigate to the backend folder:

```bash
cd backend
```

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `backend/.env` and add your Gemini API key:

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

### Step 2: Install Python Dependencies & Start Backend

From the `backend/` directory:

```bash
pip install -r requirements.txt
python main.py
```

Alternatively, start the server using Uvicorn:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL: `http://127.0.0.1:8000`

Swagger API documentation: `http://127.0.0.1:8000/docs`

### Step 3: Install Frontend Dependencies & Start Frontend

Open a separate terminal and navigate to the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

Open the application in your browser:

```text
http://localhost:5173
```

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service status check |
| GET | `/api/health` | Health check and Gemini API key status |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/documents/upload` | Upload, chunk, embed, and index a PDF |
| GET | `/api/documents` | List uploaded documents |
| GET | `/api/documents/{doc_id}` | Get specific document metadata |
| DELETE | `/api/documents/{doc_id}` | Delete a document and its vectors |
| POST | `/api/chat` | Ask questions and receive grounded answers |
| POST | `/api/summary` | Generate study summaries and review points |

### Sample Chat Request

**POST `/api/chat`**

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
  "answer": "Based on the provided document, the scaled dot-product attention formula is ...",
  "sources": [
    {
      "doc_id": "9a38c-...",
      "filename": "AI_and_Machine_Learning_Study_Notes.pdf",
      "page": 2,
      "chunk_id": "9a38c_p2_c1",
      "snippet": "Introduced in Attention Is All You Need...",
      "score": 0.42
    }
  ],
  "found_in_docs": true
}
```

---

## 🧪 Testing the RAG Workflow

A sample study notes document is included:

`sample_notes/AI_and_Machine_Learning_Study_Notes.pdf`

### Test Steps

1. **Upload:** Open the Dashboard or Study Materials page and upload the sample PDF.
2. **Observe Ingestion:** The system extracts text page by page, splits it into chunks, generates embeddings, and creates the FAISS index.
3. **Ask In-Scope Questions:**
   - "What are the three paradigms of machine learning?"
   - "Explain the scaled dot-product attention formula."
   - "Why is RAG used to prevent hallucinations in LLMs?"
4. **Ask Out-of-Scope Questions:**
   - "Who won the 2022 FIFA World Cup?"
   - "How do I bake a chocolate cake?"
   
   The assistant should indicate that relevant information was not found in the uploaded documents.
5. **AI Summarizer:** Navigate to AI Summaries and click Generate AI Summary to receive a structured overview with key topics and review highlights.
6. **Document Deletion:** Delete a document from Study Materials and verify that its file and corresponding FAISS vectors are removed.

---

## 🛡️ Anti-Hallucination & Security Features

- **Strict System Prompt:** Low temperature (0.2) and prompt instructions guide Gemini to use only retrieved context.
- **Source Transparency:** Answers include citations with document names, page numbers, and relevant excerpts.
- **Frontend Key Security:** API keys are stored on the backend in `backend/.env` and are not exposed to the frontend.
- **Clean Vector Management:** Deleted documents have their associated chunks removed from FAISS to prevent irrelevant retrievals.

---

## 📜 License

This project is open-source and intended for educational and personal study use.

---

## 🎓 Academic Use

STUDY MATE AI is designed as an educational project to demonstrate the practical implementation of Retrieval-Augmented Generation using document processing, semantic embeddings, vector search, and large language models.

