# T02 — Data models & migrations

**Suggested owner:** Teammate A (foundation — single owner to keep migration history clean)
**Concept focus:** Models & Migrations (rubric §1, 20 marks — the biggest single block)

## What to build

All 8 models in one app, plus the initial migration that applies cleanly from scratch. This ticket is intentionally owned by **one person** because the whole team shares one migration history — parallel migration generation is the main merge-conflict risk in this project.

Models (see PRD §Models for full field lists):

- **User** — UUID PK; `email` and `phone` as `CharField(unique=True)` (email is `CharField`, **not** `EmailField`, per brief).
- **Workspace** — UUID PK; `owner` FK→User (CASCADE); `is_active` default `True`.
- **WorkspaceMember** — FK→Workspace, FK→User; `role` as `TextChoices` (admin/editor/viewer); `Meta.constraints` includes `UniqueConstraint(fields=['workspace','user'], name='unique_workspace_member')`.
- **Document** — FK→Workspace (CASCADE); `created_by` FK→User (`SET_NULL`, null=True); `status` as `TextChoices` (draft/published/archived); `updated_at` `auto_now`.
- **DocumentVersion** — FK→Document (CASCADE, `related_name='versions'`); `content`; `version_number` `PositiveIntegerField`; `saved_by` FK→User (SET_NULL).
- **Comment** — FK→Document (CASCADE); `author` FK→User (SET_NULL); self-referential `parent = FK('self', null=True, blank=True, on_delete=SET_NULL, related_name='replies')`.
- **Tag** — `name` unique; `documents = ManyToManyField(Document, related_name='tags', blank=True)` declared **on Tag**.
- **AuditLog** — `actor` FK→User (SET_NULL); `action`; `model_name`; `object_id` (UUID as string); `timestamp` `auto_now_add`.

All PKs: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`.

> Note: the version-number computation and the atomic write logic are **not** in this ticket — they belong to T05/T06 in the view layer. This ticket is structure only.

## Acceptance criteria

- [ ] All 8 models defined with UUID PKs and the exact field types/relations above.
- [ ] `role` and `status` use `TextChoices` (no raw string literals).
- [ ] `WorkspaceMember` has the `UniqueConstraint` on `(workspace, user)` in `Meta`.
- [ ] `Tag.documents` is a `ManyToManyField`; `Comment.parent` is a self-referential FK.
- [ ] `makemigrations` produces one clean initial migration; `migrate` applies it from an empty DB with no errors.
- [ ] Models are importable and creatable in `manage.py shell` (quick smoke check).

## User stories covered

- #2, #15, #17, #27 (uniqueness, version numbering shape, SET_NULL survival), and the structural basis for all others.

## Blocked by

- T01 (project scaffold).
