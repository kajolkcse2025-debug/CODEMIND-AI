# API reference (Phase 1)

Base path: `/api/v1`. JSON only. Interactive docs (development only): `/docs`.
The machine-readable schema is exported to `packages/shared/openapi.json`, and the frontend's
TypeScript types are generated from it (`npm run gen:api`).

## Conventions

| Topic | Rule |
|---|---|
| Authentication | `Authorization: Bearer <Firebase ID token>` on every endpoint except the two health probes. Identity comes only from the verified token. No endpoint takes a user id. |
| Request id | Every response has `X-Request-ID`. A client may send its own (8-64 chars of `A-Za-z0-9._-`); otherwise one is generated. The same id appears in error bodies and logs. |
| Field names | `snake_case` |
| Unknown request fields | Rejected with 422 (so a client cannot smuggle in `user_id`) |

### Error envelope

Every error, including 404, 405, 422 and 500, has this shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid data.",
    "details": { "errors": [ { "field": "cgpa", "issue": "Input should be less than or equal to 10" } ] },
    "request_id": "8f3c9e0d5b1a4e6f9a2b7c1d3e5f7a90"
  }
}
```

| HTTP | `code` | When |
|---|---|---|
| 401 | `unauthenticated` | Missing/invalid/expired/revoked token. `details.reason` is `missing_token`, `token_invalid`, `token_expired` or `token_revoked`. Response includes `WWW-Authenticate: Bearer`. |
| 403 | `account_pending_deletion` | The account is scheduled for deletion |
| 404 | `not_found`, `profile_not_found` | Unknown route, or no profile yet |
| 405 | `method_not_allowed` | |
| 409 | `profile_exists`, `email_in_use` | Creating a second profile; two Firebase accounts claiming one e-mail |
| 422 | `validation_error` | `details.errors` lists `{field, issue}` per problem |
| 429 | `rate_limited` | Reserved: rate limiting is not enabled in Phase 1 |
| 500 | `internal_error` | Generic message only; details are in server logs under the request id |
| 503 | `auth_unavailable`, `auth_not_configured`, `service_unavailable` | Firebase certificates unreachable; server has no Firebase credentials configured |

## Endpoints

### `GET /health` (public)

Liveness. `200 {"status": "ok"}`.

### `GET /health/ready` (public)

Checks PostgreSQL and Redis. `200` when both are fine, `503` otherwise. Never includes
connection details.

```json
{ "status": "ok", "checks": { "database": "ok", "redis": "ok" } }
```

### `GET /me`

The authenticated user's application record, created on first sight.

```json
{
  "user": {
    "id": "6c1f1c4e-6a58-4b7e-8d5f-0e3c2f6a9b11",
    "email": "asha@example.com",
    "display_name": null,
    "role": "student",
    "onboarding_status": "complete",
    "assessment_status": "not_started",
    "xp_total": 0,
    "level": 1,
    "created_at": "2026-01-01T09:00:00Z"
  },
  "profile": null,
  "flags": { "email_verified": true }
}
```

`profile` is `null` until the student creates one. `email_verified` comes from the verified token.

### `GET /profile`

`200` with the profile, or `404 profile_not_found`.

### `POST /profile`

Create the profile (once). `201` with the profile, `409 profile_exists` if one exists, including when
two submissions race (exactly one wins; the other gets 409, never 500).
Creating the profile sets `onboarding_status` to `complete`.

### `PUT /profile`

Replaces the editable fields (full replacement: omitted optional fields reset to `null`/default).
`404 profile_not_found` if none exists.

#### Profile fields

| Field | Type | Rules |
|---|---|---|
| `name` | string | **required**, 1-100 chars |
| `college`, `degree`, `dream_company`, `dream_role` | string or null | max 120 chars; blank becomes null |
| `current_year` | integer or null | 1-8 |
| `cgpa` | number or null | >= 0, at most 2 decimals, not above `cgpa_scale` |
| `cgpa_scale` | 4, 5 or 10 | default 10 |
| `skills` | string[] | max 30; each 1-40 chars of letters, digits, space and `+ # . - / ( )`; case-insensitive de-duplication |
| `target_package_lpa` | number or null | 0 to under 10000, at most 2 decimals |
| `github_username` | string or null | valid GitHub username (not a URL) |
| `linkedin_url` | string or null | `https://[xx.]linkedin.com/in/<name>` only |
| `leetcode_username` | string or null | letters, digits, `_`, `-`, max 40 |
| `codeforces_username` | string or null | 3-24 chars: letters, digits, `_`, `-`, `.` |
| `timezone` | string | valid IANA name, default `UTC` |
| `daily_minutes` | integer or null | 15-720 |
| `preferred_language` | `python`, `java`, `cpp` or null | |

Example:

```http
POST /api/v1/profile
Authorization: Bearer <token>
Content-Type: application/json

{ "name": "Asha Kumar", "college": "IIT Madras", "current_year": 3, "cgpa": 8.75,
  "skills": ["Python", "SQL"], "timezone": "Asia/Kolkata", "daily_minutes": 90,
  "preferred_language": "python" }
```

The response has the same fields plus `created_at` and `updated_at`. Skills are returned in
alphabetical order, using the first-seen display spelling.

## Not available yet

Assessment, problems, attempts, coach, concepts, analytics, Coding DNA, weaknesses, roadmap,
missions, interviews, readiness, resumes, GitHub, data export/deletion. See the blueprint
(section 17) for the planned surface.
