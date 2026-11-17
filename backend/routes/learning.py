from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    FlashcardGenerateRequest, FlashcardRatingRequest, MindMapRequest,
    PlannerGenerateRequest, PlannerTopicUpdateRequest, QuizGenerateRequest,
    QuizSubmitRequest, StudyTimeRequest,
)
from backend.services.learning_service import learning_service

router = APIRouter(prefix="/api/learning", tags=["learning"])


def _call(operation, *args):
    try:
        return operation(*args)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/quizzes")
async def generate_quiz(request: QuizGenerateRequest):
    return _call(learning_service.generate_quiz, request.doc_id, request.difficulty, request.count)


@router.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, request: QuizSubmitRequest):
    return _call(learning_service.submit_quiz, quiz_id, request.answers)


@router.get("/quizzes")
async def list_quizzes():
    return {"attempts": learning_service.analytics()["quiz_attempts"]}


@router.post("/flashcards")
async def generate_flashcards(request: FlashcardGenerateRequest):
    return _call(learning_service.generate_flashcards, request.doc_id, request.count)


@router.get("/flashcards")
async def list_flashcards(doc_id: str | None = None):
    return {"flashcards": learning_service.list_flashcards(doc_id)}


@router.patch("/flashcards/{card_id}")
async def rate_flashcard(card_id: str, request: FlashcardRatingRequest):
    return _call(learning_service.rate_flashcard, card_id, request.rating)


@router.post("/mindmap")
async def generate_mindmap(request: MindMapRequest):
    return _call(learning_service.generate_mindmap, request.doc_id)


@router.post("/planner")
async def generate_plan(request: PlannerGenerateRequest):
    return _call(learning_service.generate_plan, request.doc_id, request.goal)


@router.get("/planner")
async def get_plan():
    return {"plan": learning_service.get_latest_plan()}


@router.patch("/planner/topics/{topic_id}")
async def update_plan_topic(topic_id: str, request: PlannerTopicUpdateRequest):
    return _call(learning_service.update_plan_topic, topic_id, request.completed)


@router.get("/analytics")
async def get_analytics():
    return learning_service.analytics()


@router.post("/analytics/study-time")
async def record_study_time(request: StudyTimeRequest):
    return {"study_time_seconds": learning_service.record_study_time(request.seconds)}
