# CodeMind AI

CodeMind AI is a personalised coding mentor and interview-preparation platform for software
engineering students. Its core loop is:

```
Student activity -> Capture -> Deterministic analysis -> Student intelligence profile
      ^                                                          |
      |                                                          v
New activity  <-  Personalised action  <-  Recommendation  <------+
```

Numbers (accuracy, mastery, scores, streaks, readiness) are computed by deterministic backend
code. AI is used only for language: explanations, coaching, interview conversation. It never
produces a score.

> **Status: Phase 1 (foundation).** This repository currently provides the platform everything
> else will be built on: authentication, user/profile, database schema, API conventions, the
> AI and code-runner seams, the pure analytics package structure, and the UI shell. There is **no
> diagnostic, problem bank, coach, scoring, roadmap or missions yet**, and the UI says so rather
> than showing placeholder numbers.

## What works today

| Area | Status |
|---|---|
| Sign up / sign in (email + password, Google), password reset | Frontend via Firebase; backend verifies ID tokens |
| `GET /api/v1/me`, `GET/POST/PUT /api/v1/profile` | Working, validated, tested |
| `GET /api/v1/health`, `/health/ready` | Working (readiness checks Postgres and Redis) |
| PostgreSQL schema (25 tables) + Alembic migration | Applied and drift-checked |
| 17 canonical topics (seeded) | Working (`python -m app.cli seed-topics`) |
| `AIProvider` + `FakeAIProvider` + `GeminiProvider` (stub) | Interface only; no model is called |
| `CodeRunner` + `FakeCodeRunner` | Always `runner_unavailable`, never counts toward metrics |
| `app/analytics` (mastery, DNA, weaknesses, readiness) | Interfaces only; never returns a score |
| Web app shell, themes, route guards, reusable components | Working |
| Assessment, coach, roadmap, missions, analytics, Coding DNA, interview | "Coming soon" pages |

## Repository layout

```
codemind-ai/
  apps/
    api/            FastAPI modular monolith (routers -> services -> repositories -> models)
    web/            React + TypeScript + Vite + Tailwind + shadcn-style components
  packages/
    shared/         OpenAPI schema + generated TypeScript types (single source of API types)
  docs/             architecture, development, API, database
  docker-compose.yml   PostgreSQL + Redis for local development
  .env.example         every environment variable (copy to .env)
```

## Prerequisites

- Python 3.11+
- Node.js 20.19+ (developed on 22) and npm
- Docker (for local PostgreSQL and Redis), or your own Postgres 14+ and Redis
- A Firebase project (see [Manual setup](#manual-setup-you-must-do))

## Quick start

```bash
# 1. Configuration
cp .env.example .env                      # then edit passwords/Firebase values
cp apps/web/.env.example apps/web/.env    # then fill in the VITE_FIREBASE_* values

# 2. Infrastructure (PostgreSQL + Redis)
docker compose up -d

# 3. Backend
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head                      # create the schema
python -m app.cli seed-topics             # insert the 17 canonical topics
uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal, from the repo root)
npm install
npm run dev:web                           # http://localhost:5173
```

API docs (development only): http://localhost:8000/docs

## Environment variables

Full, commented list in [`.env.example`](.env.example). Summary:

| Variable | Used by | Required | Notes |
|---|---|---|---|
| `DATABASE_URL` | API | yes | `postgresql+psycopg://...`; `postgres://` URLs from Railway are accepted |
| `REDIS_URL` | API | yes | |
| `CORS_ALLOWED_ORIGINS` | API | no | Comma-separated explicit origins; `*` is rejected |
| `ENVIRONMENT` | API | no | `development` (default), `test`, `staging`, `production` |
| `FIREBASE_PROJECT_ID`, `FIREBASE_SERVICE_ACCOUNT_B64` | API | staging/production | base64 of the service-account JSON |
| `FIREBASE_AUTH_EMULATOR_HOST` | API | no | Local-only; refused in staging/production |
| `AI_PROVIDER`, `GEMINI_API_KEY`, `AI_MODEL_FAST`, `AI_MODEL_STRONG` | API | no (Phase 1) | No AI call is made yet |
| `POSTGRES_USER/PASSWORD/DB` | docker compose | yes for compose | Local development only |
| `VITE_API_BASE_URL` | Web | production | Defaults to `http://localhost:8000` in dev only |
| `VITE_FIREBASE_API_KEY/AUTH_DOMAIN/PROJECT_ID/APP_ID` | Web | yes | Public identifiers, **not** secrets |
| `VITE_FIREBASE_AUTH_EMULATOR_URL` | Web | no | e.g. `http://localhost:9099` |

Secrets are never committed (`.env` is git-ignored) and never exposed to the browser. Anything
with a `VITE_` prefix is public by design.

## Running the checks

```bash
# Backend (from apps/api, venv active; Postgres and Redis running)
ruff check . && ruff format --check .
mypy
pytest                      # DB tests use TEST_DATABASE_URL (default: database "codemind_test")
pytest -m "not db and not redis"   # fast tests with no services

# Frontend (from the repo root)
npm run typecheck:web
npm run lint:web
npm run test:web
npm run build:web

# Migrations
cd apps/api && alembic upgrade head && alembic check
```

The test database must exist and be creatable by your DB user, for example:
`createdb codemind_test` (the test suite runs the real migrations against it, downgrading to base first).

## Manual setup you must do

1. **Firebase project:** create one, enable *Email/Password* and *Google* sign-in, add `localhost`
   (and later your Vercel domain) as an authorised domain.
2. **Web config:** put the web app's config values in `apps/web/.env`.
3. **Backend credentials:** create a service-account key, then
   `base64 -w0 service-account.json` into `FIREBASE_SERVICE_ACCOUNT_B64`. Alternatively, develop
   against the Firebase Auth emulator (see [docs/development.md](docs/development.md)).
4. **Deployment (later):** Vercel (frontend, root `apps/web`), Railway (API, Postgres, Redis).

## Engineering rules (enforced where possible)

- Routers validate and delegate; services hold logic; repositories touch the database.
- `app/analytics` is pure: no database, network, framework or AI imports (a test fails if it breaks).
- AI and code execution only through interfaces. Student code is never executed in the API.
- Unverified execution never affects mastery, XP, Coding DNA or readiness.
- No fake scores, statistics or "student intelligence" anywhere in the UI or API.
- Every schema change ships as an Alembic migration; CI-style drift checks live in the test suite.

## Documentation

- [docs/architecture.md](docs/architecture.md): structure, boundaries, deviations from the blueprint
- [docs/development.md](docs/development.md): daily workflow, adding endpoints/migrations, troubleshooting
- [docs/api.md](docs/api.md): endpoints, errors, conventions
- [docs/database.md](docs/database.md): schema reference and constraints
