# T02 — Data models & migrations

**Suggested owner:** Can be split across teammates — see "App layout & ownership" below
**Concept focus:** Models & Migrations (rubric §1, 20 marks — the biggest single block)

## What to build

All 8 models, **each in its own app** (8 apps), plus each app's initial migration applying cleanly from scratch. See PRD §Implementation Decisions → Apps & structure: the architecture is **multiple apps split by domain**; we've settled the mapping as **one model per app**.

Models (see PRD §Models for full field lists). Each lives in its own app:

- **User** — UUID PK; `email` and `phone` as `CharField(unique=True)` (email is `CharField`, **not** `EmailField`, per brief).
- **Workspace** — UUID PK; `owner` FK→User (CASCADE); `is_active` default `True`.
- **WorkspaceMember** — FK→Workspace, FK→User; `role` as `TextChoices` (admin/editor/viewer); `Meta.constraints` includes `UniqueConstraint(fields=['workspace','user'], name='unique_workspace_member')`.
- **Document** — FK→Workspace (CASCADE); `created_by` FK→User (`SET_NULL`, null=True); `status` as `TextChoices` (draft/published/archived); `updated_at` `auto_now`.
- **DocumentVersion** — FK→Document (CASCADE, `related_name='versions'`); `content`; `version_number` `PositiveIntegerField`; `saved_by` FK→User (SET_NULL).
- **Comment** — FK→Document (CASCADE); `author` FK→User (SET_NULL); self-referential `parent = FK('self', null=True, blank=True, on_delete=SET_NULL, related_name='replies')`.
- **Tag** — `name` unique; `documents = ManyToManyField(Document, related_name='tags', blank=True)` declared **on Tag**.
- **AuditLog** — `actor` FK→User (SET_NULL); `action`; `model_name`; `object_id` (UUID as string); `timestamp` `auto_now_add`.

All PKs: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`.

> **Cross-app FKs must use string references** — e.g. `models.ForeignKey('workspaces.Workspace', ...)`, not a direct import — so apps don't depend on each other's import order. This is the one rule that makes the per-app split work cleanly (PRD §Apps & structure, collaboration guardrail (a)).

> Note: the version-number computation and the atomic write logic are **not** in this ticket — they belong to T05/T06 in the view layer. This ticket is structure only.

## App layout & ownership

With one model per app, each app owns its own `migrations/` folder. That **removes the single-shared-history merge risk** that would have forced one owner — so this ticket can be split across teammates by app, as long as you coordinate:

- Build apps in **dependency order** so string FK targets exist: `User` → `Workspace` → `WorkspaceMember`/`Document` → `DocumentVersion`/`Comment`/`Tag`/`AuditLog`.
- Keep naming and conventions consistent across apps (two people are writing them).
- Register every app in `INSTALLED_APPS`; run `makemigrations` per app, then a single `migrate` to apply the whole graph.

## Acceptance criteria

- [x] All 8 models defined with UUID PKs and the exact field types/relations above, **one model per app** (8 apps).
- [x] All 8 apps registered in `INSTALLED_APPS`.
- [x] Cross-app FKs use **string references** (`'app_label.Model'`), not direct imports.
- [x] `role` and `status` use `TextChoices` (no raw string literals).
- [x] `WorkspaceMember` has the `UniqueConstraint` on `(workspace, user)` in `Meta`.
- [x] `Tag.documents` is a `ManyToManyField`; `Comment.parent` is a self-referential FK.
- [x] `makemigrations` produces a clean initial migration **per app**; a single `migrate` applies the full graph from an empty DB with no errors.
- [x] Models are importable and creatable in `manage.py shell` (quick smoke check).

## User stories covered

- #2, #15, #17, #27 (uniqueness, version numbering shape, SET_NULL survival), and the structural basis for all others.

## Blocked by

- T01 (project scaffold).
