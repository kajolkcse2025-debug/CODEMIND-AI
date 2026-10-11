import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.redis import KeyValueStore

logger = logging.getLogger("app.health")


class HealthService:
    """Dependency probes for readiness. Reports only ok/failing, never connection details."""

    def __init__(self, session: Session, store: KeyValueStore) -> None:
        self._session = session
        self._store = store

    def check(self) -> dict[str, str]:
        checks: dict[str, str] = {}
        try:
            self._session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            logger.warning("readiness_database_failed", exc_info=True)
            checks["database"] = "failing"
        try:
            checks["redis"] = "ok" if self._store.ping() else "failing"
        except Exception:
            logger.warning("readiness_redis_failed", exc_info=True)
            checks["redis"] = "failing"
        return checks
