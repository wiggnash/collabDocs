# T11 — Project deliverables & submission

**Suggested owner:** Teammate A + B (each contributes their own endpoints)
**Concept focus:** Code Quality & Project Setup (rubric §8) + submission requirements

## What to build

The non-code artifacts required for submission. Best done incrementally as endpoints land, finalized at the end.

- **README.md** — setup instructions, how to run the server, how to apply migrations, env var list, and the demo-video link.
- **.env.example** — all required environment variables (no real values). (Started in T01; verify complete.)
- **requirements.txt** — all dependencies pinned (in addition to the `uv` lockfile).
- **Postman collection (`.json`)** at the repo root — covers all 17 endpoints, with sample request bodies for every POST/PUT, organized into folders: Users, Workspaces, Documents, Comments, Tags, Audit Logs.
- **Demo video (5–10 min)** showing: one atomic transaction with rollback on failure, middleware logs in the console, at least one aggregation endpoint, and an `AuditLog` written by the signal after a document update.

## Acceptance criteria

- [x] README covers setup, run, and migrate steps and links the demo video.
- [x] `.env.example` lists every required variable; real `.env` is git-ignored.
- [x] `requirements.txt` pins all deps; a fresh clone installs and runs cleanly.
- [x] Migrations apply from scratch on an empty database.
- [ ] Postman collection at repo root covers all 17 endpoints with sample bodies, folder-organized.
- [ ] Demo video recorded and linked, covering all four required scenarios.

## User stories covered

- #35 (and the project's submission requirements overall).

## Blocked by

- All feature tickets (T03–T10) — needs the endpoints to exist before they can be documented/collected.
