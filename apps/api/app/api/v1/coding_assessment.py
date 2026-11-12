
"""API endpoints for coding assessments."""

import hashlib
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.roadmap_engine import generate_roadmap

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.activity import CodingAttempt, CodeSubmission
from app.models.content import Problem, ProblemTopic, Topic
from app.models.user import User
from app.schemas.submissions import SubmissionCreate
from app.services.coding_assessment_bank import QUESTION_BANK
from app.services.coding_assessment_selector import (
    select_assessment_questions,
    summarize_selection,
)
from app.services.coding_assessment_service import CodingAssessmentService


router = APIRouter(prefix="/coding-assessment", tags=["Coding Assessment"])


def get_coding_assessment_service() -> CodingAssessmentService:
    return CodingAssessmentService()


@router.get("/questions")
def get_assessment_questions(
    count: int = Query(default=8, ge=1, le=8),
):
    questions = select_assessment_questions(question_count=count)

    return {
        "total": len(questions),
        "questions": [
            {
                "slug": question.slug,
                "title": question.title,
                "topic_slug": question.topic_slug,
                "difficulty": question.difficulty,
                "statement_md": question.statement_md,
                "constraints_md": question.constraints_md,
                "starter_code": question.starter_code,
                "expected_time_sec": question.expected_time_sec,
                "optimal_time_complexity": question.optimal_time_complexity,
                "optimal_space_complexity": question.optimal_space_complexity,
                "examples": [
                    {
                        "input": case.stdin,
                        "output": case.expected_stdout,
                    }
                    for case in question.test_cases[:2]
                ],
                "diagnostic_level": question.diagnostic_level,
            }
            for question in questions
        ],
        "summary": summarize_selection(questions),
    }


@router.get("/health")
def coding_assessment_health():
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
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    question = next(
        (item for item in QUESTION_BANK if item.slug == slug),
        None,
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment question not found.",
        )

    # Execute and verify submitted code first.
    result = service.submit_code(
        slug=slug,
        language=payload.language,
        source_code=payload.source_code,
    )

    # Resolve the canonical topic.
    topic = db.scalar(
        select(Topic).where(Topic.slug == question.topic_slug)
    )

    if topic is None:
        raise HTTPException(
            status_code=500,
            detail="Assessment topic is not configured.",
        )

    # Reuse an existing problem or create it once.
    problem = db.scalar(
        select(Problem).where(Problem.slug == question.slug)
    )

    if problem is None:
        problem = Problem(
            slug=question.slug,
            title=question.title,
            statement_md=question.statement_md,
            constraints_md=question.constraints_md,
            difficulty=question.difficulty,
            expected_time_sec=question.expected_time_sec,
            optimal_time_complexity=question.optimal_time_complexity,
            optimal_space_complexity=question.optimal_space_complexity,
            starter_code={"python": question.starter_code},
            technique_tags=list(question.technique_tags),
            status="published",
            is_diagnostic=True,
            diagnostic_level=question.diagnostic_level,
        )
        db.add(problem)
        db.flush()

    # Link the problem to its canonical topic.
    problem_topic = db.get(
        ProblemTopic,
        (problem.id, topic.id),
    )

    if problem_topic is None:
        db.add(
            ProblemTopic(
                problem_id=problem.id,
                topic_id=topic.id,
                is_primary=True,
            )
        )

    now = datetime.now(timezone.utc)

    # Record one assessment attempt.
    attempt = CodingAttempt(
        user_id=user.id,
        problem_id=problem.id,
        problem_version=problem.version,
        context="assessment",
        started_at=now,
        ended_at=now,
        outcome=(
            "accepted"
            if result["verdict"] == "accepted"
            else "failed"
        ),
        submission_count=1,
        active_time_sec=0,
    )

    db.add(attempt)
    db.flush()

    # Store the verified runner result and submission metadata.
    submission = CodeSubmission(
        attempt_id=attempt.id,
        user_id=user.id,
        language=payload.language,
        code=payload.source_code,
        code_sha256=hashlib.sha256(
            payload.source_code.encode("utf-8")
        ).hexdigest(),
        kind="submit",
        verdict=result["verdict"],
        verified=result["verified"],
        tests_passed=result["tests_passed"],
        tests_total=result["tests_total"],
        failed_test_tags=[],
    )

    db.add(submission)
    db.commit()

    # Automatically refresh the student's adaptive roadmap.
    generate_roadmap(db, user.id)

    return result