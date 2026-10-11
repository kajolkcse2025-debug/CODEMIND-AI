import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.profile import ProfileOut


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str | None
    display_name: str | None
    role: str
    onboarding_status: str
    assessment_status: str
    xp_total: int
    level: int
    created_at: datetime


class MeFlags(BaseModel):
    email_verified: bool


class MeResponse(BaseModel):
    user: UserOut
    profile: ProfileOut | None
    flags: MeFlags
