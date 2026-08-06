# API Reference

Base URL: `/api/v1`

This is the JSON API surface intended for both the current web frontend's
AJAX calls and future clients (mobile). It is token-authenticated (JWT) and
independent of the session-cookie login used by the server-rendered HTML
pages (`routes/*.py`, not documented here).

## Versioning policy

`/api/v1` is frozen: existing endpoints won't have fields removed, renamed,
or change type under existing clients. New, optional fields may be added
to any response at any time (see "Response envelope conventions" below) —
clients should ignore keys they don't recognize rather than validating
against an exact/closed shape. Any change that isn't backward-compatible
in this sense ships as `/api/v2`, not as a modification to v1.

## Response envelope conventions

Two intentional patterns are in use, not one inconsistent one:

- **CRUD-style resources** (auth, profile, colleges, saved colleges,
  conversations) wrap their payload in a singular/plural key matching the
  resource: `{"user": {...}}`, `{"conversations": [...]}`,
  `{"conversation": {...}}`, `{"prediction": {...}}`.
- **Action/RPC-style endpoints** (`POST /predictor/predict`,
  `POST /comparison/compare`, `POST /ai/chat`) return a flatter,
  action-specific shape instead, e.g. `{"prediction_id", "results"}` — the
  response describes the result of an operation, not a single named
  resource, so it isn't wrapped the same way.

If you're building a generic client-side deserializer, dispatch on the
endpoint, not on a single universal envelope shape.

## Authentication

Obtain tokens via `POST /api/v1/auth/login`, then send the access token on
every subsequent request:

```
Authorization: Bearer <access_token>
```

- Access tokens expire after **30 minutes**.
- Refresh tokens expire after **30 days**.
- Call `POST /api/v1/auth/refresh` with the refresh token (as the bearer
  token) to obtain a new access token.
