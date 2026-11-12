
"""Adaptive learning roadmap generation engine."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import CodingAttempt, CodeSubmission
from app.models.content import Problem, ProblemTopic, Topic
from app.models.intelligence import TopicPerformance
from app.models.planning import Roadmap, RoadmapItem


def _serialize_roadmap(db: Session, roadmap: Roadmap) -> dict:
    """Convert roadmap database records into an API-friendly response."""

    items = db.scalars(
        select(RoadmapItem)
        .where(RoadmapItem.roadmap_id == roadmap.id)
        .order_by(RoadmapItem.position)
    ).all()

    completed = sum(1 for item in items if item.status == "done")

    return {
        "roadmap_id": str(roadmap.id),
        "status": roadmap.status,
        "daily_minutes": roadmap.daily_minutes,
        "total_topics": len(items),
        "completed_topics": completed,
        "progress_percentage": round(
            completed / len(items) * 100, 1
        ) if items else 0,
        "rationale": roadmap.rationale_md,
        "items": [
            {
                "id": str(item.id),
                "position": item.position,
                "phase": item.phase_label,
                "topic_id": item.topic_id,
                "title": item.title,
                "type": item.item_type,
                "target_problems": item.target_problem_count,
                "completed_problems": item.completed_count,
                "status": item.status,
                "reason": item.reason_detail,
                "due_date": (
                    item.due_date.isoformat()
                    if item.due_date else None
                ),
            }
            for item in items
        ],
    }


def _get_assessment_performance(db: Session, user_id) -> dict:
    """Collect verified assessment results grouped by DSA topic."""

    rows = db.execute(
        select(
            ProblemTopic.topic_id,
            CodingAttempt.outcome,
            CodeSubmission.tests_passed,
            CodeSubmission.tests_total,
        )
        .join(
            CodingAttempt,
            CodingAttempt.problem_id == ProblemTopic.problem_id,
        )
        .join(
            CodeSubmission,
            CodeSubmission.attempt_id == CodingAttempt.id,
        )
        .where(
            CodingAttempt.user_id == user_id,
            CodingAttempt.context == "assessment",
            CodeSubmission.user_id == user_id,
            CodeSubmission.kind == "submit",
            CodeSubmission.verified.is_(True),
        )
    ).all()

    results = {}

    for topic_id, outcome, passed, total in rows:
        data = results.setdefault(
            topic_id,
            {
                "attempts": 0,
                "passed_tests": 0,
                "total_tests": 0,
                "accepted": 0,
            },
        )

        data["attempts"] += 1
        data["passed_tests"] += passed or 0
        data["total_tests"] += total or 0

        if outcome == "accepted":
            data["accepted"] += 1

    for data in results.values():
        if data["total_tests"] > 0:
            data["score"] = (
                data["passed_tests"] / data["total_tests"]
            ) * 100
        elif data["attempts"] > 0:
            data["score"] = (
                data["accepted"] / data["attempts"]
            ) * 100
        else:
            data["score"] = 0.0

    return results


def _get_topic_decision(
    topic_id: int,
    performance_by_topic: dict,
    assessment_by_topic: dict,
) -> dict:
    """Decide the next learning activity using both data sources."""

    performance = performance_by_topic.get(topic_id)
    assessment = assessment_by_topic.get(topic_id)

    practice_attempts = (
        performance.attempts_count if performance else 0
    )

    practice_mastery = (
        float(performance.mastery_score)
        if performance and performance.mastery_score is not None
        else None
    )

    confidence = (
        float(performance.confidence)
        if performance and performance.confidence is not None
        else 0.0
    )

    assessment_attempts = (
        assessment["attempts"] if assessment else 0
    )

    assessment_score = (
        assessment["score"] if assessment else None
    )

    # Combine assessment evidence with regular coding performance.
    scores = []

    if practice_mastery is not None:
        scores.append((practice_mastery, 0.4))

    if assessment_score is not None:
        scores.append((assessment_score, 0.6))

    if scores:
        total_weight = sum(weight for _, weight in scores)
        mastery = sum(
            score * weight for score, weight in scores
        ) / total_weight
    else:
        mastery = 0.0

    total_attempts = practice_attempts + assessment_attempts

    # Assessment evidence increases confidence in the topic decision.
    if assessment_attempts:
        confidence = max(
            confidence,
            min(assessment_attempts / 3, 1.0),
        )

    if total_attempts == 0:
        item_type = "learn"
        reason_code = "new_topic"
        explanation = (
            "You have no recorded performance for this topic yet. "
            "Start by learning its fundamentals."
        )

    elif assessment_score is not None and assessment_score < 50:
        item_type = "practice"
        reason_code = "assessment_weakness"
        explanation = (
            f"Your assessment score for this topic was "
            f"{assessment_score:.1f}%. Focus on fundamentals "
            "and targeted practice."
        )

    elif mastery < 50:
        item_type = "practice"
        reason_code = "low_mastery"
        explanation = (
            "Your combined assessment and coding-practice "
            "performance indicates that you need more practice."
        )

    elif total_attempts < 3 or confidence < 0.4:
        item_type = "practice"
        reason_code = "insufficient_evidence"
        explanation = (
            "Complete more problems so CodeMind can measure "
            "your understanding more reliably."
        )

    elif mastery < 75:
        item_type = "practice"
        reason_code = "developing_mastery"
        explanation = (
            "You understand some parts of this topic. "
            "More practice will improve consistency."
        )

    else:
        item_type = "revise"
        reason_code = "strong_mastery"
        explanation = (
            "Your performance is strong. Revise important "
            "patterns and attempt more challenging problems."
        )

    return {
        "item_type": item_type,
        "reason_code": reason_code,
        "explanation": explanation,
        "mastery": round(mastery, 1),
        "confidence": round(confidence, 2),
        "practice_attempts": practice_attempts,
        "assessment_attempts": assessment_attempts,
        "assessment_score": (
            round(assessment_score, 1)
            if assessment_score is not None else None
        ),
    }


def generate_roadmap(
    db: Session,
    user_id,
    daily_minutes: int = 45,
) -> dict:
    """Generate or refresh a personalized roadmap."""

    topics = db.scalars(
        select(Topic).order_by(Topic.display_order)
    ).all()

    performances = db.scalars(
        select(TopicPerformance).where(
            TopicPerformance.user_id == user_id
        )
    ).all()

    performance_by_topic = {
        performance.topic_id: performance
        for performance in performances
    }

    assessment_by_topic = _get_assessment_performance(
        db,
        user_id,
    )

    existing = db.scalar(
        select(Roadmap).where(
            Roadmap.user_id == user_id,
            Roadmap.kind == "standard",
            Roadmap.status == "active",
        )
    )

    today = date.today()

    if existing:
        # Refresh recommendations without deleting completed work.
        items = db.scalars(
            select(RoadmapItem)
            .where(RoadmapItem.roadmap_id == existing.id)
            .order_by(RoadmapItem.position)
        ).all()

        for item in items:
            if item.status == "done":
                continue

            decision = _get_topic_decision(
                item.topic_id,
                performance_by_topic,
                assessment_by_topic,
            )

            item.item_type = decision["item_type"]
            item.title = (
                f"{item.title.split(' — ')[0].split(' â€” ')[0]} "
                f"— {decision['item_type'].title()}"
            )
            item.reason_code = decision["reason_code"]
            item.reason_detail = decision

        existing.daily_minutes = daily_minutes
        existing.rationale_md = (
            "This roadmap adapts to your verified coding assessment "
            "results and regular coding-practice performance. "
            "Completed topics are preserved."
        )

        db.commit()
        db.refresh(existing)

        return _serialize_roadmap(db, existing)

    roadmap = Roadmap(
        user_id=user_id,
        kind="standard",
        status="active",
        version=1,
        daily_minutes=daily_minutes,
        inputs_snapshot={
            "topic_count": len(topics),
            "daily_minutes": daily_minutes,
            "assessment_topic_count": len(assessment_by_topic),
        },
        rationale_md=(
            "This roadmap uses your verified assessment results "
            "and regular coding-practice performance to select "
            "the learning activity for each topic."
        ),
        engine_version=2,
    )

    db.add(roadmap)
    db.flush()

    for position, topic in enumerate(topics, start=1):
        decision = _get_topic_decision(
            topic.id,
            performance_by_topic,
            assessment_by_topic,
        )

        item = RoadmapItem(
            roadmap_id=roadmap.id,
            user_id=user_id,
            position=position,
            phase_label=f"Phase {position}",
            topic_id=topic.id,
            item_type=decision["item_type"],
            title=f"{topic.name} — {decision['item_type'].title()}",
            target_problem_count=3,
            completed_count=0,
            start_date=today + timedelta(days=(position - 1) * 2),
            due_date=today + timedelta(days=position * 2),
            status="active" if position == 1 else "upcoming",
            reason_code=decision["reason_code"],
            reason_detail=decision,
        )

        db.add(item)

    db.commit()
    db.refresh(roadmap)

    return _serialize_roadmap(db, roadmap)
