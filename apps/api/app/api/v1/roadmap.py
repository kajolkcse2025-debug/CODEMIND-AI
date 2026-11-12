
"""Personalized learning roadmap API."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.planning import Roadmap, RoadmapItem
from app.services.roadmap_engine import generate_roadmap

router = APIRouter(
    prefix="/roadmap",
    tags=["Roadmap"],
)


@router.get("")
def get_roadmap(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    daily_minutes: int = Query(default=45, ge=15, le=240),
):
    return generate_roadmap(
        db=db,
        user_id=user.id,
        daily_minutes=daily_minutes,
    )


@router.put("/{item_id}/complete")
def complete_roadmap_item(
    item_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    item = (
        db.query(RoadmapItem)
        .join(Roadmap, Roadmap.id == RoadmapItem.roadmap_id)
        .filter(
            RoadmapItem.id == item_id,
            RoadmapItem.user_id == user.id,
            Roadmap.status == "active",
        )
        .first()
    )

    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap topic not found")

    if item.status == "done":
        return {
            "message": "Topic already completed",
            "item_id": str(item.id),
            "status": "done",
        }

    item.status = "done"
    item.completed_count = item.target_problem_count

    next_item = (
        db.query(RoadmapItem)
        .filter(
            RoadmapItem.roadmap_id == item.roadmap_id,
            RoadmapItem.status == "upcoming",
        )
        .order_by(RoadmapItem.position)
        .first()
    )

    if next_item:
        next_item.status = "active"

    db.commit()

    return {
        "message": "Topic completed successfully",
        "item_id": str(item.id),
        "status": item.status,
        "next_topic": next_item.title if next_item else None,
    }
