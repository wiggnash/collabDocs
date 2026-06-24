# CollabDocs

An **API-only** backend for a simplified Notion / Google Docs. Users create
workspaces, invite collaborators with role-based access, write versioned documents,
comment in threads, tag documents, and have every important action audit-logged.

There is no frontend — **Postman is the client**.

> 🚧 Work in progress. This README will be filled in as features are completed.

## Tech Stack

- **Python** 3.12+
- **Django** 6.x
- **Django REST Framework** 3.x
- **PostgreSQL**
- **[uv](https://docs.astral.sh/uv/)** for dependency and environment management

## Features (planned)

- Workspaces with role-based membership (`admin`, `editor`, `viewer`)
- Versioned documents — every save snapshots a new `DocumentVersion`
- Threaded comments (self-referential replies)
- Tagging documents (many-to-many)
- Aggregated stats/summary endpoints
- Audit logging via Django signals
- Custom request-logging middleware

## Prerequisites

- Python 3.12+
- PostgreSQL (running locally or reachable via connection details)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

## Setup

```bash
# 1. Install dependencies into a project virtual environment
uv sync

# 2. Create your local environment file and fill in real PostgreSQL credentials
cp .env.example .env
```

## Running the project

```bash
# Apply database migrations
uv run python manage.py migrate

# Start the development server (serves /api/ endpoints)
uv run python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

## Common commands

```bash
uv run python manage.py makemigrations   # generate migrations after model changes
uv run python manage.py migrate          # apply migrations
uv run python manage.py shell            # open a Django shell
uv add <package>                         # add a dependency
```

## API

All endpoints are namespaced under `/api/`. Full endpoint documentation and a Postman
collection will be added as the endpoints are implemented. See
[`docs/project_brief.md`](docs/project_brief.md) for the complete specification.

## Project documentation

- [`docs/project_brief.md`](docs/project_brief.md) — full spec, data models, endpoint
  list, and evaluation rubric.
