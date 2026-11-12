
"""Personalized AI Coding Mentor API."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.ai import AiConversation, AiMessage
from app.models.user import User, Profile
from app.models.intelligence import (
    TopicPerformance,
    CodingDnaTrait,
    DetectedWeakness,
)
from app.models.activity import CodingAttempt, CodeSubmission
from app.models.content import Problem, ProblemTopic, Topic
from app.ai.types import AIMessage, ModelTier
from app.ai.factory import build_ai_provider
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    reply: str
    provider: str


SYSTEM_PROMPT = """
You are CodeMind AI, a personalized coding mentor and interview coach.

Your responsibilities:
1. Teach programming and DSA step by step.
2. Explain concepts in simple language with examples.
3. Give hints before revealing complete solutions.
4. Analyze the student's coding strengths and weaknesses using
   the available student data.
5. Adapt explanations to the student's current skill level.
6. Help prepare for technical interviews and placements.
7. Create realistic, personalized learning roadmaps.
8. Recommend what the student should learn and practice next.
9. Encourage independent problem-solving instead of blindly
   copying answers.
10. Consider the student's target company, role, available
    study time, and preferred programming language.
11. Never claim that the user has an authentication error,
    expired token, or connection issue. You cannot diagnose
    authentication from chat messages.
12. Never invent CGPA, coding statistics, skills, or achievements.
13. Use the supplied student context as the only source of
    personal performance information.
14. Clearly distinguish measured strengths from preliminary
    observations and unknown skills.
15. If performance records are empty, explain that an assessment
    is needed instead of pretending to have analyzed the student.

Important rules:
- Never invent student scores, achievements, or assessment results.
- If data is unavailable, say that more practice or assessment
  is needed.
