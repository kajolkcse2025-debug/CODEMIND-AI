
"""Adaptive DSA problem recommendation engine."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import CodingAttempt
from app.models.content import Problem, ProblemTopic, Topic
from app.models.intelligence import TopicPerformance


def recommend_problems(db: Session, user_id, limit: int = 5) -> dict:
    performances = db.execute(
        select(TopicPerformance, Topic)
        .join(Topic, Topic.id == TopicPerformance.topic_id)
        .where(TopicPerformance.user_id == user_id)
        .order_by(TopicPerformance.mastery_score.asc().nulls_first())
    ).all()

    attempted_problem_ids = set(
        db.scalars(
            select(CodingAttempt.problem_id).where(
                CodingAttempt.user_id == user_id,
                CodingAttempt.outcome == "accepted",
            )
        ).all()
    )

    recommendations = []

    for performance, topic in performances:
        score = float(performance.mastery_score or 0)
        confidence = float(performance.confidence or 0)
        attempts = performance.attempts_count

        # Low confidence: the student needs more evidence.
        if confidence < 0.4 or attempts < 3:
            difficulty_order = ["easy", "medium"]
            per_difficulty_limit = 1
            reason = (
                f"Your measured mastery in {topic.name} is {score:.1f}%, "
                f"but it is based on only {attempts} attempts. "
                "Build consistency with more practice."
            )

        # High confidence and low mastery: strengthen fundamentals.
        elif score < 40:
            difficulty_order = ["easy", "medium"]
            per_difficulty_limit = limit
            reason = (
                f"Your mastery in {topic.name} is {score:.1f}%. "
                "Strengthen your fundamentals with focused practice."
            )

        elif score < 70:
            difficulty_order = ["easy", "medium", "hard"]
            per_difficulty_limit = limit
            reason = (
                f"Your mastery in {topic.name} is {score:.1f}%. "
                "Build consistency and gradually increase difficulty."
            )

        else:
            difficulty_order = ["medium", "hard", "easy"]
            per_difficulty_limit = limit
            reason = (
                f"Your measured mastery in {topic.name} is {score:.1f}%. "
                "Challenge yourself with more advanced problems."
            )

        for difficulty in difficulty_order:
            problems = db.execute(
                select(Problem)
                .join(
                    ProblemTopic,
                    ProblemTopic.problem_id == Problem.id,
                )
                .where(
                    ProblemTopic.topic_id == topic.id,
                    Problem.difficulty == difficulty,
                    Problem.status == "published",
                )
                .order_by(Problem.created_at.asc())
            ).scalars().all()

            added_for_difficulty = 0

            for problem in problems:
                if problem.id in attempted_problem_ids:
                    continue

                recommendations.append(
                    {
                        "problem_id": str(problem.id),
                        "slug": problem.slug,
                        "title": problem.title,
                        "topic": topic.name,
                        "difficulty": problem.difficulty,
                        "mastery": score,
                        "reason": reason,
                    }
                )

                added_for_difficulty += 1

                if len(recommendations) >= limit:
                    return {
                        "recommendations": recommendations,
                        "count": len(recommendations),
                    }

                if added_for_difficulty >= per_difficulty_limit:
                    break

    return {
        "recommendations": recommendations,
        "count": len(recommendations),
    }
