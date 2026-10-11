# Development guide

## Daily workflow

```bash
docker compose up -d                       # PostgreSQL + Redis
cd apps/api && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000  # API
# new terminal, repo root:
npm run dev:web                            # web app
```

## First-time setup

See the README quick start. Extra notes:

- The test suite needs its own database. With Docker Compose:
  `docker compose exec postgres createdb -U codemind codemind_test`.
  Tests use `TEST_DATABASE_URL` (default `postgresql+psycopg://codemind:codemind@localhost:5432/codemind_test`;
  override it if your password differs) and `TEST_REDIS_URL` (default database 15).
  They never touch your development database.
- If `.env` is missing the API refuses to start with a message naming the missing variables.

## Common tasks

### Add or change a table

1. Edit/add the model in `apps/api/app/models/` (and import it in `models/__init__.py`).
2. `alembic revision --autogenerate -m "describe the change" --rev-id 0002`
3. **Read the generated migration.** Autogenerate misses some things and sometimes adds noise.
4. `alembic upgrade head && alembic check` (must report no new operations).
5. `pytest tests/integration` (it also verifies models and migrations have not drifted).
6. Regenerate the reference: `python -m app.cli describe-schema` and update `docs/database.md`.

Production migrations should be backward compatible (add nullable, backfill, switch, drop later).

### Add an endpoint

1. **Schema** in `app/schemas/` (Pydantic; `extra="forbid"` for request bodies).
2. **Repository** method for any query. Every user-owned query takes the user's id.
3. **Service** method with the logic and transaction boundary.
4. **Router** that only validates, depends on `get_current_user` and a service, and returns.
   Add `responses={...: {"model": ErrorResponse}}` so the OpenAPI schema documents errors.
5. Tests: happy path, unauthenticated (401), validation (422), and that another user cannot
   reach the data (404).
6. `npm run gen:api` so the frontend types follow.

### Regenerate the shared API types

```bash
npm run gen:api     # exports openapi.json from the API, regenerates packages/shared/src/api.ts
```

### Add a UI component

Components in `apps/web/src/components/ui` follow the shadcn/ui pattern (Radix + cva + Tailwind
tokens) and were written by hand. `components.json` is present, so
`npx shadcn@latest add <name>` works where you have network access.

### Seed data

`python -m app.cli seed-topics` is idempotent. Re-running it never overwrites a tuned
`interview_weight`.

## Local authentication without a Firebase project

You can use the Firebase Authentication emulator (`npm i -g firebase-tools`, then
`firebase emulators:start --only auth --project demo-codemind`). Then set:

- API: `FIREBASE_AUTH_EMULATOR_HOST=localhost:9099`, `FIREBASE_PROJECT_ID=demo-codemind`
- Web: `VITE_FIREBASE_AUTH_EMULATOR_URL=http://localhost:9099`, plus any placeholder values for
  the other `VITE_FIREBASE_*` variables (for example `demo-key`, `localhost`, `demo-codemind`,
  `1:1:web:1`).

The API refuses to start with the emulator enabled in staging or production, because the
emulator issues unsigned tokens. The emulator flow itself was not run during Phase 1 development
(no emulator binaries were reachable); the backend's verification of emulator-style tokens is
covered by `tests/unit/test_security.py`.

## Quality gates

| Check | Command |
|---|---|
| Lint / format (API) | `ruff check . && ruff format --check .` |
| Types (API, strict) | `mypy` |
| Tests (API) | `pytest` |
| Migrations | `alembic upgrade head && alembic check` |
| Types (web, strict) | `npm run typecheck:web` |
| Lint (web) | `npm run lint:web` |
| Tests (web) | `npm run test:web` |
| Production build | `npm run build:web` |

## Troubleshooting

- **`PostgreSQL is not reachable at TEST_DATABASE_URL`**: start Postgres and create `codemind_test`.
- **`auth_not_configured` (503) from the API**: Firebase credentials or the emulator are not
  configured. This is expected until you complete the Firebase setup.
- **Sign-in page says Firebase is not configured**: fill `apps/web/.env` and restart Vite
  (environment variables are read at startup).
- **CORS errors in the browser**: add your web origin to `CORS_ALLOWED_ORIGINS` and restart the API.
- **`npm install` reports a missing package when generating types**: delete `node_modules` and
  `package-lock.json`, then run `npm install` again.
