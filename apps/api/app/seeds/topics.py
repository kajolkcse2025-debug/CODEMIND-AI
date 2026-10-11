"""The canonical topic taxonomy: the only one. Assessment, analytics and roadmap all use it.

Diagnostic rounds follow the blueprint: round 1 easy, round 2 medium, round 3 advanced.
``interview_weight`` is deliberately NOT set here: it is a tunable assumption (default 1.00)
and re-seeding must never overwrite a tuned value.
"""

from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.content import Topic


@dataclass(frozen=True)
class TopicSeed:
    id: int
    slug: str
    name: str
    diagnostic_round: int | None = None


CANONICAL_TOPICS: tuple[TopicSeed, ...] = (
    TopicSeed(1, "arrays", "Arrays", 1),
    TopicSeed(2, "strings", "Strings", 1),
    TopicSeed(3, "hashing", "Hashing", 1),
    TopicSeed(4, "sliding-window", "Sliding Window", 2),
    TopicSeed(5, "two-pointer", "Two Pointer"),
    TopicSeed(6, "binary-search", "Binary Search"),
    TopicSeed(7, "linked-list", "Linked List"),
    TopicSeed(8, "stack", "Stack", 2),
    TopicSeed(9, "queue", "Queue", 2),
    TopicSeed(10, "heap", "Heap"),
    TopicSeed(11, "trees", "Trees", 3),
    TopicSeed(12, "bst", "BST"),
    TopicSeed(13, "graphs", "Graphs", 3),
    TopicSeed(14, "backtracking", "Backtracking"),
    TopicSeed(15, "greedy", "Greedy"),
    TopicSeed(16, "dynamic-programming", "Dynamic Programming", 3),
    TopicSeed(17, "trie", "Trie"),
)


def seed_topics(session: Session) -> int:
    """Idempotently upsert the canonical topics. Returns the number of topics now defined."""
    for order, topic in enumerate(CANONICAL_TOPICS, start=1):
        statement = insert(Topic).values(
            id=topic.id,
            slug=topic.slug,
            name=topic.name,
            display_order=order,
            diagnostic_round=topic.diagnostic_round,
        )
        statement = statement.on_conflict_do_update(
            index_elements=[Topic.id],
            set_={
                "slug": statement.excluded.slug,
                "name": statement.excluded.name,
                "display_order": statement.excluded.display_order,
                "diagnostic_round": statement.excluded.diagnostic_round,
            },
        )
        session.execute(statement)
    session.commit()
    return len(CANONICAL_TOPICS)