- Treat low-confidence data as preliminary.
- A single accepted problem does not prove overall topic mastery.
- Use verified submission results as measured evidence.
- Give actionable, achievable recommendations.
- Be supportive, patient, practical, and concise.
"""


def build_student_context(db: Session, user: User) -> str:
    """Build personalized context from the student's existing records."""

    profile = db.scalar(
        select(Profile).where(Profile.user_id == user.id)
    )

    performance = db.scalars(
        select(TopicPerformance).where(
            TopicPerformance.user_id == user.id
        )
    ).all()

    dna = db.scalars(
        select(CodingDnaTrait).where(
            CodingDnaTrait.user_id == user.id
        )
    ).all()

    weaknesses = db.scalars(
        select(DetectedWeakness).where(
            DetectedWeakness.user_id == user.id,
            DetectedWeakness.status.in_(["active", "improving"]),
        )
    ).all()

    assessment_rows = db.execute(
        select(
            CodeSubmission,
            CodingAttempt,
            Problem,
            Topic,
        )
        .join(
            CodingAttempt,
            CodeSubmission.attempt_id == CodingAttempt.id,
        )
        .join(
            Problem,
            CodingAttempt.problem_id == Problem.id,
        )
        .outerjoin(
            ProblemTopic,
            ProblemTopic.problem_id == Problem.id,
        )
        .outerjoin(
            Topic,
            Topic.id == ProblemTopic.topic_id,
        )
        .where(
            CodeSubmission.user_id == user.id,
            CodeSubmission.verified.is_(True),
            CodingAttempt.context == "assessment",
        )
        .order_by(CodeSubmission.submitted_at.desc())
        .limit(10)
    ).all()

    lines = ["STUDENT PROFILE:"]

    if profile:
        fields = {
            "Name": profile.name,
            "College": profile.college,
            "Degree": profile.degree,
            "Year": profile.current_year,
            "CGPA": profile.cgpa,
            "Dream company": profile.dream_company,
            "Dream role": profile.dream_role,
            "Target package (LPA)": profile.target_package_lpa,
            "Daily study time (minutes)": profile.daily_minutes,
            "Preferred language": profile.preferred_language,
        }

        for label, value in fields.items():
            if value is not None and value != "":
                lines.append(f"{label}: {value}")

    lines.append("\nVERIFIED CODING ASSESSMENT SUBMISSIONS:")

    if assessment_rows:
        for submission, attempt, problem, topic in assessment_rows:
            topic_name = topic.slug if topic else "Unknown topic"
            submitted_at = (
                submission.submitted_at.isoformat()
                if submission.submitted_at
                else "Unknown time"
            )

            lines.append(
                f"Question: {problem.title}; "
                f"Topic: {topic_name}; "
                f"Language: {submission.language}; "
                f"Verdict: {submission.verdict}; "
                f"Tests passed: {submission.tests_passed}/"
                f"{submission.tests_total}; "
                f"Attempt outcome: {attempt.outcome}; "
                f"Submitted: {submitted_at}"
            )

        lines.append(
            "These are verified individual submissions. "
            "Do not infer overall topic mastery from one question."
        )
    else:
        lines.append("No verified coding assessment submissions yet.")

    lines.append("\nTOPIC PERFORMANCE:")

    if performance:
        for item in performance:
            lines.append(
                f"Topic ID: {item.topic_id}, "
                f"Mastery: {item.mastery_score}, "
                f"Accuracy: {item.accuracy}, "
                f"Attempts: {item.attempts_count}, "
                f"Solved: {item.solved_count}, "
                f"Skill level: {item.band}, "
                f"Confidence: {item.confidence}"
            )
    else:
        lines.append("No topic performance data available yet.")

    lines.append("\nCODING DNA:")

    if dna:
        for item in dna:
            lines.append(
                f"Trait: {item.trait}, "
                f"Score: {item.score}, "
                f"State: {item.state}, "
                f"Confidence: {item.confidence}, "
                f"Samples: {item.sample_count}"
            )
    else:
        lines.append("Coding DNA is still being calibrated.")

    lines.append("\nDETECTED WEAKNESSES:")

    if weaknesses:
        for item in weaknesses:
            lines.append(
                f"Weakness: {item.weakness_code}, "
                f"Severity: {item.severity}, "
                f"Occurrences: {item.occurrences}, "
                f"Confidence: {item.confidence}, "
                f"Status: {item.status}"
            )
    else:
        lines.append("No active weaknesses recorded.")

    return "\n".join(lines)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = request.message.strip()

    if not message:
        raise HTTPException(422, "Message cannot be empty.")

    try:
        if request.conversation_id:
            conversation = db.scalar(
                select(AiConversation).where(
                    AiConversation.id == request.conversation_id,
                    AiConversation.user_id == current_user.id,
                    AiConversation.kind == "coach",
                )
            )

            if conversation is None:
                raise HTTPException(
                    404, "Conversation not found."
                )
        else:
            conversation = AiConversation(
                user_id=current_user.id,
                kind="coach",
            )
            db.add(conversation)
            db.flush()

        history = db.scalars(
            select(AiMessage)
            .where(
                AiMessage.conversation_id == conversation.id
            )
            .order_by(AiMessage.created_at.desc())
            .limit(20)
        ).all()

        history.reverse()

        student_context = build_student_context(
            db, current_user
        )

        messages = [
            AIMessage(
                role="system",
                content=SYSTEM_PROMPT,
            ),
            AIMessage(
                role="system",
                content=(
                    "Use this verified student data to personalize "
                    "your guidance. Do not invent missing information:\n"
                    f"{student_context}"
                ),
            ),
            *[
                AIMessage(
                    role=item.role,
                    content=item.content,
                )
                for item in history
            ],
            AIMessage(
                role="user",
                content=message,
            ),
        ]

        settings = get_settings()
        provider = build_ai_provider(settings)

        response = provider.generate_text(
            messages=messages,
            tier=ModelTier.FAST,
        )

        if not response.text:
            raise RuntimeError(
                "AI provider returned an empty response."
            )

        db.add(
            AiMessage(
                conversation_id=conversation.id,
                role="user",
                content=message,
            )
        )

        db.add(
            AiMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=response.text,
            )
        )

        db.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            reply=response.text,
            provider=response.provider,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        logger.exception("AI Coach request failed")
        raise HTTPException(
            503,
            "AI Coach is temporarily unavailable. Please try again.",
        )
