import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from backend.rag.vectorstore import FAISSVectorStoreManager
from backend.services.gemini_service import GeminiService
from backend.services.storage_service import get_document


DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "study_mate.sqlite3")


class LearningService:
    """Generates study tools from indexed PDF passages and persists learning activity."""

    def __init__(self) -> None:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS quizzes (
                    id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, difficulty TEXT NOT NULL,
                    questions_json TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id TEXT PRIMARY KEY, quiz_id TEXT NOT NULL, score INTEGER NOT NULL,
                    total INTEGER NOT NULL, answers_json TEXT NOT NULL,
                    topic_scores_json TEXT NOT NULL, completed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS flashcards (
                    id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, question TEXT NOT NULL,
                    answer TEXT NOT NULL, topic TEXT NOT NULL, source_json TEXT NOT NULL,
                    rating TEXT, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS study_plans (
                    id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, goal TEXT NOT NULL,
                    topics_json TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS study_time (
                    id INTEGER PRIMARY KEY CHECK(id = 1), seconds INTEGER NOT NULL DEFAULT 0
                );
                INSERT OR IGNORE INTO study_time(id, seconds) VALUES(1, 0);
                """
            )

    def _context(self, doc_id: str, query: str, top_k: int = 10) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if not get_document(doc_id):
            raise LookupError("Document not found.")
        results = FAISSVectorStoreManager.get_instance().search(query, top_k=top_k, doc_id=doc_id)
        chunks = []
        sources = []
        for document, distance in results:
            text = document.page_content.strip()
            metadata = document.metadata
            if not text or not metadata.get("page") or not metadata.get("filename"):
                continue
            chunks.append({"text": text, "metadata": metadata})
            sources.append({
                "doc_id": doc_id,
                "filename": metadata["filename"],
                "page": int(metadata["page"]),
                "chunk_id": metadata.get("chunk_id", ""),
                "snippet": text[:700],
                "score": float(distance),
            })
        if not chunks:
            raise ValueError("No indexed, citable text was found for this document.")
        return chunks, sources

    def _generate_json(self, task: str, chunks: list[dict[str, Any]], max_tokens: int = 3000) -> dict[str, Any]:
        context = "\n\n".join(
            f"[Source: {item['metadata']['filename']}, page {item['metadata']['page']}, "
            f"chunk {item['metadata'].get('chunk_id', '')}]\n{item['text']}"
            for item in chunks
        )
        raw = GeminiService.get_instance().generate_structured(task, context, max_tokens=max_tokens)
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            raise ValueError("The AI did not return valid structured study content. Please try again.")
        try:
            value = json.loads(raw[start:end + 1])
        except json.JSONDecodeError as error:
            raise ValueError("The AI returned malformed study content. Please try again.") from error
        if not isinstance(value, dict):
            raise ValueError("The AI response has an unexpected format.")
        return value

    def generate_quiz(self, doc_id: str, difficulty: str, count: int) -> dict[str, Any]:
        if difficulty not in {"Easy", "Medium", "Hard"}:
            raise ValueError("Difficulty must be Easy, Medium, or Hard.")
        chunks, sources = self._context(doc_id, f"Key facts, definitions, and concepts for a {difficulty} difficulty study quiz", 12)
        generated = self._generate_json(
            f"""Create exactly {count} original multiple-choice study questions at {difficulty} difficulty from the supplied passages only.
Return JSON with a "questions" array. Each item must have "question", "options" (exactly four distinct strings),
"correct_index" (integer 0-3), "explanation", and "topic". Do not add facts absent from the passages.
Make distractors plausible but clearly incorrect. Avoid duplicate questions.""",
            chunks,
        )
        questions = generated.get("questions")
        if not isinstance(questions, list) or len(questions) != count:
            raise ValueError("The AI could not produce the requested number of quiz questions from this document.")
        for question in questions:
            if (not isinstance(question, dict) or not isinstance(question.get("question"), str)
                    or not question["question"].strip()
                    or not isinstance(question.get("options"), list) or len(question["options"]) != 4
                    or not all(isinstance(option, str) and option.strip() for option in question["options"])
                    or len({option.strip().casefold() for option in question["options"]}) != 4
                    or type(question.get("correct_index")) is not int
                    or question["correct_index"] not in range(4)
                    or not isinstance(question.get("explanation"), str) or not question["explanation"].strip()
                    or not isinstance(question.get("topic"), str) or not question["topic"].strip()):
                raise ValueError("The AI returned a quiz question with invalid fields. Please try again.")
        quiz_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO quizzes VALUES (?, ?, ?, ?, ?)",
                (quiz_id, doc_id, difficulty, json.dumps(questions), created_at),
            )
        public_questions = [{key: value for key, value in item.items() if key != "correct_index"} for item in questions]
        return {"id": quiz_id, "doc_id": doc_id, "difficulty": difficulty, "questions": public_questions, "sources": sources}

    def submit_quiz(self, quiz_id: str, answers: dict[str, int]) -> dict[str, Any]:
        with self._connect() as connection:
            quiz = connection.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
            if not quiz:
                raise LookupError("Quiz not found.")
            questions = json.loads(quiz["questions_json"])
            if any(not key.isdigit() or int(key) >= len(questions) or value not in range(4) for key, value in answers.items()):
                raise ValueError("Quiz answers must use valid question and option indexes.")
            score = 0
            review = []
            topic_scores: dict[str, dict[str, int]] = {}
            for index, item in enumerate(questions):
                selected = answers.get(str(index))
                correct = selected == item["correct_index"]
                score += int(correct)
                topic = item["topic"]
                topic_scores.setdefault(topic, {"correct": 0, "total": 0})
                topic_scores[topic]["correct"] += int(correct)
                topic_scores[topic]["total"] += 1
                review.append({
                    "question": item["question"], "options": item["options"],
                    "selected_index": selected, "correct_index": item["correct_index"],
                    "correct": correct, "explanation": item["explanation"], "topic": topic,
                })
            attempt_id = str(uuid.uuid4())
            completed_at = datetime.now(timezone.utc).isoformat()
            connection.execute(
                "INSERT INTO quiz_attempts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (attempt_id, quiz_id, score, len(questions), json.dumps(answers),
                 json.dumps(topic_scores), completed_at),
            )
        return {"id": attempt_id, "quiz_id": quiz_id, "score": score, "total": len(questions), "review": review, "completed_at": completed_at}

    def generate_flashcards(self, doc_id: str, count: int) -> dict[str, Any]:
        chunks, sources = self._context(doc_id, "Important concepts, definitions, and explanations for study flashcards", 12)
        generated = self._generate_json(
            f"""Create exactly {count} concise study flashcards grounded in the passages.
Return JSON with a "flashcards" array of objects containing "question", "answer", "topic", and "source_chunk_id".
"source_chunk_id" must exactly match the chunk identifier in the source heading for the passage supporting this card.
Do not add facts absent from the passages.""",
            chunks,
        )
        cards = generated.get("flashcards")
        if not isinstance(cards, list) or len(cards) != count:
            raise ValueError("The AI could not produce the requested flashcards from this document.")
        source_by_chunk = {str(item["metadata"].get("chunk_id", "")): item for item in chunks}
        for card in cards:
            if (not isinstance(card, dict)
                    or not all(isinstance(card.get(key), str) and card[key].strip() for key in ("question", "answer", "topic"))
                    or not isinstance(card.get("source_chunk_id"), str)
                    or not card["source_chunk_id"].strip()
                    or card["source_chunk_id"] not in source_by_chunk):
                raise ValueError("The AI returned an invalid flashcard. Please try again.")
        saved = []
        with self._connect() as connection:
            for card in cards:
                source_chunk = source_by_chunk[card["source_chunk_id"]]
                metadata = source_chunk["metadata"]
                card_id = str(uuid.uuid4())
                source = {
                    "filename": metadata["filename"], "page": int(metadata["page"]),
                    "snippet": source_chunk["text"][:700],
                }
                connection.execute(
                    "INSERT INTO flashcards VALUES (?, ?, ?, ?, ?, ?, NULL, ?)",
                    (card_id, doc_id, card["question"], card["answer"], card["topic"],
                     json.dumps(source), datetime.now(timezone.utc).isoformat()),
                )
                saved.append({
                    "id": card_id,
                    **{key: value for key, value in card.items() if key != "source_chunk_id"},
                    "source": source,
                    "rating": None,
                })
        return {"flashcards": saved, "sources": sources}

    def list_flashcards(self, doc_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as connection:
            query = "SELECT * FROM flashcards"
            args: tuple[Any, ...] = ()
            if doc_id:
                query += " WHERE doc_id = ?"
                args = (doc_id,)
            rows = connection.execute(query + " ORDER BY created_at DESC", args).fetchall()
        return [{
            "id": row["id"], "doc_id": row["doc_id"], "question": row["question"],
            "answer": row["answer"], "topic": row["topic"], "rating": row["rating"],
            "source": json.loads(row["source_json"]), "created_at": row["created_at"],
        } for row in rows]

    def rate_flashcard(self, card_id: str, rating: str) -> dict[str, Any]:
        if rating not in {"Easy", "Medium", "Hard"}:
            raise ValueError("Rating must be Easy, Medium, or Hard.")
        with self._connect() as connection:
            result = connection.execute("UPDATE flashcards SET rating = ? WHERE id = ?", (rating, card_id))
            if not result.rowcount:
                raise LookupError("Flashcard not found.")
        return {"id": card_id, "rating": rating}

    def generate_mindmap(self, doc_id: str) -> dict[str, Any]:
        chunks, sources = self._context(doc_id, "Main topics, subtopics, and relationships between concepts", 12)
        generated = self._generate_json(
            """Extract a mind map from the provided passages. Return JSON with "topic" as the central topic
and "branches" as an array of objects with "name", "relationship", and "children" (an array of strings).
Use only topics and relationships supported by the text.""",
            chunks,
        )
        if (not isinstance(generated.get("topic"), str) or not generated["topic"].strip()
                or not isinstance(generated.get("branches"), list) or not generated["branches"]):
            raise ValueError("The AI could not create a valid mind map from this document.")
        for branch in generated["branches"]:
            if (not isinstance(branch, dict)
                    or not isinstance(branch.get("name"), str) or not branch["name"].strip()
                    or not isinstance(branch.get("children"), list)
                    or not all(isinstance(child, str) and child.strip() for child in branch["children"])
                    or not isinstance(branch.get("relationship", ""), str)):
                raise ValueError("The AI returned an invalid mind map structure.")
        return {"doc_id": doc_id, "topic": generated["topic"], "branches": generated["branches"], "sources": sources}

    def generate_plan(self, doc_id: str, goal: str) -> dict[str, Any]:
        chunks, sources = self._context(doc_id, "Document topics, chapter headings, and concepts to study", 12)
        today = datetime.now(timezone.utc).date().isoformat()
        generated = self._generate_json(
            f"""Create a realistic revision schedule beginning on {today} for this study goal: {goal!r}.
Return JSON with "topics" as an ordered array of objects containing "title", "day" (YYYY-MM-DD, beginning on {today}),
"duration_minutes" (integer), and "reason". Use only topics present in the passages.""",
            chunks,
        )
        topics = generated.get("topics")
        if not isinstance(topics, list) or not topics:
            raise ValueError("The AI did not return a study plan for the selected document.")
        normalized = []
        for topic in topics:
            if (not isinstance(topic, dict)
                    or not all(isinstance(topic.get(key), str) and topic[key].strip() for key in ("title", "day", "reason"))):
                raise ValueError("The AI returned an invalid study plan topic.")
            try:
                topic_day = datetime.strptime(topic["day"], "%Y-%m-%d").date()
            except ValueError as error:
                raise ValueError("The AI returned a study plan with an invalid date.") from error
            if topic_day < datetime.now(timezone.utc).date():
                raise ValueError("The AI returned a study plan date in the past.")
            try:
                duration = int(topic.get("duration_minutes", 30))
            except (TypeError, ValueError) as error:
                raise ValueError("The AI returned an invalid study duration.") from error
            normalized.append({
                "id": str(uuid.uuid4()), "title": topic["title"], "day": topic["day"],
                "duration_minutes": max(5, min(600, duration)),
                "reason": topic["reason"], "completed": False,
            })
        plan_id = str(uuid.uuid4())
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO study_plans VALUES (?, ?, ?, ?, ?)",
                (plan_id, doc_id, goal, json.dumps(normalized), datetime.now(timezone.utc).isoformat()),
            )
        return {"id": plan_id, "doc_id": doc_id, "goal": goal, "topics": normalized, "sources": sources}

    def get_latest_plan(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM study_plans ORDER BY created_at DESC LIMIT 1").fetchone()
        if not row:
            return None
        return {"id": row["id"], "doc_id": row["doc_id"], "goal": row["goal"], "topics": json.loads(row["topics_json"]), "created_at": row["created_at"]}

    def update_plan_topic(self, topic_id: str, completed: bool) -> dict[str, Any]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM study_plans ORDER BY created_at DESC").fetchall()
            for row in rows:
                topics = json.loads(row["topics_json"])
                for topic in topics:
                    if topic["id"] == topic_id:
                        topic["completed"] = completed
                        connection.execute("UPDATE study_plans SET topics_json = ? WHERE id = ?", (json.dumps(topics), row["id"]))
                        return topic
        raise LookupError("Study plan topic not found.")

    def record_study_time(self, seconds: int) -> int:
        with self._connect() as connection:
            connection.execute("UPDATE study_time SET seconds = seconds + ? WHERE id = 1", (seconds,))
            return connection.execute("SELECT seconds FROM study_time WHERE id = 1").fetchone()["seconds"]

    def analytics(self) -> dict[str, Any]:
        with self._connect() as connection:
            attempts = connection.execute(
                """SELECT a.id, a.quiz_id, a.score, a.total, a.completed_at, q.difficulty
                FROM quiz_attempts a JOIN quizzes q ON q.id = a.quiz_id ORDER BY a.completed_at DESC"""
            ).fetchall()
            topic_rows = connection.execute("SELECT topic_scores_json FROM quiz_attempts").fetchall()
            seconds = connection.execute("SELECT seconds FROM study_time WHERE id = 1").fetchone()["seconds"]
            card_count = connection.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
            plans = connection.execute("SELECT topics_json FROM study_plans").fetchall()
        weak_topics: dict[str, list[int]] = {}
        for row in topic_rows:
            for topic, score in json.loads(row["topic_scores_json"]).items():
                aggregate = weak_topics.setdefault(topic, [0, 0])
                aggregate[0] += score["correct"]
                aggregate[1] += score["total"]
        weak = [
            {"topic": topic, "accuracy": round(correct / total * 100), "attempted": total}
            for topic, (correct, total) in weak_topics.items() if total and correct / total < 0.7
        ]
        completed_topics = total_topics = 0
        for row in plans:
            topics = json.loads(row["topics_json"])
            total_topics += len(topics)
            completed_topics += sum(bool(topic["completed"]) for topic in topics)
        return {
            "completed_quizzes": len(attempts), "quiz_attempts": [dict(row) for row in attempts],
            "weak_topics": sorted(weak, key=lambda item: item["accuracy"]),
            "average_score": round(sum(row["score"] / row["total"] * 100 for row in attempts) / len(attempts)) if attempts else 0,
            "study_time_seconds": seconds, "flashcards_saved": card_count,
            "topics_completed": completed_topics, "topics_total": total_topics,
            "learning_progress": round(completed_topics / total_topics * 100) if total_topics else 0,
        }

    def delete_document_data(self, doc_id: str) -> None:
        with self._connect() as connection:
            quiz_ids = [row["id"] for row in connection.execute("SELECT id FROM quizzes WHERE doc_id = ?", (doc_id,))]
            for quiz_id in quiz_ids:
                connection.execute("DELETE FROM quiz_attempts WHERE quiz_id = ?", (quiz_id,))
            connection.execute("DELETE FROM quizzes WHERE doc_id = ?", (doc_id,))
            connection.execute("DELETE FROM flashcards WHERE doc_id = ?", (doc_id,))
            connection.execute("DELETE FROM study_plans WHERE doc_id = ?", (doc_id,))


learning_service = LearningService()
