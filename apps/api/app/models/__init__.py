"""Import every model so ``Base.metadata`` is complete (Alembic and tests rely on this)."""

from app.models.activity import CodeSubmission, CodingAttempt, DetectedError
from app.models.ai import AiConversation
from app.models.content import Problem, ProblemTopic, Topic
from app.models.gamification import Achievement, UserAchievement
from app.models.intelligence import (
    CodingDnaTrait,
    DetectedWeakness,
    Streak,
    TopicPerformance,
)
from app.models.interview import (
    InterviewQuestion,
    InterviewResponse,
    InterviewScore,
    InterviewSession,
)
from app.models.planning import DailyMission, MissionItem, Roadmap, RoadmapItem
from app.models.user import Profile, Skill, User, UserSkill

__all__ = [
    "Achievement",
    "AiConversation",
    "CodeSubmission",
    "CodingAttempt",
    "CodingDnaTrait",
    "DailyMission",
    "DetectedError",
    "DetectedWeakness",
    "InterviewQuestion",
    "InterviewResponse",
    "InterviewScore",
    "InterviewSession",
    "MissionItem",
    "Problem",
    "ProblemTopic",
    "Profile",
    "Roadmap",
    "RoadmapItem",
    "Skill",
    "Streak",
    "Topic",
    "TopicPerformance",
    "User",
    "UserAchievement",
    "UserSkill",
]
