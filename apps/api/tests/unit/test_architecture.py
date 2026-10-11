"""Static checks for the layering rules in the blueprint (section 5.1)."""

import ast
from pathlib import Path

APP = Path(__file__).parents[2] / "app"


def _imports(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def _violations(
    folder: str, forbidden: tuple[str, ...], *, skip: tuple[str, ...] = ()
) -> list[str]:
    result: list[str] = []
    for file in (APP / folder).rglob("*.py"):
        if file.name in skip:
            continue
        for module in _imports(file):
            if module.startswith(forbidden):
                result.append(f"{file.relative_to(APP)} imports {module}")
    return result


def test_routers_do_not_touch_the_database_or_repositories() -> None:
    # deps.py is the one place that wires sessions into services. Routers may name ORM classes
    # (e.g. ``User``) purely as type annotations, but never import sqlalchemy, sessions or repos.
    forbidden = ("sqlalchemy", "app.repositories", "app.db")
    assert _violations("api", forbidden, skip=("deps.py",)) == []


def test_services_do_not_depend_on_the_web_framework() -> None:
    assert _violations("services", ("fastapi", "starlette", "app.api")) == []


def test_repositories_do_not_contain_business_logic_dependencies() -> None:
    assert _violations("repositories", ("fastapi", "app.services", "app.api", "app.ai")) == []


def test_ai_vendor_sdks_are_not_imported_anywhere_yet() -> None:
    assert _violations("", ("google.generativeai", "google.genai", "vertexai", "openai")) == []


def test_only_the_ai_package_may_be_named_after_a_provider() -> None:
    outside = [
        str(file.relative_to(APP))
        for file in APP.rglob("*.py")
        if "gemini" in file.read_text().lower()
        and "app/ai/" not in file.as_posix()
        and file.name not in ("config.py",)
    ]
    assert outside == []
