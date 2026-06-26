# PRD: CollabDocs API Backend

> Source: `docs/project_brief.md`. This PRD restates the brief from the user's perspective and records the implementation, verification, and scope decisions for the build. Stack: Django + Django REST Framework + PostgreSQL, managed with `uv`. API-only; Postman is the client. (Database: **SQLite for early development, PostgreSQL for submission** — switched purely via `DATABASE_URL` in `.env`; see Implementation Decisions → Configuration.)

## Problem Statement

Teams that write and collaborate on documents need a shared, structured place to do it — but a flat "everyone can edit everything" model doesn't work. People need to group work into workspaces, control who can do what (admin vs. editor vs. viewer), keep a history of every change so nothing is lost, discuss specific documents in threads, organize documents with tags, and trust that an authoritative record exists of who did what and when.

As the developer (and learner), I also need this backend to demonstrate, end to end, a specific set of Django/DRF concepts — UUID keys, `TextChoices`, constraints, M2M and self-referential FKs, viewsets and custom actions, querysets/filtering/aggregations, atomic transactions, custom middleware, and signals — because each maps to a rubric item I'm graded on.

## Solution

An API-only backend exposing 17 REST endpoints under `/api/` that lets clients:

- Register users and look them up by UUID.
- Create workspaces, where the owner is automatically enrolled as an `admin` member in the same transaction.
- Invite collaborators to a workspace with a role, and list members with their roles.
- Create and update documents, where **every save snapshots the content into a new immutable `DocumentVersion`** within one atomic transaction.
- Browse, search, and filter documents; read a document's full version history; tag documents.
- Comment on documents and reply to comments (threaded), and read a document's comment thread.
- View aggregated stats (workspace summary, workspace detail member count, document stats).
- Read an audit trail of document changes, filtered by actor and date range — written automatically by a signal.

A custom request-logging middleware prints method, path, status, and duration for every request. Every document create/update produces an `AuditLog` row via a `post_save` signal, inside the same atomic block as the action.

## User Stories

1. As an API client, I want to create a user with first name, last name, email, and phone, so that the person can become an actor in the system.
2. As an API client, I want a user's email and phone to be enforced as unique, so that duplicate accounts are rejected with a clear error.
3. As an API client, I want to fetch a user by their UUID, so that I can display or reference their profile.
4. As a workspace owner, I want to create a workspace by name, so that I have a container for my team's documents.
5. As a workspace owner, I want to be automatically added as an `admin` member when I create a workspace, so that I immediately have full control without a second request.
6. As a workspace owner, I want the workspace creation and my admin membership to either both succeed or both fail, so that I never end up with an ownerless or memberless workspace.
7. As a workspace admin, I want to add a collaborator with a role of `admin`, `editor`, or `viewer`, so that I control their level of access.
8. As a workspace admin, I want adding the same user to the same workspace twice to be rejected with a 409, so that membership stays unique and unambiguous.
9. As a workspace member, I want to list all members of a workspace with their roles, so that I can see who has access and at what level.
10. As a workspace member, I want to see the member count when I fetch a workspace, so that I understand the size of the team at a glance.
11. As a workspace member, I want a workspace summary showing document count, member count, and total comments, so that I can gauge activity without paging through everything.
12. As an author, I want to create a document with a title, content, status, and workspace, so that I can start writing collaboratively.
13. As an author, I want a first version to be created automatically when I create a document, so that the history starts from the very first save.
14. As an author, I want each update to my document to create a new version snapshot, so that no previous content is ever lost.
15. As an author, I want version numbers to increment per document starting at 1, so that history is readable and ordered.
16. As an author, I want document creation/update and its version snapshot to be atomic, so that I never get a document whose history is missing a version.
17. As a document with a deleted author, I want the `created_by` reference to become null rather than cascade-delete the document, so that content survives user removal.
18. As a reader, I want to list documents with search and filtering (by title/content text, status, workspace), so that I can find relevant documents quickly.
19. As a reader, I want to search documents by a term that matches title OR content, so that I find a document even if I only remember part of it.
20. As a reader, I want to read all versions of a document ordered by version number, so that I can review how it evolved.
21. As a reader, I want document stats showing version count, comment count, and contributor count, so that I understand how much activity and collaboration a document has seen.
22. As an editor, I want to tag a document with one or more tags in a single request, so that I can categorize it.
23. As a reader, I want to filter documents by tag, so that I can find all documents in a category.
24. As a collaborator, I want to post a top-level comment on a document, so that I can give feedback.
25. As a collaborator, I want to reply to an existing comment, so that discussion stays threaded.
26. As a collaborator, I want to list all comments for a document in threaded form, so that I can follow the conversation.
27. As a collaborator, I want a comment whose author was deleted to keep the comment with a null author, so that the thread stays intact.
28. As an API client, I want to create a tag with a unique name, so that categories are not duplicated.
29. As an API client, I want creating a duplicate tag name to fail with a meaningful error, so that I know the tag already exists.
30. As an auditor, I want every document create and update to be recorded automatically in an audit log, so that I have a trustworthy history of changes without relying on callers to log.
31. As an auditor, I want each audit entry to record the actor, action (`created`/`updated`), model name, object id, and timestamp, so that I can reconstruct what happened.
32. As an auditor, I want to filter audit logs by actor and by a date range, so that I can investigate a specific person or time window.
33. As an operator, I want every request logged with its HTTP method, path, response status, and duration in milliseconds, so that I can observe and debug traffic.
34. As any API client, I want meaningful error messages and correct HTTP status codes (400 / 404 / 409), so that I can handle failures programmatically and understand them.
35. As a teammate picking up this repo, I want clean migrations that apply from scratch, a README, `.env.example`, and pinned dependencies, so that I can run the project without guesswork.
36. As a developer, I want list endpoints that return nested user/workspace/document data to use `select_related` (and reverse lookups efficiently), so that responses don't trigger N+1 queries.

