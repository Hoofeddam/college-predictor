# Architecture

Flask + PostgreSQL application for JEE/JoSAA college prediction, comparison,
and an AI counselor chat. Two client surfaces exist side by side:

- **Web** — server-rendered Jinja2 templates + vanilla JS (AJAX for the chat
  page), authenticated via Flask-Login session cookies.
- **JSON API** (`/api/v1/*`) — authenticated via JWT (Flask-JWT-Extended).
  This is the surface a future mobile client should use exclusively. See
  [`API.md`](API.md) for the full endpoint reference.

## Request flow and the two auth models

```
Browser  ──(session cookie)──>  routes/*.py            ──┐
                                                           ├──> services/*.py ──> models.py (SQLAlchemy) ──> PostgreSQL
Mobile / ──(JWT bearer token)──>  routes/api/*.py       ──┘
API client
```

Both entry points are kept thin and are expected to call into the same
`services/*.py` functions for business logic, so behavior stays identical
regardless of which client is used. This pattern is fully in place for
conversations (`services/ai_service.py`); it is **not yet** consistently
applied to prediction/comparison history-recording, where the web and API
routes each independently write their own `PredictionHistory` /
`ComparisonHistory` rows (see *Known gaps* below).

There is no database schema difference between the two auth models — a
user's data is identical whether they use the web app or the API.

## Error handling

All `/api/v1/*` responses use one JSON envelope, `{"error": {"code",
"message"}}`, for every failure mode: explicit validation errors returned
by a route, Flask routing errors (404/405) for unmatched API paths, JWT
auth failures (missing/invalid/expired token), and unexpected exceptions.
This is registered once, in `routes/api/errors.py`
(`register_api_error_handlers`), and wired into `app.py`. Non-API routes
are untouched and keep Flask's normal HTML error pages. Full error code
reference: [`API.md`](API.md#error-format).

## Configuration and secrets

`config.py` reads everything (`SECRET_KEY`, `JWT_SECRET_KEY`,
`DATABASE_URL`) from environment variables via `python-dotenv`, loaded
from a local `.env` (gitignored, never committed). See `.env.example` for
the required keys. There is no Alembic/Flask-Migrate — schema changes are
applied manually via `psql` (`ALTER TABLE ...`).

## The AI counselor pipeline

Chat messages flow: `services/ai_service.py` (`chat()`) →
`agents/conversation_manager.py` (`process_message()` — conversation/message
persistence, title derivation) → `agent/agent.py` (`run_agent()` — the
actual LLM tool-calling loop: builds a system prompt from
`tools/tool_registry.py`'s tool descriptions, calls
`services/openai_service.py`, parses the model's response, executes the
chosen tool via `agent/executor.py`) → `response_blocks/` (builds
structured card payloads like `recommendation_card` alongside the prose
answer).

**Naming note:** there are two separate top-level packages, `agent/`
(singular — the low-level LLM loop described above) and `agents/` (plural
— higher-level per-feature agents: `conversation_manager.py`,
`predictor_agent.py`, `comparison_agent.py`, etc., plus the tool
`registry.py` they share). `agents/conversation_manager.py` imports from
`agent.agent`, so both are live and neither can be deleted outright — see
*Known gaps* below.

## Folder map

| Path | Contents |
|---|---|
| `routes/*.py` | Web (session-auth) route handlers, one blueprint per feature |
| `routes/api/*.py` | JSON API (JWT-auth) route handlers, mirroring the same features under `/api/v1` |
| `services/*.py` | Shared business logic, called from both route layers |
| `agents/`, `agent/` | AI counselor pipeline — see above |
| `response_blocks/` | Structured card builders for AI chat responses |
| `tools/` | Tool definitions the AI agent can call (search, compare, etc.) |
| `models.py` | All SQLAlchemy models (single file) |
| `templates/`, `static/` | Server-rendered pages and their CSS/JS |
| `docs/` | This file and `API.md` |
| `mcp_server/`, `pipeline/`, `rag/`, `scripts/`, `data/`, `documents/`, `database/`, `qdrant_db/` | Data ingestion / RAG / tooling, largely independent of the live request path |

## Known gaps

Carried over from the pre-mobile backend audit; not addressed in this
pass (secrets, the global API error handler, and this documentation were
the scope of that pass):

- **Duplicated history-recording logic.** Web and API routes for
  predictor/comparison each independently create their history rows
  instead of sharing a service function.
- **`agent/` vs `agents/` naming collision.** Confirmed non-dead code on
  both sides, but confusing; most of `agent/`'s files are unreachable
  dead code and the live chain should eventually be consolidated into
  `agents/`.
- **No pagination** on list endpoints as conversation/history counts grow.
- **No indexes on foreign key columns** (`Conversation.user_id`,
  `Message.conversation_id`, etc.) — Postgres doesn't create these
  automatically, and per-user list queries will slow down as data grows.
- **No JWT revocation** — logout is client-side token deletion only.
- **`created_at` timestamp source is inconsistent** across models: most
  use `server_default=db.func.now()` (DB clock), `Conversation`/`Message`
  use an app-side `datetime.now(UTC)` default. Only matters if the DB
  server's timezone isn't UTC.

None of these are exposed differently to a mobile client than to the web
app today — they're maintenance/scaling concerns, not current
functional bugs, with the exception of the FK-less `User`↔`Conversation`
relationship (no cascade if a user is ever deleted — there's currently no
user-deletion endpoint, so this is latent).
