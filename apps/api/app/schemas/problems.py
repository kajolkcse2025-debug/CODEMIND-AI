
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProblemListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    difficulty: str
    expected_time_sec: int
    technique_tags: list[str]


class ProblemDetail(ProblemListItem):
    statement_md: str
    constraints_md: str | None
    starter_code: dict | None


class ProblemListResponse(BaseModel):
    items: list[ProblemListItem]
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
