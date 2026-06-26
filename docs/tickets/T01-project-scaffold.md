# T01 — Project scaffold & configuration

**Suggested owner:** Teammate A (shared foundation — pair on it if you like)
**Concept focus:** Code Quality & Project Setup (rubric §8)

## What to build

The runnable Django + DRF project skeleton that every other ticket builds on. No business logic yet — just a server that starts, connects to the database via environment variables, and exposes an empty `/api/` router.

> **DB choice — SQLite for dev, PostgreSQL for submission.** To keep the scaffold zero-setup, develop against **SQLite** first and switch to **PostgreSQL** later once models stabilize. Both are selected purely through `DATABASE_URL` in `.env` (`env.db()` parses either), so the switch is a config change, not a code change. Keep `psycopg[binary]` installed from the start so Postgres works the instant we flip `DATABASE_URL`. See PRD → Configuration.

- Initialize the project with `uv` (`pyproject.toml` / `uv.lock`).
- Add deps: `django`, `djangorestframework`, `psycopg[binary]`, `django-environ` (the chosen env library — see PRD → Configuration).
- Create the Django project (`config`). **App structure: multiple apps split by domain** (separation of concerns), created **as required** — not one monolithic app. The exact model→app mapping is **decided during model implementation**, not in this scaffold ticket. Each app is added when needed via `uv run python manage.py startapp <name>`.
- Cross-app FKs use **string references** (`'workspaces.Workspace'`) to avoid import-ordering problems. Shared/neutral code (request-logging middleware, common utilities) lives in the `config` project package or a dedicated `common` app — **not** inside a domain app.
- Configure `settings.py` to read DB config and `SECRET_KEY` from `.env` via `django-environ` (`env.db()` for `DATABASES`, `env.bool('DEBUG', ...)`) — **no hardcoded credentials**. `env.db()` reads `DATABASE_URL` and supports both `sqlite:///db.sqlite3` (dev) and `postgres://…` (submission) with no code change.
- Add `rest_framework` and each domain app to `INSTALLED_APPS` as the apps come into existence.
- Wire a DRF `DefaultRouter` mounted at `/api/` in the root URLconf (empty registry for now).
- Reserve a slot in `MIDDLEWARE` for the logging middleware, and plan the `signals.py` import point in the owning app's `AppConfig.ready()` (the `audit`/`documents` app — so T03 and T10 just fill them in).
- Commit a `.env.example` with all required variable names (no real values), including the `DATABASE_URL` expected by `env.db()`. Show **both** the SQLite dev form (`sqlite:///db.sqlite3`) and the commented-out Postgres form (`postgres://USER:PASSWORD@HOST:PORT/NAME`) so the switch is self-documenting.

## Acceptance criteria

- [ ] `uv sync` installs all dependencies from the lockfile.
- [ ] `cp .env.example .env` + filling real values lets `uv run python manage.py runserver` start with no errors.
- [ ] `uv run python manage.py migrate` connects to the configured DB successfully (Django's built-in tables apply) — against **SQLite** for dev.
- [ ] Switching `DATABASE_URL` to a `postgres://…` value and re-running `migrate` applies cleanly against **PostgreSQL** with no code change (verify at least once before relying on Postgres for submission).
- [ ] Hitting `/api/` returns the DRF browsable API root (empty router is fine).
- [ ] No credentials appear anywhere in tracked source; `.env` is git-ignored, `.env.example` is committed.

## User stories covered

- #35 (clean setup, runnable from scratch).

## Blocked by

None — can start immediately.