- **Deferred, tracked decision:** refresh tokens are not rotated (the same
  refresh token remains valid, unchanged, for its full 30-day lifetime
  across repeated `/refresh` calls) and there is no server-side revocation
  — logout is client-side only (discard the stored tokens). This is a
  known gap, not an oversight (see `ARCHITECTURE.md`'s "Known gaps"), and
  is worth revisiting before real users carry longer-lived mobile
  sessions, but isn't part of this contract freeze.

## Error format

Every error response, whether raised explicitly by a route or by an
unhandled exception/routing failure, uses the same envelope:

```json
{
  "error": {
    "code": "not_found",
    "message": "Conversation not found."
  }
}
```

`code` is a short machine-readable slug; `message` is a human-readable
string safe to show to a user. Common codes:

| Code | Status | Meaning |
|---|---|---|
| `missing_fields` | 400 | Required field(s) missing from the request body |
| `invalid_input` / `invalid_rank` / `invalid_title` | 400 | A field failed validation |
| `missing_token` | 401 | No `Authorization` header present |
| `invalid_credentials` | 401 | Wrong email/password on login |
| `token_expired` | 401 | Access/refresh token has expired |
| `invalid_token` | 422 | Malformed or unparseable token |
| `not_found` | 404 | Resource doesn't exist, or isn't owned by the caller |
| `email_taken` / `username_taken` | 409 | Signup conflict |
| `method_not_allowed` | 405 | Wrong HTTP method for the route |
| `chat_failed` / `internal_error` | 500 | Unexpected server-side failure |

Ownership checks (e.g. conversations, saved colleges, prediction/comparison
history) always return `404 not_found` rather than `403 forbidden` for
another user's resource, so existence isn't leaked.

Successful responses are unaffected by any of the above — this table only
describes the error path.

---

## Auth — `/api/v1/auth`

### `POST /signup`
Body: `{ "username", "email", "password" }`
→ `201 { "user": {...} }`
Errors: `missing_fields` (400), `email_taken` / `username_taken` (409)

### `POST /login`
Body: `{ "email", "password" }`
→ `200 { "access_token", "refresh_token", "user": {...} }`
Errors: `missing_fields` (400), `invalid_credentials` (401)

### `POST /refresh`
Auth: refresh token required.
→ `200 { "access_token" }`

### `GET /me`
Auth: access token required.
→ `200 { "user": {...} }`

**User object:** `{ id, username, email, created_at }`

---

## Predictor — `/api/v1/predictor`

All routes require an access token.

### `GET /options`
→ `200 { "exams": [...], "categories": [...], "quotas": [...] }`
(each item is `{ id, name }`)

### `POST /predict`
Body: `{ "exam", "category", "quota", "rank" }`
→ `200 { "prediction_id", "results": [...] }`
Errors: `missing_fields`, `invalid_rank` (rank not an integer), `invalid_input` (unknown exam/category/quota) — all 400

Each result item: `{ college_id, college, branch, exam, category, quota, round, year, closing_rank, avg_package, median_package, placement_rate, nirf_rank, fees, hostel_fees, website }`

### `GET /history`
→ `200 { "predictions": [...] }`
(each item is `{ id, exam, category, quota, rank, created_at }`)

### `GET /history/<id>`
→ `200 { "prediction": {...}, "results": [...] }`
Errors: `not_found` (404)

---

## Comparison — `/api/v1/comparison`

All routes require an access token.

### `GET /branches`
→ `200 { "branches": [...] }`
(each item is `{ id, branch_name, branch_code, intake, avg_package, median_package, placement_rate, college: {...} }`)

### `POST /compare`
Body: `{ "branch1_id", "branch2_id" }`
→ `200 { "comparison_id", "branch1": {...}, "branch2": {...} }`
Errors: `missing_fields` (400), `not_found` (404, unknown branch id)

### `GET /history`
→ `200 { "comparisons": [...] }`
(each item is `{ id, branch1, branch2, created_at }`)

---

## Colleges — `/api/v1/colleges`

### `GET /<id>`
No auth required (public read).
→ `200 { "college": { id, name, location, state, college_type, fees, hostel_fees, nirf_rank, website, branches: [...] } }`
Errors: `not_found` (404)

---

## Saved colleges — `/api/v1/saved`

All routes require an access token.

### `GET /`
→ `200 { "saved": [...] }`
(each item is `{ id, college: {...}, created_at }`)

### `POST /<college_id>`
Idempotent — saving an already-saved college returns the existing row.
→ `201 { "saved": {...} }`
Errors: `not_found` (404, unknown college id)

### `DELETE /<saved_id>`
→ `204` (empty body)
Errors: `not_found` (404)

---

## Profile — `/api/v1/profile`

### `GET /`
Auth required.
→ `200 { "user": {...} }`

---

## AI Counselor — `/api/v1/ai`

All routes require an access token.

### `POST /chat`
Body: `{ "message", "conversation_id"? }`. Omit `conversation_id` to start a
new conversation.
→ `200`:
```json
{
  "conversation_id": 42,
  "answer": "raw markdown text",
  "user_message": { "id", "role", "content", "created_at" },
  "assistant_message": {
    "id", "role", "content", "created_at",
    "blocks": [ { "type": "recommendation_card", "version": 1, "data": {...} } ]
  },
  "meta": { "elapsed_ms": 812 }
}
```
`content` is **raw markdown**, not pre-rendered HTML — the web frontend
renders it to HTML itself for DOM insertion; a mobile client should render
it with its own markdown component. `user_message` and `assistant_message`
use the exact same shape as messages returned by
`GET /conversations/<id>` (both are built by the one shared serializer) --
a client can treat a live chat response and a reloaded history message
identically, with no special-casing. See "Response blocks" below for the
`blocks` field.

Errors: `missing_fields` (400), `not_found` (404, if `conversation_id` is
given but doesn't belong to the caller), `chat_failed` (500)

### `GET /conversations`
→ `200 { "conversations": [...] }`, ordered by most recently active first.
(each item is `{ id, title, title_is_custom, created_at, updated_at }` —
no `messages` field; see detail endpoint)

Optional query param: `?q=<term>` filters by title (case-insensitive
substring match). Omitting it, or passing an empty/whitespace-only value,
returns the full unfiltered list -- existing callers are unaffected.

### `GET /conversations/<id>`
→ `200 { "conversation": { id, title, title_is_custom, created_at, updated_at, messages: [...] } }`
(each message is `{ id, role, content, created_at }`)
Errors: `not_found` (404)

### `PATCH /conversations/<id>`
Body: `{ "title" }`. Renaming sets `title_is_custom: true`, which locks the
title against future auto-generation.
→ `200 { "conversation": {...} }`
Errors: `missing_fields` (400, no `title` key), `invalid_title` (400, empty/whitespace-only), `not_found` (404)

### `DELETE /conversations/<id>`
→ `204` (empty body)
Errors: `not_found` (404)

### Response blocks

`assistant_message.blocks` (from `POST /chat`, and reconstructed nowhere
else -- see below) is always an array, possibly empty, of structured cards
alongside the prose answer:

```json
{ "type": "recommendation_card", "version": 1, "data": {...} }
```

Known `type` values today: `recommendation_card`, `prediction_card`,
`comparison_card`. Each block's `data` shape is specific to its `type` and
independently versioned via `version`, so a type can gain new `data`
fields, or a wholly new type can be introduced, without a coordinated
release across clients.

**Forward-compatibility contract (required of every client, including
ones not yet written):** if a block's `type` is unrecognized, or its
`version` is higher than the client knows how to render, the client
**must** skip that block silently and continue rendering everything else
in the response (the prose answer, and any other blocks). Do not error,
do not block rendering of the rest of the message. The web frontend
(`static/js/blocks.js`) already implements this — an unrecognized type
simply produces no DOM node. Any future client must do the same.

**Blocks are transient, not persisted.** They exist only in the response
to the `POST /chat` call that generated them. If that same conversation is
later reloaded via `GET /conversations/<id>`, its messages carry `content`
and `role` only -- `blocks` is not present and is not reconstructed, even
if the original live response included cards. This is intentional, not a
bug: don't design a client that assumes historical messages will have
their original blocks available.

---

## Pagination

Not yet implemented on any list endpoint (`/predictor/history`,
`/comparison/history`, `/saved`, `/ai/conversations`) -- they currently
return the full, unbounded list. This is safe to add later without a
breaking change, since every list response is already wrapped in a named
object rather than returned as a bare top-level array (e.g.
`{"conversations": [...]}`, not `[...]`) -- a page/cursor field can be
added alongside the existing array key.

Parameter names are committed now, ahead of implementation, so that
whichever endpoint gets pagination first doesn't set an inconsistent
precedent for the others: cursor-based, using `?cursor=` (opaque, from the
previous response) and `?limit=` (page size), with the response adding a
`next_cursor` key (`null` when there are no more results) alongside the
existing array.

## Not yet implemented

- Pagination — see above; contract is decided, implementation is deferred.
- Server-side JWT revocation / refresh-token rotation — see "Authentication" above.
