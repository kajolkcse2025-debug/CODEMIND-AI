
from fastapi import APIRouter

from app.api.v1 import (
    health,
    me,
    profile,
    problems,
    coding_assessment,
    ai_coach,
    recommendations,
    roadmap,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(me.router)
api_router.include_router(profile.router)
api_router.include_router(problems.router)
api_router.include_router(coding_assessment.router)
api_router.include_router(ai_coach.router)
api_router.include_router(recommendations.router)
api_router.include_router(roadmap.router)
