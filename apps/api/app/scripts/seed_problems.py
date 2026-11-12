
from sqlalchemy import select

from app.db.session import get_session_factory
from app.models.content import Problem, ProblemTopic, Topic, ProblemTestCase


PROBLEMS = [
    {
        "slug": "sum-two-numbers",
        "title": "Sum Two Numbers",
        "statement_md": (
            "## Problem\n"
            "Read two integers and print their sum.\n\n"
            "### Example\n"
            "Input: `3 5`\n\n"
            "Output: `8`"
        ),
        "constraints_md": "The inputs are integers.",
        "difficulty": "easy",
        "expected_time_sec": 300,
        "optimal_time_complexity": "O(1)",
        "optimal_space_complexity": "O(1)",
        "technique_tags": ["input-output", "arithmetic"],
        "topic_slug": "arrays",
        "starter_code": {
            "python": "a, b = map(int, input().split())\n# Write your code below\n"
        },
        "tests": [
            ("3 5\n", "8\n"),
            ("-2 7\n", "5\n"),
            ("0 0\n", "0\n"),
        ],
    },
    {
        "slug": "even-or-odd",
        "title": "Even or Odd",
        "statement_md": (
            "## Problem\n"
            "Read an integer. Print `Even` if it is divisible by 2; "
            "otherwise print `Odd`.\n\n"
            "### Example\nInput: `7`\n\nOutput: `Odd`"
        ),
        "constraints_md": "The input is an integer.",
        "difficulty": "easy",
        "expected_time_sec": 300,
        "optimal_time_complexity": "O(1)",
        "optimal_space_complexity": "O(1)",
        "technique_tags": ["conditionals", "modulo"],
        "topic_slug": "arrays",
        "starter_code": {
            "python": "n = int(input())\n# Write your code below\n"
        },
        "tests": [
            ("4\n", "Even\n"),
            ("7\n", "Odd\n"),
            ("0\n", "Even\n"),
        ],
    },
    {
        "slug": "largest-of-three",
        "title": "Largest of Three Numbers",
        "statement_md": (
            "## Problem\n"
            "Read three integers and print the largest one.\n\n"
            "### Example\nInput: `4 9 2`\n\nOutput: `9`"
        ),
        "constraints_md": "The inputs are integers.",
        "difficulty": "easy",
        "expected_time_sec": 420,
        "optimal_time_complexity": "O(1)",
        "optimal_space_complexity": "O(1)",
        "technique_tags": ["conditionals", "comparison"],
        "topic_slug": "arrays",
        "starter_code": {
            "python": "a, b, c = map(int, input().split())\n# Write your code below\n"
        },
        "tests": [
            ("4 9 2\n", "9\n"),
            ("8 3 5\n", "8\n"),
            ("6 6 2\n", "6\n"),
        ],
    },
    {
        "slug": "reverse-a-string",
        "title": "Reverse a String",
        "statement_md": (
            "## Problem\n"
            "Read a string and print it in reverse order.\n\n"
            "### Example\nInput: `hello`\n\nOutput: `olleh`"
        ),
        "constraints_md": "The input contains one non-empty line.",
        "difficulty": "easy",
        "expected_time_sec": 420,
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "technique_tags": ["strings", "iteration"],
        "topic_slug": "strings",
        "starter_code": {
            "python": "s = input()\n# Write your code below\n"
        },
        "tests": [
            ("hello\n", "olleh\n"),
            ("python\n", "nohtyp\n"),
            ("a\n", "a\n"),
        ],
    },
    {
        "slug": "find-maximum-in-array",
        "title": "Find Maximum in an Array",
        "statement_md": (
            "## Problem\n"
            "Read `n`, followed by `n` integers. Print the largest integer.\n\n"
            "### Example\nInput:\n`5`\n`3 8 2 9 4`\n\nOutput: `9`"
        ),
        "constraints_md": "1 <= n <= 100000.",
        "difficulty": "easy",
        "expected_time_sec": 600,
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "technique_tags": ["arrays", "iteration"],
        "topic_slug": "arrays",
        "starter_code": {
            "python": (
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "# Write your code below\n"
            )
        },
        "tests": [
            ("5\n3 8 2 9 4\n", "9\n"),
            ("3\n-5 -2 -9\n", "-2\n"),
            ("1\n42\n", "42\n"),
        ],
    },
    {
        "slug": "assessment-two-sum",
        "title": "Two Sum",
        "statement_md": (
            "## Problem\n"
            "Given an array of integers and a target, find the indices "
            "of two distinct elements whose sum equals the target.\n\n"
            "Print the two indices in ascending order. Exactly one valid "
            "pair exists.\n\n"
            "### Example\n"
            "Input:\n"
            "`4`\n`2 7 11 15`\n`9`\n\n"
            "Output: `0 1`"
        ),
        "constraints_md": (
            "2 <= n <= 100000. "
            "Array elements and target are integers."
        ),
        "difficulty": "medium",
        "expected_time_sec": 900,
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "technique_tags": ["arrays", "hash-map", "complement-search"],
        "topic_slug": "arrays",
        "starter_code": {
            "python": (
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "target = int(input())\n"
                "# Write your code below\n"
            )
        },
        "tests": [
            ("4\n2 7 11 15\n9\n", "0 1\n"),
            ("3\n3 2 4\n6\n", "1 2\n"),
            ("4\n3 3 2 4\n6\n", "0 1\n"),
            ("4\n-1 -2 -3 -4\n-6\n", "1 3\n"),
        ],
    },
]


def seed_problems() -> None:
    session_factory = get_session_factory()

    with session_factory() as session:
        try:
            # Check that every topic already exists.
            topic_slugs = {p["topic_slug"] for p in PROBLEMS}

            topics = session.scalars(
                select(Topic).where(Topic.slug.in_(topic_slugs))
            ).all()

            topics_by_slug = {
                topic.slug: topic for topic in topics
            }

            missing = topic_slugs - topics_by_slug.keys()

            if missing:
                raise RuntimeError(
                    "These topics do not exist in the database: "
                    + ", ".join(sorted(missing))
                    + ". Check the existing topic seed data first."
                )

            for data in PROBLEMS:
                existing = session.scalar(
                    select(Problem).where(
                        Problem.slug == data["slug"]
                    )
                )

                if existing:
                    print(f"Already exists; skipped: {data['slug']}")
                    continue

                problem = Problem(
                    slug=data["slug"],
                    title=data["title"],
                    statement_md=data["statement_md"],
                    constraints_md=data["constraints_md"],
                    difficulty=data["difficulty"],
                    expected_time_sec=data["expected_time_sec"],
                    optimal_time_complexity=data["optimal_time_complexity"],
                    optimal_space_complexity=data["optimal_space_complexity"],
                    technique_tags=data["technique_tags"],
                    starter_code=data["starter_code"],
                    status="published",
                    version=1,
                    is_diagnostic=False,
                )

                session.add(problem)
                session.flush()

                topic = topics_by_slug[data["topic_slug"]]

                session.add(
                    ProblemTopic(
                        problem_id=problem.id,
                        topic_id=topic.id,
                        is_primary=True,
                    )
                )

                for index, (stdin, expected_stdout) in enumerate(
                    data["tests"], start=1
                ):
                    session.add(
                        ProblemTestCase(
                            problem_id=problem.id,
                            problem_version=1,
                            case_index=index,
                            stdin=stdin,
                            expected_stdout=expected_stdout,
                            is_hidden=index > 1,
                        )
                    )

                print(f"Added: {data['slug']}")

            session.commit()
            print("Problem seeding completed.")

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_problems()
