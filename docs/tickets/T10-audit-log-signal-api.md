# T10 — Audit log: signal + endpoint

**Suggested owner:** Teammate B
**Concept focus:** Signals (rubric §7), filtering with `__gte`/`__lte` and query params

## What to build

Automatic audit logging of document changes via a `post_save` signal, plus a read endpoint to query the log.

- **Signal:** `post_save` on `Document`, defined in `signals.py`, connected in `AppConfig.ready()`. Use `instance._state.adding` to distinguish create vs. update. Write an `AuditLog` with: `actor = created_by`, `action = 'created' | 'updated'`, `model_name = 'Document'`, `object_id = str(pk)`.
- Because the document save (T06) runs inside `transaction.atomic()`, the signal fires within that same block — so a rollback of the document write also discards the audit entry. Confirm this holds.
- **Endpoint:** `GET /api/audit-logs/` — list audit logs, filterable by `actor` and a date range (`start`/`end`) using `timestamp__gte` / `timestamp__lte` and query params.

## Acceptance criteria

- [x] Creating a document writes an `AuditLog` row with action `created`.
- [x] Updating a document writes an `AuditLog` row with action `updated`.
- [x] Signal is connected in `AppConfig.ready()` (not imported ad-hoc).
- [x] A rolled-back document save leaves no audit row (atomic guarantee — required demo item).
- [ ] `GET /api/audit-logs/?actor=<id>&start=<date>&end=<date>` filters correctly via `__gte`/`__lte`.

## User stories covered

- #30, #31, #32.

## Blocked by

- T02 (data models), T06 (signal fires on Document saves).
