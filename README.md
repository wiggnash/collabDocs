# CollabDocs

An **API-only** backend for a simplified Notion / Google Docs, built with Django REST
Framework. Users create workspaces, invite collaborators with role-based access, write
**versioned** documents, comment in threads, tag documents, and have every important
action **audit-logged** automatically.

There is no frontend — **Postman is the client**. All endpoints live under `/api/`.

---

## Table of contents

- [Tech stack](#tech-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration (environment variables)](#configuration-environment-variables)
- [Running the server](#running-the-server)
- [Applying migrations](#applying-migrations)
- [Data models](#data-models)
- [API reference (17 endpoints)](#api-reference-17-endpoints)
- [Architecture highlights](#architecture-highlights)
- [Project structure](#project-structure)
- [Postman collection](#postman-collection)
- [Demo video](#demo-video)
- [Switching to PostgreSQL for submission](#switching-to-postgresql-for-submission)

---

## Tech stack

| Layer            | Choice                                             |
| ---------------- | -------------------------------------------------- |
| Language         | Python 3.12+                                        |
| Web framework    | Django 6.x                                          |
| API framework    | Django REST Framework 3.x                           |
| Database         | PostgreSQL (production) · SQLite (local dev)         |
| Env / packaging  | [uv](https://docs.astral.sh/uv/) + `django-environ` |

---

## Features

- **Workspaces** with role-based membership (`admin`, `editor`, `viewer`); the owner is
  auto-enrolled as an `admin` member in the same transaction.
- **Versioned documents** — every create and every update snapshots a new
  `DocumentVersion`, numbered per document.
- **Threaded comments** via a self-referential foreign key (a comment can reply to another).
- **Tagging** documents through a many-to-many relationship, with filtering by tag.
- **Aggregated stats** — workspace detail, workspace summary, and document stats endpoints
  built with `annotate()` / `aggregate()` and `Count`.
- **Automatic audit logging** — a `post_save` signal on `Document` writes an `AuditLog`
  row on every create/update.
- **Custom request-logging middleware** — prints method, path, status code, and duration
  (ms) for every request.

---

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** installed
- **PostgreSQL** — only required for the final submission pass. Local development runs on
  file-based SQLite with zero setup (see [Configuration](#configuration-environment-variables)).

---

## Setup

```bash
# 1. Clone the repository
git clone <your-repo-url> collabDocs
cd collabDocs

# 2. Install dependencies into a project-local virtual environment
uv sync

# 3. Create your local environment file from the template
cp .env.example .env

# 4. Generate a Django SECRET_KEY and paste it into .env
uv run python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"

# 5. Apply migrations (creates db.sqlite3 by default)
uv run python manage.py migrate

# 6. Run the server
uv run python manage.py runserver
```

The API is now available at **`http://127.0.0.1:8000/api/`**.

> `uv sync` reads `pyproject.toml` + `uv.lock` and installs into `.venv/`. Prefixing
> commands with `uv run` executes them inside that environment — no manual `activate` needed.

---

## Configuration (environment variables)

Copy `.env.example` to `.env` and fill in real values. **The real `.env` is git-ignored;
never commit it.**

| Variable        | Required          | Description                                                                                   |
| --------------- | ----------------- | --------------------------------------------------------------------------------------------- |
| `SECRET_KEY`    | Yes               | Django cryptographic secret. Generate a fresh one (see step 4 above).                          |
| `DEBUG`         | Yes               | `True` for local dev, `False` in production. Parsed with `env.bool()`.                         |
| `ALLOWED_HOSTS` | Yes               | Comma-separated hostnames. May be empty while `DEBUG=True`.                                    |
| `NODB`          | Yes               | Database switch. `True` → SQLite (zero-setup dev default); `False` → PostgreSQL.               |
| `DATABASE_URL`  | When `NODB=False` | PostgreSQL DSN: `postgres://USER:PASSWORD@HOST:PORT/NAME`. Ignored when `NODB=True`.           |

**How the database switch works:** `settings.py` reads `NODB`. When `True`, it builds a
SQLite config pointing at `db.sqlite3` — no database server to install or run. When
`False`, it parses `DATABASE_URL` and connects to PostgreSQL. Switching backends is a
one-line `.env` change with **no code edits**.

---

## Running the server

```bash
uv run python manage.py runserver
```

Serves the API at `http://127.0.0.1:8000/api/`. Watch the console — the custom
`RequestLoggingMiddleware` prints a line per request:

```
POST /api/documents/ 201 42.317ms
GET /api/workspaces/<uuid>/summary/ 200 8.914ms
```

---

## Applying migrations

```bash
# Generate migrations after changing any model
uv run python manage.py makemigrations

# Apply all migrations to the configured database
uv run python manage.py migrate
```

All migrations are committed and apply cleanly from scratch on an empty database.

---

## Data models

Eight models, all with **`UUIDField` primary keys** (`uuid.uuid4`, `editable=False`):

| Model             | Purpose                                                                              |
| ----------------- | ------------------------------------------------------------------------------------ |
| `User`            | Person. Unique `email` and `phone`.                                                   |
| `Workspace`       | Container owned by a user; owner auto-added as `admin` member.                        |
| `WorkspaceMember` | User ↔ Workspace link with a `role`. **UniqueConstraint** on `(workspace, user)`.     |
| `Document`        | Titled, versioned content in a workspace, with a `status` (`draft`/`published`/`archived`). |
| `DocumentVersion` | Immutable snapshot of a document's content; `version_number` auto-increments per doc. |
| `Comment`         | Threaded discussion; **self-referential** `parent` FK for replies.                    |
| `Tag`             | Label with a **ManyToMany** link to documents (declared on `Tag`).                    |
| `AuditLog`        | Append-only action record, written automatically by a signal.                         |

Enums (`WorkspaceMember.role`, `Document.status`) use Django `TextChoices`. See
[`docs/project_brief.md`](docs/project_brief.md) for full field-level specs.

---

## API reference (17 endpoints)

All routes are namespaced under `/api/` and registered via DRF's `DefaultRouter`.

### Users

| Method | Endpoint             | Description        |
| ------ | -------------------- | ------------------ |
| `POST` | `/api/users/`        | Create a user.     |
| `GET`  | `/api/users/{id}/`   | Retrieve a user.   |

### Workspaces

| Method | Endpoint                          | Description                                             |
| ------ | --------------------------------- | ------------------------------------------------------ |
| `POST` | `/api/workspaces/`                | Create a workspace + auto-add owner as `admin` (atomic). |
| `GET`  | `/api/workspaces/{id}/`           | Retrieve a workspace with member count.                |
| `POST` | `/api/workspaces/{id}/members/`   | Add a member with a role (returns **409** on duplicate). |
| `GET`  | `/api/workspaces/{id}/members/`   | List members with their roles.                         |
| `GET`  | `/api/workspaces/{id}/summary/`   | Document count, member count, total comments.          |

### Documents

| Method | Endpoint                          | Description                                            |
| ------ | --------------------------------- | ----------------------------------------------------- |
| `POST` | `/api/documents/`                 | Create a document + first version (atomic).            |
| `PUT`  | `/api/documents/{id}/`            | Update content + create a new version (atomic).        |
| `GET`  | `/api/documents/`                 | List with search & filtering (`Q` objects, `__icontains`, tag). |
| `GET`  | `/api/documents/{id}/versions/`   | List all versions, newest first.                       |
| `GET`  | `/api/documents/{id}/stats/`      | Version count, comment count, contributor count.       |
| `POST` | `/api/documents/{id}/tags/`       | Add one or more tags to the document.                  |

### Comments

| Method | Endpoint                          | Description                                          |
| ------ | --------------------------------- | --------------------------------------------------- |
| `POST` | `/api/comments/`                  | Add a top-level comment or a reply (via `parent`).   |
| `GET`  | `/api/comments/?document={id}`    | List all comments for a document (threaded).         |

### Tags & Audit Logs

| Method | Endpoint                                          | Description                                     |
| ------ | ------------------------------------------------- | ----------------------------------------------- |
| `POST` | `/api/tags/`                                      | Create a tag (unique name).                     |
| `GET`  | `/api/audit-logs/`                                | List audit logs, filterable by actor ID and date range (query params). |

---

## Architecture highlights

- **Transactions & integrity** — Workspace creation (`create()` override) and document
  save/version creation (`create()` + `update()` overrides) each run inside a single
  `transaction.atomic()` block, so a failure rolls back the whole operation. Duplicate
  `WorkspaceMember` inserts are caught as `IntegrityError` and returned as **HTTP 409**;
  missing objects raise `DoesNotExist` → **404**.
- **Signals** — `audit_logs/signals.py` defines a `post_save` receiver on `Document`,
  connected in `AuditLogsConfig.ready()`. It uses `instance._state.adding` to distinguish
  `created` from `updated` and writes an `AuditLog` row each time.
- **Middleware** — `config/middleware.py::RequestLoggingMiddleware`, registered last in
  `settings.MIDDLEWARE`, times each request and prints method, path, status, and duration.
- **Query optimisation** — `select_related()` on endpoints returning nested user/workspace/
  document data; `annotate()`/`aggregate()` with `Count` on the stats/summary/detail
  endpoints; `Q` objects for OR search on the document list.

---

## Project structure

```
collabDocs/
├── config/                 # Project settings, URLs, WSGI/ASGI, middleware
│   ├── settings.py         #   INSTALLED_APPS, MIDDLEWARE, DB switch (NODB)
│   ├── urls.py             #   /api/ router includes for every app
│   └── middleware.py       #   RequestLoggingMiddleware
├── users/                  # User model, serializer, viewset, urls
├── workspaces/             # Workspace + members/summary actions
├── workspace_members/      # WorkspaceMember model + UniqueConstraint
├── documents/              # Document + versions/stats/tags actions
├── document_versions/      # DocumentVersion model
├── comments/               # Threaded comments (self-referential FK)
├── tags/                   # Tag model (M2M to Document)
├── audit_logs/             # AuditLog model + post_save signal (ready())
├── docs/                   # project_brief.md and tickets
├── manage.py
├── pyproject.toml / uv.lock
├── requirements.txt        # Pinned deps (mirror of the uv lockfile)
└── .env.example            # Environment template (copy to .env)
```

Each app follows the standard Django layout (`models.py`, `serializers.py`, `views.py`,
`urls.py`, `migrations/`) so responsibilities are easy to find and safe to split across
teammates.

---

## Postman collection

A Postman collection covering all 17 endpoints — organised into **Users, Workspaces,
Documents, Comments, Tags, Audit Logs** folders, with sample request bodies for every
`POST`/`PUT` — is committed at the repository root as `CollabDocs.postman_collection.json`.

Import it into Postman: **Import → File → select the `.json`**. Set the collection variable
`base_url` to `http://127.0.0.1:8000`.

---

## Demo video

📹 **Walkthrough (5–10 min):** _<add your Loom / Google Drive link here>_

The video demonstrates:

1. A complete atomic transaction with **rollback on failure**.
2. **Middleware logs** appearing in the console during requests.
3. At least one **aggregation** endpoint (document stats / workspace summary).
4. An **`AuditLog` written by the signal** after a document update.

---

## Switching to PostgreSQL for submission

Local development uses SQLite for speed, but the rubric expects PostgreSQL. Before
submitting:

```bash
# 1. Create the database and user in Postgres
#    createdb collabdocs   (and a matching role/password)

# 2. In .env, flip the switch and set the DSN
#    NODB=False
#    DATABASE_URL=postgres://collabdocs:password@localhost:5432/collabdocs

# 3. Re-run migrations against Postgres from scratch
uv run python manage.py migrate

# 4. Re-run the full Postman collection to confirm everything passes
```

No code changes are required — only `.env`.

---

## Project documentation

- [`docs/project_brief.md`](docs/project_brief.md) — full spec, data models, endpoint list,
  and evaluation rubric.
- [`docs/tickets/`](docs/tickets/) — feature-by-feature implementation tickets.
