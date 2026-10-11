from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user, get_profile_service, get_verified_token
from app.core.security import VerifiedToken
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.user import MeFlags, MeResponse, UserOut
from app.services.profile_service import ProfileService

router = APIRouter(tags=["me"])


@router.get(
    "/me",
    response_model=MeResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="The authenticated user's application record",
)
def read_me(
    user: User = Depends(get_current_user),
    token: VerifiedToken = Depends(get_verified_token),
    profiles: ProfileService = Depends(get_profile_service),
) -> MeResponse:
    return MeResponse(
        user=UserOut.model_validate(user),
        profile=profiles.get_optional(user),
        flags=MeFlags(email_verified=token.email_verified),
    )
