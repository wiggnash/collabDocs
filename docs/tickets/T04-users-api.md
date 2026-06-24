# T04 — Users API

**Suggested owner:** Teammate B
**Concept focus:** ModelViewSet, ModelSerializer, validation, UUID PK in URLs

## What to build

A `ModelViewSet` for users wired into the router, exposing create and retrieve.

- `POST /api/users/` — create a user (first/last name, email, phone). Validation surfaces uniqueness errors (email, phone) as **400** with a meaningful message.
- `GET /api/users/{id}/` — retrieve by UUID; **404** with a clear message if not found.
- `ModelSerializer` for the User model.

This is the simplest full slice — good warm-up for establishing serializer/viewset conventions the rest of the team will follow.

## Acceptance criteria

- [ ] `POST /api/users/` creates a user and returns 201 with the serialized user (UUID id present).
- [ ] Duplicate email or phone returns 400 with a meaningful message.
- [ ] `GET /api/users/{id}/` returns the user; unknown id returns 404.
- [ ] Endpoints registered via `DefaultRouter`.

## User stories covered

- #1, #2, #3, #34 (create user, uniqueness, fetch by UUID, correct status codes).

## Blocked by

- T02 (data models).
