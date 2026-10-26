from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import get_problems_service
from app.schemas.problems import ProblemDetail, ProblemListResponse
from app.schemas.submissions import SubmissionCreate, SubmissionResult
from app.services.problems_service import ProblemsService


router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=ProblemListResponse)
def list_problems(
    service: Annotated[ProblemsService, Depends(get_problems_service)],
    difficulty: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProblemListResponse:
    return service.list_problems(
        difficulty=difficulty,
        limit=limit,
        offset=offset,
    )


@router.get("/{slug}", response_model=ProblemDetail)
def get_problem(
    slug: str,
    service: Annotated[ProblemsService, Depends(get_problems_service)],
) -> ProblemDetail:
    return service.get_problem(slug)


@router.post("/{slug}/submissions", response_model=SubmissionResult)
def submit_code(
    slug: str,
    payload: SubmissionCreate,
    service: Annotated[ProblemsService, Depends(get_problems_service)],
) -> SubmissionResult:
    return service.submit_code(slug, payload)
