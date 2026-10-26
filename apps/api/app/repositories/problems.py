
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Problem

from app.models.content import ProblemTestCase


class ProblemsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_published(
        self,
        difficulty: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Problem]:
        query = select(Problem).where(Problem.status == "published")

        if difficulty is not None:
            query = query.where(Problem.difficulty == difficulty)

        query = query.order_by(Problem.title).limit(limit).offset(offset)

        return list(self._session.scalars(query).all())

    def get_published_by_slug(self, slug: str) -> Problem | None:
        query = select(Problem).where(
            Problem.slug == slug,
            Problem.status == "published",
        )
        return self._session.scalar(query)  
        
    def get_test_cases(self, problem_id, problem_version: int):
        query = (
            select(ProblemTestCase)
            .where(
                ProblemTestCase.problem_id == problem_id,
                ProblemTestCase.problem_version == problem_version,
            )
            .order_by(ProblemTestCase.case_index)
        )
        return list(self._session.scalars(query).all())

    