## Implementation Decisions

### Apps & structure
- **Decision: multiple apps, split by domain** (separation of concerns) rather than one monolithic app. Apps are created **as required** during the build, not all up front. **The exact model→app mapping is deliberately left open** and will be decided during model implementation — when we build the models we'll determine which app each one belongs to. The principle is fixed (domain-separated apps, each owning its own models/serializers/viewsets/signals); the specific boundaries are not.
- **Collaboration guardrails for the multi-app choice:** (a) cross-app FKs reference models by string (`'workspaces.Workspace'`) to avoid import-ordering issues; (b) each app has its own `migrations/` folder, which reduces (but doesn't eliminate) migration merge conflicts — coordinate on who edits which app; (c) keep naming/conventions consistent across apps since two people are building them; (d) the request-logging middleware and any shared utilities live in a neutral location (the `config`/project package or a dedicated `common` app), not inside a domain app.
- `DefaultRouter` wires all `ModelViewSet`s under `/api/`. Custom endpoints are `@action` methods on the relevant viewset (not separate `APIView`s).

### Authentication (decision: none — no SimpleJWT)
- **Decision: build with NO authentication layer — no `djangorestframework-simplejwt`, no login, no tokens, no sessions.** This is a deliberate, recorded choice, made after weighing the alternative of adding SimpleJWT.
- **Why no auth:**
  - **Rubric.** All 100 marks map to Models, Serializers, ViewSets, QuerySets, Aggregations, Transactions, Middleware/Signals, and Code Quality. Authentication is *not* a graded item — effort spent on it earns nothing on the scorecard.
  - **The brief is silent on auth and never mentions JWT/SimpleJWT/tokens** (verified by grep over `project_brief.md`), and its `User` spec has **no `password`**, `email` as `CharField` (not `EmailField`), and no `username` — i.e. a plain domain record, not an authenticatable account.
  - **Adding auth would fight the brief's design.** Endpoints take the actor in the request body (`created_by`, `author`, `saved_by`); real JWT would derive the actor from `request.user`, forcing a rewrite of serializers/flows away from the graded spec.
  - **It would force a migration-level change** (`AUTH_USER_MODEL` / `AbstractBaseUser`, set before the first migration), risking the 20-mark Models section whose field spec we'd be contradicting.
- **Identity model we use instead (client-declared actor):** there is no `request.user`. The caller (Postman) is trusted and **passes the acting user's UUID in the request body**. Roles (`WorkspaceMember.role`) are **stored and displayed but never enforced** at the request level. This is a single-tenant / trusted-client simulation of collaboration — it models the *data* of access control without the *enforcement*.
- **`User` stays a plain model** (`class User(models.Model)`), separate from Django's `django.contrib.auth` user, exactly per the brief's field list.
- **If revisited later:** real auth (SimpleJWT) is a valid *learning extension* but must live on a separate `feature/jwt-auth` branch **after** the core build is verified — never on the submission branch — since it changes the user model and the actor-resolution flow.

### Models (8)
- All PKs: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`.
- `User`: `email` and `phone` as `CharField` with `unique=True` (email is `CharField`, **not** `EmailField`, per brief).
- `Workspace`: `owner` FK→User (CASCADE), `is_active` default True. Creation enrolls owner as `WorkspaceMember(role='admin')`.
- `WorkspaceMember`: FK→Workspace, FK→User, `role` via `TextChoices` (admin/editor/viewer). `Meta.constraints` has a `UniqueConstraint(fields=['workspace','user'], name='unique_workspace_member')`.
- `Document`: FK→Workspace (CASCADE), `created_by` FK→User (`SET_NULL`, null=True), `status` via `TextChoices` (draft/published/archived), `updated_at` `auto_now`.
- `DocumentVersion`: FK→Document (CASCADE, `related_name='versions'`), `content` snapshot, `version_number` `PositiveIntegerField`, `saved_by` FK→User (SET_NULL). Version number computed as `document.versions.count() + 1` inside the atomic block.
- `Comment`: FK→Document (CASCADE), `author` FK→User (SET_NULL), self-referential `parent` FK (`'self'`, null/blank, SET_NULL, `related_name='replies'`). Null parent = top-level comment.
- `Tag`: `name` unique, `documents = ManyToManyField(Document, related_name='tags', blank=True)` declared **on Tag**.
- `AuditLog`: `actor` FK→User (SET_NULL), `action`, `model_name`, `object_id` (UUID-as-string), `timestamp`.

### API contracts (17 endpoints under `/api/`)
- **Users**: `POST /users/`, `GET /users/{id}/`.
- **Workspaces**: `POST /workspaces/` (override `create()`, atomic owner+admin), `GET /workspaces/{id}/` (annotate member count), `POST /workspaces/{id}/members/` (add member; 409 on duplicate), `GET /workspaces/{id}/members/` (select_related user, nested serializer), `GET /workspaces/{id}/summary/` (`@action`; document count, member count, total comments via aggregate/annotate + Count).
- **Documents**: `POST /documents/` (override `create()`, atomic doc + first version), `PUT /documents/{id}/` (override `update()`, atomic update + new version), `GET /documents/` (list with `Q`-object OR search across title/content, plus filters via query params and `__icontains`), `GET /documents/{id}/versions/` (`@action`, ordered reverse FK), `GET /documents/{id}/stats/` (`@action`; version/comment/contributor counts), `POST /documents/{id}/tags/` (`@action`, M2M `.add()`).
- **Comments**: `POST /comments/` (top-level or reply via `parent`), `GET /comments/?document={id}` (filter by query param, select_related, threaded representation built with a `SerializerMethodField`).
- **Tags & Audit Logs**: `POST /tags/` (unique handling), `GET /audit-logs/?actor=&start=&end=` (filter with `__gte`/`__lte` on timestamp and actor).

### Serializers & validation
- `ModelSerializer` throughout. At least two `SerializerMethodField`s — e.g. nested `replies` on comments and computed counts/role displays — and custom `validate_*`/`validate` methods in at least two serializers (e.g. member role validity; comment parent must belong to the same document).
- Error responses: 400 for validation, 404 for missing objects (`DoesNotExist`), 409 for duplicate `WorkspaceMember` (caught `IntegrityError`).

### QuerySets & performance
- `select_related` on every endpoint returning nested user/workspace/document data; reverse FK lookups for versions/comments. `values_list(..., flat=True)` where only IDs are needed (e.g. contributor ids for distinct counts). `Q` objects for the document search OR-filter. `aggregate()`/`annotate()` with `Count` in at least 3 endpoints (workspace detail, workspace summary, document stats).

### Transactions & integrity
- `transaction.atomic()` wraps: (a) workspace creation + owner-admin membership, and (b) document save + version creation. The `AuditLog` write happens inside the same atomic block as the document action (via the signal firing within the transaction). `DoesNotExist` → 404; `IntegrityError` on duplicate membership → 409.

### Middleware & signals
- Custom request-logging middleware class (`__init__(self, get_response)` + `__call__(self, request)`): record time before/after `get_response`, print method, path, status, and elapsed ms. Registered in `settings.MIDDLEWARE`.
- `post_save` signal on `Document` in `signals.py`, connected in `AppConfig.ready()`. Use `instance._state.adding` to distinguish create vs. update; write an `AuditLog` with actor=`created_by`, action `created`/`updated`, model_name `Document`, object_id=str(pk).

> Decision note: because the audit log must live in the **same atomic block** as the document write, the signal runs synchronously within the `transaction.atomic()` of the create/update flow — so a rollback of the document write also rolls back its audit entry. This is the intended integrity guarantee.

### Configuration
- **Env library:** `django-environ` is the chosen tool for reading `.env` (decision recorded; installed via `uv add django-environ`). Use `environ.Env` in `settings.py` — `env.db()` to build `DATABASES` from a `DATABASE_URL`, and `env.bool('DEBUG', default=False)` to cast booleans safely (avoids the `os.environ.get('DEBUG') == "False"` truthiness footgun).
- **Database — SQLite for dev, PostgreSQL for submission (decision):** to move fast in early development we run on **SQLite** (zero-setup, single file, no server to provision), then switch to **PostgreSQL** once models and endpoints stabilize. Because `DATABASES` is built from `DATABASE_URL` via `env.db()`, switching is a `.env` change only — **no code change**:
  - Dev: `DATABASE_URL=sqlite:///db.sqlite3`
  - Prod/submission: `DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME`
  - `.env.example` documents both forms. `psycopg[binary]` stays a dependency throughout so Postgres works the moment we switch. **Before submission, run migrations from scratch and re-run the full Postman pass against PostgreSQL** — the rubric and brief expect Postgres, and SQLite differs in some constraint/transaction behaviors (e.g. deferred constraint checking, type affinity), so the Postgres run is the authoritative verification.
- PostgreSQL credentials from `.env` (never hardcoded). `.env.example` lists all required variables. `requirements.txt` pins all deps (in addition to `uv` lockfile) — generate before submission with `uv export --format requirements-txt --no-hashes -o requirements.txt`. README covers setup, running the server, and applying migrations. A Postman collection (`.json`) covering all 17 endpoints, organized into folders, is committed at the repo root.

## Testing Decisions

Per the brief and the user's choice, verification is **manual via Postman** — there is no automated test suite in scope for this PRD.

- **Verification seam:** the HTTP API boundary. Every feature is exercised by sending real requests to `/api/` endpoints in Postman and asserting on status codes and JSON response bodies — the same boundary the rubric grades against.
- **What "passing" looks like:** for each of the 17 endpoints, a saved Postman request with a sample body (for POST/PUT) returns the correct status code and a meaningful payload/error. Requests are organized into folders: Users, Workspaces, Documents, Comments, Tags, Audit Logs.
- **Integrity scenarios to demonstrate explicitly** (these are required in the demo video):
  - One complete atomic transaction with **rollback on failure** (e.g. force a failure during document+version creation and show neither persists).
  - Middleware logs appearing in the console during requests.
  - At least one aggregation endpoint (document stats or workspace summary) returning correct counts.
  - An `AuditLog` row written by the signal after a document update.
  - Duplicate `WorkspaceMember` add returning **409**; missing object returning **404**; invalid body returning **400**.
- **Prior art:** none yet — greenfield repo. The Postman collection itself becomes the regression artifact and is committed to the repo root.

## Out of Scope

> **Inference note:** the brief explicitly marks only the **frontend** as out of scope (`project_brief.md` line 4). The remaining items below are **our scoping decisions inferred from the brief**, not statements the brief makes. Most consequential: the brief is *silent* on authentication and even mentions "role-based permissions" (line 3), but defines no `password` field, no auth endpoints, and no requirement to gate endpoints by role — so we infer auth/authz enforcement is out of scope.

- Any frontend / UI. *(explicitly out of scope per brief)*
- **Authentication & authorization (team decision — no SimpleJWT).** No login, tokens, sessions, or request-level permission checks. The brief is silent on auth (mentions "role-based permissions" but defines no `password` field, no auth endpoints, no role-gating); we have explicitly chosen to build without it. The actor is passed in the request body; roles are stored but not enforced. Full rationale in *Implementation Decisions → Authentication*.
- An automated test suite (unit/integration), CI, linting/formatting gates.
- Pagination, rate limiting, throttling, caching.
- Soft-delete / restore flows beyond the `is_active` flag and `SET_NULL` behaviors specified.
- Real-time collaboration, websockets, presence, or conflict resolution / merge of concurrent edits.
- Audit logging for models other than `Document` (signal is `Document`-only per brief).
- Deployment, containerization, and production hardening.

## Further Notes

- This is a **learning project** and a **two-person group project**: prefer conventional, readable patterns over clever ones; coordinate on shared migrations to avoid conflicts; keep naming and conventions consistent across both contributors.
- Every requirement maps to a graded rubric item (Models & Migrations 20, Serializers & Validation 15, ViewSets & Routing 15, QuerySets & Filtering 15, Aggregations 10, Transactions & Integrity 10, Middleware & Signals 10, Code Quality & Setup 5 = 100). The Implementation Decisions above are organized to cover each.
- Submission requires: public GitHub repo (with `.env.example`, pinned `requirements.txt`, clean migrations, README), the Postman collection `.json` at repo root, and a 5–10 minute demo video covering the integrity scenarios listed under Testing Decisions.
