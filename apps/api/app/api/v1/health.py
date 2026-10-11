from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.deps import get_health_service
from app.schemas.common import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
    summary="Readiness probe (database and Redis)",
)
def ready(service: HealthService = Depends(get_health_service)) -> ReadinessResponse | JSONResponse:
    checks = service.check()
    if all(value == "ok" for value in checks.values()):
        return ReadinessResponse(status="ok", checks=checks)
    body = ReadinessResponse(status="unavailable", checks=checks)
    return JSONResponse(status_code=503, content=body.model_dump())
