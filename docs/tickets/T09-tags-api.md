# T09 — Tags API

**Suggested owner:** Teammate A
**Concept focus:** ModelSerializer, unique-constraint handling, meaningful errors

## What to build

A `ModelViewSet` (or at minimum create) for tags.

- `POST /api/tags/` — create a tag with a unique `name`. Creating a duplicate name returns a meaningful error (400/409) rather than a raw DB exception.
- `ModelSerializer` for Tag.

Note: *attaching* tags to documents lives in T07 (`POST /api/documents/{id}/tags/`). This ticket is just tag creation/management.

## Acceptance criteria

- [ ] `POST /api/tags/` creates a tag and returns 201.
- [ ] Duplicate tag name returns a clear, handled error (not a 500).
- [ ] Registered via `DefaultRouter`.

## User stories covered

- #28, #29, #34.

## Blocked by

- T02 (data models).
