
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
- **Framework**: React.js 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (Professional Blue & White SaaS theme)
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown Rendering**: React-Markdown
- **Mind Maps & Charts**: Interactive React concept graph and responsive progress visualizations
- **Text-to-Speech**: Browser Web Speech API (available voices depend on the device)

### Backend
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Server**: Uvicorn
- **PDF Processing**: PyPDF
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database**: FAISS (`faiss-cpu`)
- **Orchestration**: LangChain & LangChain Community
- **LLM**: Google Gemini API (`gemini-3.5-flash-lite`)
- **Learning Data**: SQLite for quizzes/attempts, flashcards, plans, and study time

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
│   │   ├── documents.py            # Upload, list, and delete documents
│   │   ├── chat.py                 # RAG Question-Answering endpoint
│   │   ├── summary.py              # AI study notes summary generator
│   │   └── learning.py             # Quizzes, flashcards, mind maps, plans, analytics
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── text_splitter.py
│   │   ├── vectorstore.py
│   │   └── pipeline.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py          # PyPDF text extraction
│   │   ├── storage_service.py      # JSON metadata persistence
│   │   ├── gemini_service.py       # Google Gemini LLM caller with anti-hallucination prompt
│   │   └── learning_service.py     # Grounded study generation and SQLite persistence
│   ├── study_mate.sqlite3          # Quiz history, saved cards, plans, and study time
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
| `GET` | `/` | Service status check |
| `GET` | `/api/health` | Health check & Gemini API key status |
| `GET` | `/api/stats` | Dashboard statistics (total docs, chunks, models) |
| `POST` | `/api/documents/upload` | Upload a PDF, chunk text, embed, and index in FAISS |
| `GET` | `/api/documents` | List all uploaded documents with metadata |
| `GET` | `/api/documents/{doc_id}` | Get metadata for a specific document |
| `DELETE` | `/api/documents/{doc_id}` | Delete document file, metadata, and remove vectors from FAISS |
| `POST` | `/api/chat` | Send a question; accepts optional language/history and returns grounded answer with page citations |
| `POST` | `/api/summary` | Generate study overview, key topics, and review points (`language`: English or Tamil) |
| `GET` | `/api/documents/{doc_id}/file` | Open the original PDF; citation links target the cited page |
| `POST` | `/api/learning/quizzes` | Generate a 1–10 question quiz for a document and difficulty |
| `POST` | `/api/learning/quizzes/{quiz_id}/submit` | Score answers, return explanations, and persist the attempt |
| `GET` | `/api/learning/quizzes` | List completed quiz attempts |
| `POST` | `/api/learning/flashcards` | Generate and persist 1–20 document-grounded flashcards |
| `GET` | `/api/learning/flashcards?doc_id={id}` | List saved revision cards (optionally filtered by document) |
| `PATCH` | `/api/learning/flashcards/{card_id}` | Save an Easy, Medium, or Hard card rating |
| `POST` | `/api/learning/mindmap` | Generate topics, subtopics, and concept relationships |
| `POST` | `/api/learning/planner` | Create and persist a topic-based plan for a stated goal |
| `GET` | `/api/learning/planner` | Read the latest saved plan |
| `PATCH` | `/api/learning/planner/topics/{topic_id}` | Update a plan topic's completion state |
| `GET` | `/api/learning/analytics` | Quiz scores, weak topics, study time, card count, and plan progress |
| `POST` | `/api/learning/analytics/study-time` | Add active study seconds to persistent analytics |

### Sample Chat Request (`POST /api/chat`)
```json
{
  "question": "What is the scaled dot-product attention formula?",
  "selected_doc_id": null
}
```

### Learning API examples

Generate a quiz from one indexed PDF:

```json
POST /api/learning/quizzes
{
  "doc_id": "document-uuid",
  "difficulty": "Medium",
  "count": 5
}
```

Submit the selected option index for each question (indexes are zero-based):

