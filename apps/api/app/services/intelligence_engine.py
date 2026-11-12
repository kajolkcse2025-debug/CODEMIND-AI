
"""Rule-based student intelligence engine.

Uses verified coding submissions to calculate topic mastery and weaknesses.
No external AI API calls are required.
"""

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import CodingAttempt, CodeSubmission
from app.models.content import ProblemTopic, Topic
from app.models.intelligence import DetectedWeakness, TopicPerformance


ENGINE_VERSION = 1


def _band(score: float | None) -> str:
    if score is None:
        return "unexplored"
    if score < 40:
        return "weak"
    if score < 65:
        return "developing"
    if score < 85:
        return "proficient"
    return "strong"


def rebuild_topic_performance(db: Session, user_id) -> dict:
    """Recalculate topic statistics from verified submissions."""

    rows = db.execute(
        select(
            CodingAttempt,
            CodeSubmission,
            ProblemTopic.topic_id,
            Topic.name,
        )
        .join(CodeSubmission, CodeSubmission.attempt_id == CodingAttempt.id)
        .join(ProblemTopic, ProblemTopic.problem_id == CodingAttempt.problem_id)
        .join(Topic, Topic.id == ProblemTopic.topic_id)
        .where(
            CodingAttempt.user_id == user_id,
            CodeSubmission.user_id == user_id,
            CodeSubmission.kind == "submit",
            CodeSubmission.verified.is_(True),
        )
        .order_by(CodeSubmission.submitted_at.asc())
    ).all()

    latest = {}
    for attempt, submission, topic_id, topic_name in rows:
        latest[(attempt.id, topic_id)] = (attempt, submission, topic_name)

    grouped = defaultdict(list)

    for (_, topic_id), (attempt, submission, topic_name) in latest.items():
        grouped[topic_id].append((attempt, submission, topic_name))

    updated = []

    for topic_id, records in grouped.items():
        attempts = len(records)
        solved = sum(
            1 for attempt, submission, _ in records
            if submission.verdict == "accepted"
            and attempt.outcome == "accepted"
        )

        first_try = sum(
            1 for attempt, submission, _ in records
            if submission.verdict == "accepted"
            and attempt.outcome == "accepted"
            and attempt.attempt_index == 1
        )

        accuracy = solved / attempts if attempts else 0
        score = accuracy * 100

        active_times = [
            attempt.active_time_sec
            for attempt, _, _ in records
            if attempt.active_time_sec is not None
            and attempt.active_time_sec > 0
        ]
        avg_time = (
            round(sum(active_times) / len(active_times))
            if active_times else None
        )

        hints = [
            attempt.hints_used
            for attempt, _, _ in records
            if attempt.hints_used is not None
        ]
        avg_hints = sum(hints) / len(hints) if hints else None

        confidence = min(attempts / 5, 1.0)

        performance = db.get(
            TopicPerformance,
            {"user_id": user_id, "topic_id": topic_id},
        )

        if performance is None:
            performance = TopicPerformance(
                user_id=user_id,
                topic_id=topic_id,
            )
            db.add(performance)

        performance.attempts_count = attempts
        performance.solved_count = solved
        performance.first_try_solved_count = first_try
        performance.accuracy = Decimal(str(round(accuracy, 4)))
        performance.success_rate = Decimal(str(round(accuracy, 4)))
        performance.avg_solve_time_sec = avg_time
        performance.avg_hints = (
            Decimal(str(round(avg_hints, 2)))
            if avg_hints is not None else None
        )
        performance.mastery_score = Decimal(str(round(score, 2)))
        performance.confidence = Decimal(str(round(confidence, 3)))
        performance.band = _band(score)
        performance.last_practiced_at = max(
            attempt.ended_at or attempt.started_at
            for attempt, _, _ in records
        )
        performance.engine_version = ENGINE_VERSION

        updated.append({
            "topic_id": str(topic_id),
            "topic": records[0][2],
            "attempts": attempts,
            "solved": solved,
            "mastery": round(score, 2),
            "band": _band(score),
        })

    db.flush()

    return {
        "topics_analyzed": len(updated),
        "results": updated,
    }


def detect_topic_weaknesses(db: Session, user_id) -> dict:
    """Create or update topic weaknesses based on measured mastery."""

    performances = db.execute(
        select(TopicPerformance, Topic.name)
        .join(Topic, Topic.id == TopicPerformance.topic_id)
        .where(
            TopicPerformance.user_id == user_id,
            TopicPerformance.attempts_count >= 2,
        )
    ).all()

    detected = []

    for performance, topic_name in performances:
        score = float(performance.mastery_score or 0)

        if score >= 50:
            continue

        code = "low_topic_mastery"

        weakness = db.execute(
            select(DetectedWeakness).where(
                DetectedWeakness.user_id == user_id,
                DetectedWeakness.topic_id == performance.topic_id,
                DetectedWeakness.weakness_code == code,
                DetectedWeakness.status.in_(["active", "improving"]),
            )
        ).scalar_one_or_none()

        severity = max(0.0, min(1.0, 1 - score / 100))
        now = datetime.now(timezone.utc)

        if weakness is None:
            weakness = DetectedWeakness(
                user_id=user_id,
                topic_id=performance.topic_id,
                weakness_code=code,
                severity=Decimal(str(round(severity, 3))),
                confidence=performance.confidence,
                occurrences=1,
                first_detected_at=now,
                last_detected_at=now,
                status="active",
                ai_interpretation=(
                    f"Your measured accuracy in {topic_name} is "
                    f"{score:.1f}%. Practice this topic."
                ),
                interpretation_version=ENGINE_VERSION,
                engine_version=ENGINE_VERSION,
            )
            db.add(weakness)
        else:
            weakness.severity = Decimal(str(round(severity, 3)))
            weakness.confidence = performance.confidence
            weakness.last_detected_at = now
            weakness.ai_interpretation = (
                f"Your measured accuracy in {topic_name} is "
                f"{score:.1f}%. Practice this topic."
            )
            weakness.engine_version = ENGINE_VERSION

        detected.append({
            "topic": topic_name,
            "mastery": score,
            "severity": round(severity, 3),
        })

    db.flush()

    return {
        "weak_topics": detected,
        "count": len(detected),
    }


def analyze_student(db: Session, user_id) -> dict:
    """Run the complete student intelligence analysis."""

    try:
        mastery = rebuild_topic_performance(db, user_id)
        weaknesses = detect_topic_weaknesses(db, user_id)
        db.commit()

        return {
            "success": True,
            "mastery": mastery,
            "weaknesses": weaknesses,
        }
    except Exception:
        db.rollback()
        raise
