
"""Question bank for CodeMind AI coding assessments.

This module defines the question format and validates the bank.
It does not access the database or execute submitted code.
"""

from dataclasses import dataclass
from typing import Literal


Difficulty = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class CodingTestCase:
    """One input and its expected output."""

    stdin: str
    expected_stdout: str


@dataclass(frozen=True)
class CodingAssessmentQuestion:
    """The information needed to present and validate a coding question."""

    slug: str
    title: str
    topic_slug: str
    difficulty: Difficulty
    statement_md: str
    constraints_md: str
    starter_code: str
    expected_time_sec: int
    optimal_time_complexity: str
    optimal_space_complexity: str
    technique_tags: tuple[str, ...]
    test_cases: tuple[CodingTestCase, ...]
    diagnostic_level: int



QUESTION_BANK: tuple[CodingAssessmentQuestion, ...] = (
    CodingAssessmentQuestion(
        slug="assessment-second-largest",
        title="Second Largest Distinct Number",
        topic_slug="arrays",
        difficulty="easy",
        statement_md=(
            "Read an integer n followed by n integers. Print the second "
            "largest distinct number. If it does not exist, print -1."
        ),
        constraints_md="2 <= n <= 100000",
        starter_code=(
            "n = int(input())\n"
            "nums = list(map(int, input().split()))\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=600,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
        technique_tags=("arrays", "distinct-values"),
        diagnostic_level=1,
        test_cases=(
            CodingTestCase("5\n1 5 3 5 2\n", "3\n"),
            CodingTestCase("4\n7 7 7 7\n", "-1\n"),
            CodingTestCase("3\n-5 -2 -9\n", "-5\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-palindrome-string",
        title="Check a Palindrome",
        topic_slug="strings",
        difficulty="easy",
        statement_md=(
            "Read a string and print True if it reads the same forward "
            "and backward; otherwise print False. Comparison is "
            "case-sensitive and includes spaces."
        ),
        constraints_md="1 <= length of string <= 100000",
        starter_code=(
            "s = input()\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=600,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
        technique_tags=("strings", "reversal"),
        diagnostic_level=1,
        test_cases=(
            CodingTestCase("madam\n", "True\n"),
            CodingTestCase("hello\n", "False\n"),
            CodingTestCase("abba\n", "True\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-two-sum",
        title="Two Sum",
        topic_slug="hashing",
        difficulty="medium",
        statement_md=(
            "Read n, then n integers, then a target. Print the two "
            "zero-based indices of distinct elements that add to the "
            "target, in increasing index order. If no pair exists, "
            "print -1."
        ),
        constraints_md="2 <= n <= 100000",
        starter_code=(
            "n = int(input())\n"
            "nums = list(map(int, input().split()))\n"
            "target = int(input())\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=900,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
        technique_tags=("hash-map", "complement"),
        diagnostic_level=2,
        test_cases=(
            CodingTestCase("4\n2 7 11 15\n9\n", "0 1\n"),
            CodingTestCase("3\n3 2 4\n6\n", "1 2\n"),
            CodingTestCase("3\n1 2 3\n7\n", "-1\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-longest-unique-substring",
        title="Longest Substring Without Repeating Characters",
        topic_slug="sliding-window",
        difficulty="medium",
        statement_md=(
            "Read a string and print the length of its longest substring "
            "that contains no repeated characters."
        ),
        constraints_md="0 <= length of string <= 100000",
        starter_code=(
            "s = input()\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=1200,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(min(n, alphabet_size))",
        technique_tags=("sliding-window", "last-seen-index"),
        diagnostic_level=2,
        test_cases=(
            CodingTestCase("abcabcbb\n", "3\n"),
            CodingTestCase("bbbbb\n", "1\n"),
            CodingTestCase("pwwkew\n", "3\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-two-sum-sorted",
        title="Two Sum in a Sorted Array",
        topic_slug="two-pointer",
        difficulty="medium",
        statement_md=(
            "Read n, then n integers in non-decreasing order, then a "
            "target. Print the zero-based indices of two distinct "
            "elements that add to the target, in increasing index "
            "order. If no pair exists, print -1."
        ),
        constraints_md="2 <= n <= 100000",
        starter_code=(
            "n = int(input())\n"
            "nums = list(map(int, input().split()))\n"
            "target = int(input())\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=900,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(1)",
        technique_tags=("two-pointers", "sorted-array"),
        diagnostic_level=2,
        test_cases=(
            CodingTestCase("4\n1 2 4 7\n6\n", "1 2\n"),
            CodingTestCase("5\n1 2 3 4 5\n9\n", "-1\n"),
            CodingTestCase("2\n-3 3\n0\n", "0 1\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-binary-search",
        title="Binary Search",
        topic_slug="binary-search",
        difficulty="easy",
        statement_md=(
            "Read n, then n integers in non-decreasing order, then a "
            "target. Print the target's zero-based index, or -1 if "
            "it does not occur."
        ),
        constraints_md="0 <= n <= 100000",
        starter_code=(
            "n = int(input())\n"
            "nums = list(map(int, input().split())) if n else []\n"
            "target = int(input())\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=600,
        optimal_time_complexity="O(log n)",
        optimal_space_complexity="O(1)",
        technique_tags=("binary-search", "sorted-array"),
        diagnostic_level=1,
        test_cases=(
            CodingTestCase("5\n1 3 5 7 9\n7\n", "3\n"),
            CodingTestCase("4\n2 4 6 8\n5\n", "-1\n"),
            CodingTestCase("1\n10\n10\n", "0\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-linked-list-cycle",
        title="Detect a Cycle in a Linked List",
        topic_slug="linked-list",
        difficulty="hard",
        statement_md=(
            "A linked list is represented by n node values and a "
            "zero-based index pos. The final node points to pos; "
            "pos = -1 means it points to nothing. Print True if the "
            "list contains a cycle, otherwise print False."
        ),
        constraints_md="0 <= n <= 100000; -1 <= pos < n",
        starter_code=(
            "n = int(input())\n"
            "values = list(map(int, input().split())) if n else []\n"
            "pos = int(input())\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=1500,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(1)",
        technique_tags=("linked-list", "fast-slow-pointers"),
        diagnostic_level=3,
        test_cases=(
            CodingTestCase("3\n3 2 0\n1\n", "True\n"),
            CodingTestCase("3\n1 2 3\n-1\n", "False\n"),
            CodingTestCase("1\n1\n0\n", "True\n"),
        ),
    ),
    CodingAssessmentQuestion(
        slug="assessment-climbing-stairs",
        title="Climbing Stairs",
        topic_slug="dynamic-programming",
        difficulty="medium",
        statement_md=(
            "You are climbing n stairs. Each move can climb either "
            "one or two stairs. Print the number of distinct ways "
            "to reach the top."
        ),
        constraints_md="1 <= n <= 45",
        starter_code=(
            "n = int(input())\n"
            "\n"
            "# Write your solution below\n"
        ),
        expected_time_sec=900,
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(1)",
        technique_tags=("dynamic-programming", "fibonacci"),
        diagnostic_level=2,
        test_cases=(
            CodingTestCase("2\n", "2\n"),
            CodingTestCase("3\n", "3\n"),
            CodingTestCase("5\n", "8\n"),
        ),
    ),
)



def validate_question_bank(
    questions: tuple[CodingAssessmentQuestion, ...],
) -> list[str]:
    """Return validation errors; an empty list means the bank is valid."""

    errors: list[str] = []
    seen_slugs: set[str] = set()

    for question in questions:
        if question.slug in seen_slugs:
            errors.append(f"Duplicate question slug: {question.slug}")
        seen_slugs.add(question.slug)

        if not question.slug.strip():
            errors.append("Question slug cannot be empty.")

        if question.topic_slug not in {
            "arrays",
            "strings",
            "hashing",
            "sliding-window",
            "two-pointer",
            "binary-search",
            "linked-list",
            "dynamic-programming",
        }:
            errors.append(
                f"{question.slug}: unsupported assessment topic "
                f"'{question.topic_slug}'."
            )

        if question.difficulty not in {"easy", "medium", "hard"}:
            errors.append(f"{question.slug}: invalid difficulty.")

        if not question.statement_md.strip():
            errors.append(f"{question.slug}: statement cannot be empty.")

        if question.expected_time_sec <= 0:
            errors.append(f"{question.slug}: expected time must be positive.")

        if question.diagnostic_level not in {1, 2, 3}:
            errors.append(f"{question.slug}: diagnostic level must be 1, 2, or 3.")

        if not question.test_cases:
            errors.append(f"{question.slug}: at least one test case is required.")

        for index, case in enumerate(question.test_cases, start=1):
            if not case.expected_stdout.strip():
                errors.append(
                    f"{question.slug}: test case {index} has empty expected output."
                )

    return errors
