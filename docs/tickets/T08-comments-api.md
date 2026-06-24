# T08 — Comments API

**Suggested owner:** Teammate A
**Concept focus:** Self-referential FK, `SerializerMethodField` (threaded replies), custom validation, filtering by query param

## What to build

A `ModelViewSet` for comments supporting top-level comments and threaded replies.

- `POST /api/comments/` — create a top-level comment (no `parent`) or a reply (`parent` set). Custom validation: a reply's `parent` must belong to the **same document** → 400 otherwise.
- `GET /api/comments/?document={id}` — list all comments for a document in **threaded** form. Filter by the `document` query param, use `select_related('author', 'document')`, and build the nested `replies` representation with a `SerializerMethodField`.

This is one of the two required `SerializerMethodField` uses for the rubric (the nested `replies`).

## Acceptance criteria

- [ ] Posting a comment with no parent creates a top-level comment (201).
- [ ] Posting with a valid `parent` creates a reply; a parent on a different document returns 400.
- [ ] `GET /api/comments/?document={id}` returns the document's comments threaded (replies nested under parents via `SerializerMethodField`).
- [ ] List uses `select_related` for author/document.
- [ ] Deleting a comment's author leaves the comment with a null author (SET_NULL behavior holds).

## User stories covered

- #24, #25, #26, #27, #34.

## Blocked by

- T02 (data models), T06 (need documents to comment on for manual testing).
