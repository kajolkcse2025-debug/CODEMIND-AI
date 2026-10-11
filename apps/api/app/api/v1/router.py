from fastapi import APIRouter

from app.api.v1 import health, me, profile

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(me.router)
api_router.include_router(profile.router)
