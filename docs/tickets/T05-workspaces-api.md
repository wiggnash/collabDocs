# T05 — Workspaces API

**Suggested owner:** Teammate A
**Concept focus:** Transactions & Integrity (atomic create), Aggregations (Count/annotate), 409 handling

## What to build

A `ModelViewSet` for workspaces plus its custom member and summary endpoints.

- `POST /api/workspaces/` — override `create()`. Inside a single `transaction.atomic()`: create the workspace **and** add the owner as a `WorkspaceMember` with `role='admin'`. Both succeed or both roll back.
- `GET /api/workspaces/{id}/` — retrieve with a **member count** via `annotate(Count(...))`. 404 if missing.
- `POST /api/workspaces/{id}/members/` — `@action`: add a member with a role. Catch `IntegrityError` from the `(workspace, user)` unique constraint and return **409** with a meaningful message. Invalid role → 400.
- `GET /api/workspaces/{id}/members/` — `@action`: list members with their roles, using `select_related('user')` and a nested serializer.
- `GET /api/workspaces/{id}/summary/` — `@action`: document count, member count, and total comments across the workspace's documents, via `aggregate()`/`annotate()` with `Count`.

## Acceptance criteria

- [x] Creating a workspace returns 201 and the owner exists as an `admin` member.
- [x] If member creation fails, the workspace is **not** persisted (demonstrable rollback).
- [x] Workspace detail includes a correct member count (annotated, not computed in Python).
- [x] Adding a duplicate member returns 409; invalid role returns 400; unknown workspace/user returns 404.
- [x] Member list uses `select_related` and shows each member's role.
- [x] Summary returns correct document count, member count, and total comment count.
- [x] Custom endpoints use `@action`; CRUD uses `ModelViewSet`.

## User stories covered

- #4, #5, #6, #7, #8, #9, #10, #11, #34.

## Blocked by

- T02 (data models). Member-add references users created via T04 (not a code dependency, but useful for manual testing).