```json
POST /api/learning/quizzes/{quiz_id}/submit
{
  "answers": {"0": 2, "1": 0, "2": 1}
}
```

Create a study plan:

```json
POST /api/learning/planner
{
  "doc_id": "document-uuid",
  "goal": "Review the main topics before Friday's exam"
}
```

Learning-generation endpoints retrieve document-scoped FAISS matches and return source passage metadata. They return an error when the document has no indexed text or Gemini is not configured; they do not substitute hardcoded quiz or topic content. Quiz answer keys remain server-side until submission. SQLite is initialized automatically at `backend/study_mate.sqlite3`; remove a PDF through the documents API to remove its associated quizzes, attempts, flashcards, and plans as well as its FAISS vectors.

## ✨ Learning features

- **AI quizzes:** Easy, Medium, and Hard multiple-choice quizzes use four options per question. Submissions are scored by the backend, which returns the correct answer and explanation and records topic-level results.
- **Smart flashcards:** Generate and persist question/answer cards, flip them to reveal the answer, and save an Easy, Medium, or Hard review rating. Cards retain their source filename and page.
- **Interactive mind maps:** Generate a central concept with related branches and subtopics from retrieved passages. Branches expand interactively and show source passages.
- **Read-aloud summaries:** Generate summaries in English or Tamil, then use browser speech synthesis to play, pause/resume, or stop them and select playback speed. Actual Tamil voice availability depends on the browser and operating system.
- **Progress analytics:** See quiz history and scores, weak topics from topic-level answers, saved cards, study time, and study-plan completion.
- **Study planner:** Set a goal, generate a topic-based revision schedule, and persist completion state per topic.
- **Multilingual grounded chat:** Select English or Tamil; follow-up history is stored in the browser and included in retrieval context. Tamil explanations use simple Tamil and retain technical terms where useful.
- **Source review:** Chat and learning tools show retrieved document excerpts and original page numbers. Source links open the stored PDF on that page, and chat highlights question terms in citations.
- **Responsive workspace and dark mode:** Sidebar navigation exposes each study feature, and the theme choice persists in the browser.

### Learning data and privacy

Quiz questions and answer keys, quiz attempts, flashcards and ratings, study plans, and active study seconds are stored locally in SQLite. Document metadata and vector chunks remain in the existing local stores. No Gemini key is sent to the frontend. The application currently has no user accounts or multi-user access controls; run it only in a trusted, local environment unless authentication and deployment hardening are added.

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
7. **Learning tools**: Open **AI Quizzes**, generate a quiz at each difficulty, submit answers, and review explanations. Generate flashcards and rate them, expand mind-map branches, then create and complete a study plan.
8. **Analytics and speech**: Complete a quiz and mark a study-plan topic complete to populate **Analytics**. Generate a Tamil summary and use the read-aloud controls; available voices depend on the browser and OS.
9. **Citation review**: Ask a question in Chat, expand its sources, inspect the highlighted retrieved excerpt, and open the original cited PDF page.

---

## 🛡️ Anti-Hallucination & Security Features

- **Strict System Prompt**: Low temperature (0.2) and prompt engineering instruct Gemini to strictly cite and only use the retrieved context chunks.
- **Source Transparency**: Every answer includes an expandable citations panel displaying the exact page numbers and excerpts used to formulate the answer. Generated page citations are checked against retrieved chunk metadata; unsupported citations are removed.
- **Frontend Key Security**: API keys are strictly stored on the server side (`backend/.env`) and never exposed to the client.
- **Clean Vector Management**: When a document is deleted, its chunks are purged from FAISS, preventing ghost retrievals.

---

## 📜 License

This project is open-source and intended for educational and personal study use.

---

## 🎓 Academic Use

STUDY MATE AI is designed as an educational project to demonstrate the practical implementation of Retrieval-Augmented Generation using document processing, semantic embeddings, vector search, and large language models.

