# T06 — Documents: write paths & versioning

**Suggested owner:** Teammate B
**Concept focus:** Transactions & Integrity (atomic doc + version), overriding `create()`/`update()`, version-number logic

## What to build

The write side of the Documents `ModelViewSet`. Every save snapshots content into a new `DocumentVersion` inside one atomic transaction.

- `POST /api/documents/` — override `create()`. Inside `transaction.atomic()`: create the `Document` **and** its first `DocumentVersion`. Compute `version_number` as `document.versions.count() + 1` (→ 1 for the first).
- `PUT /api/documents/{id}/` — override `update()`. Inside `transaction.atomic()`: update the document content **and** create a new `DocumentVersion` snapshot with the incremented version number. 404 if missing.
- `ModelSerializer` for Document; capture `saved_by`/`created_by` appropriately.

> The `AuditLog` write triggered by these saves is handled by the signal in **T10**, which fires inside this same atomic block — coordinate so the signal exists before the demo. The document write must roll back its audit entry on failure.

## Acceptance criteria

- [x] Creating a document returns 201 and creates exactly one version with `version_number == 1`.
- [x] Updating a document creates a new version with the next number; previous versions are untouched.
- [x] Document + version creation is atomic — a forced failure persists neither (this is the required demo rollback scenario).
- [x] `create()` and `update()` are explicitly overridden on the viewset.
- [x] Unknown document id returns 404.

## User stories covered

- #12, #13, #14, #15, #16, #34.

## Blocked by

- T02 (data models).
