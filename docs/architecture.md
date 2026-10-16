# Architecture (as built in Phase 1)

The approved blueprint is the source of truth for where the product is going. This document
describes what exists now and where Phase 1 deliberately differs from the blueprint.

## System

```
Browser (React SPA)
  Firebase JS SDK: sign-in only
  ApiClient: attaches ID token, refreshes once on 401, parses error envelope
        |  HTTPS, Authorization: Bearer <Firebase ID token>
        v
FastAPI (apps/api)
  middleware: request id -> CORS
  routers (app/api/v1)      validate input, call services, no DB access
  services (app/services)   business logic, transaction boundaries
  repositories              all SQLAlchemy queries
  models (app/models)       25 tables
  analytics (app/analytics) PURE functions: no I/O of any kind
  ai (app/ai)               AIProvider interface + Fake + Gemini stub
  integrations/code_runner  CodeRunner interface + FakeCodeRunner
  core                      errors, security (token verification), redis, middleware
        |
        +--> PostgreSQL (source of truth)       +--> Redis (KeyValueStore seam)
        +--> Firebase Admin SDK (token verification only)
```

Modular monolith, one deployable. The code runner (Judge0) will be the only separate service,
and only in a later phase.

## Layer rules and how they are enforced

| Rule | Enforced by |
|---|---|
| Routers do not import SQLAlchemy, sessions or repositories | `tests/unit/test_architecture.py` |
| Services do not import FastAPI | `tests/unit/test_architecture.py` |
| Repositories do not import services, API or AI | `tests/unit/test_architecture.py` |
| `app/analytics` imports no framework, DB, network or AI module | `tests/unit/test_analytics.py` |
| Gemini is named only inside `app/ai` (and config) | `tests/unit/test_architecture.py` |
| No vendor AI SDK is imported anywhere | `tests/unit/test_architecture.py` |
| Frontend never calls `fetch` outside the API client | ESLint `no-restricted-globals` |
| Identity comes only from a verified token | `tests/api/test_auth_and_me.py` |
| The committed OpenAPI schema (and generated TS types) match the app | `test_committed_openapi_schema_matches_the_running_app` |
| `docs/database.md` lists every table | `test_committed_database_docs_list_every_table` |
| Unverified results never count | `RunResult.counts_toward_metrics`, `analytics.verified_only`, DB `CHECK unavailable_is_unverified`, and their tests |

## Authentication flow

1. The browser signs in with Firebase and receives a short-lived ID token.
2. `ApiClient` sends it as a Bearer token. No cookies are used, so classic CSRF does not apply.
3. `get_verified_token` verifies it with the Firebase Admin SDK. Failures return `401` with a
   `details.reason` (`missing_token`, `token_invalid`, `token_expired`, `token_revoked`).
   If Firebase's certificates cannot be fetched the API returns `503 auth_unavailable`, not 401.
4. `get_current_user` provisions the application user with a race-safe
   `INSERT ... ON CONFLICT` keyed by the verified Firebase uid. No endpoint accepts a user id.
5. Accounts marked `pending_deletion` get `403 account_pending_deletion`.

## Concurrency rules

Found and fixed during verification, each with a regression test (`tests/integration/test_concurrency.py`,
`tests/unit/test_security.py`):

- Lazy Firebase app initialisation is serialised with a lock and tolerates another initialiser.
- A duplicate `POST /profile` is decided by the primary key and mapped to `409`, never `500`.
- Skill upserts insert in sorted order and never update existing rows, so concurrent writers cannot
  deadlock (PostgreSQL 40P01).
- First-request user provisioning is a single `INSERT ... ON CONFLICT`.

## The three seams

- **AI** (`app/ai`): `AIProvider` has `generate_text`, `generate_structured`, `stream_text`.
  `FakeAIProvider` returns only what a test scripts. `GeminiProvider` calls nothing and raises
  `AIUnavailableError`. `build_ai_provider` picks the implementation from configuration, and
  `AI_PROVIDER=fake` is refused in staging and production.
- **Code execution** (`integrations/code_runner`): `CodeRunner.run(RunRequest) -> RunResult`.
  `FakeCodeRunner` always returns `runner_unavailable`, `verified=False`. It executes nothing
  (a test proves submitted code is never run).
- **Analytics** (`app/analytics`): `calculate_topic_mastery`, `calculate_coding_dna`,
  `detect_weaknesses`, `calculate_readiness`. They apply the verified-only gate for real but
  implement **no scoring formula**, so they always return `score=None`, `state=unavailable`
  and a `reason`. Formulas arrive in a later phase (blueprint sections 9, 10, 11, 15).

## Data model

25 tables, created by one migration (`0001`). Constraints encode honesty rules, for example a
`coding_dna` row in `calibrating` state cannot have a score, and a `runner_unavailable`
submission cannot be marked verified. Details in [database.md](database.md).

## Deviations from the blueprint (intentional, for Phase 1)

| Blueprint | Phase 1 | Why |
|---|---|---|
| Tables such as `user_consents`, `topic_prerequisites`, `problem_test_cases`, `problem_hints`, `hint_events`, `xp_events`, `active_days`, `revision_queue`, `readiness_snapshots`, `coding_dna_snapshots`, `ai_messages`, `ai_usage_events`, `notifications`, `resumes`, `github_profiles`, `company_profiles` | Not created | Not in the Phase 1 schema list; each arrives with the feature that needs it |
| `profiles.dream_company_id` FK to companies | `dream_company` free text | There is no company table yet |
| Error `details` as an array | `details` is an object: `{"errors": [{"field", "issue"}]}` | Phase 1 spec fixed `details` as `{}` |
| Onboarding completed by an explicit endpoint with consents | Creating the profile sets `onboarding_status=complete` | Consents and the 18+ confirmation are not built yet |
| Topic `interview_weight` tuned per topic | Seeded at 1.00 for all | It is an assumption; no data justifies other values yet |
| Recharts, CodeMirror 6 | Not installed | Nothing uses them yet. Added with the first feature that does |
| Async SQLAlchemy was an option | Synchronous sessions, `def` endpoints | Simpler and robust; FastAPI runs them in a thread pool |

## Not built (by design)

Diagnostic assessment, problem bank, Judge0, real Coding DNA / mastery / weakness / readiness
calculations, roadmap and mission generation, AI coach and teacher, mock interviews, company
mode, resume and GitHub analysis, XP/streak logic, notifications, data export and deletion
endpoints, rate limiting (Redis seam only), CI pipeline, deployment configuration.
