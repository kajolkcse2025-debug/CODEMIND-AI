from typing import Any

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_user, get_profile_service
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.profile import ProfileIn, ProfileOut
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
}


@router.get("", response_model=ProfileOut, responses=_ERRORS, summary="Read your profile")
def get_profile(
    user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.get(user)


@router.post(
    "",
    response_model=ProfileOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Create your profile (once)",
)
def create_profile(
    data: ProfileIn,
    user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.create(user, data)


@router.put(
    "",
    response_model=ProfileOut,
    responses={**_ERRORS, 422: {"model": ErrorResponse}},
    summary="Replace the editable profile fields",
)
def update_profile(
    data: ProfileIn,
    user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileOut:
    return service.update(user, data)
