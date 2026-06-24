# T03 — Request-logging middleware

**Suggested owner:** Teammate B (can start in parallel with T02 — only needs the scaffold)
**Concept focus:** Middleware & Signals (rubric §7, middleware half)

## What to build

A custom middleware class that logs one line per request: HTTP method, path, response status code, and time taken in milliseconds.

- Class-based middleware: `__init__(self, get_response)` + `__call__(self, request)`.
- Record a timestamp before calling `get_response(request)` and after; print the elapsed time in ms alongside method, path, and `response.status_code`.
- Register it in `settings.MIDDLEWARE`.

This ticket is independent of the data models, so it's the ideal early parallel task while T02 is in progress.

## Acceptance criteria

- [ ] Middleware class implements `__init__` and `__call__` correctly.
- [ ] Registered in `settings.MIDDLEWARE`.
- [ ] Every request to any endpoint prints a console line containing method, path, status code, and duration in ms.
- [ ] Works for GET, POST, PUT, and DELETE.
- [ ] Verified visible in the console (this is one of the required demo-video items).

## User stories covered

- #33 (observe/debug traffic via per-request logs).

## Blocked by

- T01 (project scaffold).
