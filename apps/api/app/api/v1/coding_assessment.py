
"""API endpoints for coding assessments."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.submissions import SubmissionCreate
from app.services.coding_assessment_bank import QUESTION_BANK
from app.services.coding_assessment_selector import (
    select_assessment_questions,
    summarize_selection,
)
from app.services.coding_assessment_service import CodingAssessmentService


router = APIRouter(
    prefix="/coding-assessment",
    tags=["Coding Assessment"],
)


def get_coding_assessment_service() -> CodingAssessmentService:
    return CodingAssessmentService()


@router.get("/questions")
def get_assessment_questions(
    count: int = Query(default=8, ge=1, le=8),
):
    """Return a selected set of coding assessment questions."""
    try:
        questions = select_assessment_questions(
            question_count=count,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "total": len(questions),
        
        "questions": [
        {
            "slug": question.slug,
            "title": question.title,
            "topic": question.topic_slug,
            "difficulty": question.difficulty,
            "statement": question.statement_md,
            "constraints": question.constraints_md,
            "starter_code": question.starter_code,
            "time_limit_sec": question.expected_time_sec,
            "examples": [
                {
                    "input": case.stdin.rstrip("\n"),
                    "output": case.expected_stdout.rstrip("\n"),
                }
                for case in question.test_cases[:2]
            ],
            "optimal_time_complexity": question.optimal_time_complexity,
            "optimal_space_complexity": question.optimal_space_complexity,
        }
        for question in questions
    ],

        "summary": summarize_selection(questions),
    }


@router.get("/health")
def coding_assessment_health():
    """Check whether the coding assessment bank is available."""
    return {
        "status": "ok",
        "question_bank_size": len(QUESTION_BANK),
    }


@router.post("/{slug}/submit")
def submit_assessment_code(
    slug: str,
    payload: SubmissionCreate,
    service: Annotated[
        CodingAssessmentService,
        Depends(get_coding_assessment_service),
    ],
):
    """Run a student's code against an assessment question."""
    return service.submit_code(
        slug=slug,
        language=payload.language,
        source_code=payload.source_code,
    )

