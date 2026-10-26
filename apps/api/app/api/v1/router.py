from fastapi import APIRouter

from app.api.v1 import health, me, profile, problems, coding_assessment


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(me.router)
api_router.include_router(profile.router)
api_router.include_router(problems.router)
api_router.include_router(coding_assessment.router)
