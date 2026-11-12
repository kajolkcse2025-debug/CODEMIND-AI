
"""Personalized problem recommendation API."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.recommendation_engine import recommend_problems


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get("")
def get_recommendations(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=5, ge=1, le=20),
):
    return recommend_problems(
        db=db,
        user_id=user.id,
        limit=limit,
    )
