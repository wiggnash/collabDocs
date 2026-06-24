# T07 — Documents: list/search, versions, stats, tags

**Suggested owner:** Teammate B (same owner as T06 — both touch the Documents viewset, avoid file conflicts)
**Concept focus:** QuerySets & Filtering (Q objects, `__icontains`, query params, `values_list`), Aggregations (stats)

## What to build

The read/aggregation side of the Documents viewset, plus the tag-attach action.

- `GET /api/documents/` — list with filtering and search via query params:
  - A search term matching **title OR content** using `Q` objects + `__icontains`.
  - Filters for `status`, `workspace`, and `tag` (e.g. `tags__name`).
  - Use `select_related('workspace', 'created_by')` to avoid N+1.
- `GET /api/documents/{id}/versions/` — `@action`: all versions ordered by `version_number` (reverse FK lookup, `order_by`).
- `GET /api/documents/{id}/stats/` — `@action`: version count, comment count, and **distinct contributor** count via `aggregate()`/`annotate()` with `Count`. Use `values_list(..., flat=True)` where only IDs are needed.
- `POST /api/documents/{id}/tags/` — `@action`: attach one or more tags to the document via `ManyToManyField.add()`.

## Acceptance criteria

- [ ] `GET /api/documents/?search=<term>` returns docs matching the term in title OR content (Q-object OR filter).
- [ ] Filtering by `status`, `workspace`, and `tag` works via query params.
- [ ] List endpoint uses `select_related` (no N+1 on workspace/created_by).
- [ ] `versions/` returns all versions in version-number order.
- [ ] `stats/` returns correct version, comment, and contributor counts (aggregation, not Python loops).
- [ ] `tags/` attaches the given tags and they appear on subsequent reads / tag filtering.

## User stories covered

- #18, #19, #20, #21, #22, #23, #36.

## Blocked by

- T06 (Documents write paths — shares the viewset).
