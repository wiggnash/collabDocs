# CollabDocs — Tickets

Work breakdown for the CollabDocs backend, derived from [`../PRD.md`](../PRD.md) and [`../project_brief.md`](../project_brief.md).

Each ticket is a grabbable slice. Pick one, move it to **In progress**, finish it (acceptance criteria all checked), then open the next unblocked ticket. Two teammates (**A** and **B**) — owners are *suggestions*, reassign freely.

## Why this ordering

All 8 models live in one Django app and **share a migration history**. Two people generating migrations in parallel is the most likely source of merge conflicts in this project, so **T02 (models + migrations) is a single foundation ticket owned by one person**. Almost everything is blocked by it. The exception is **T03 (middleware)**, which only needs the project scaffold and can run in parallel with the model work.

## Dependency graph

```
T01 scaffold ──┬─> T02 models ──┬─> T04 Users
               │                 ├─> T05 Workspaces
               │                 ├─> T06 Documents (write) ──> T07 Documents (read) 
               │                 │         │
               │                 │         └──> T08 Comments  (also needs T06)
               │                 │         └──> T10 Audit log + signal (also needs T06)
               │                 └─> T09 Tags
               └─> T03 Middleware
                                                       all ──> T11 Deliverables
```

## Board

| # | Ticket | Suggested owner | Blocked by | Status |
| - | ------ | --------------- | ---------- | ------ |
| [T01](T01-project-scaffold.md) | Project scaffold & config | A (shared) | — | Todo |
| [T02](T02-data-models-migrations.md) | Data models & migrations | A (shared) | T01 | Todo |
| [T03](T03-request-logging-middleware.md) | Request-logging middleware | B | T01 | Todo |
| [T04](T04-users-api.md) | Users API | B | T02 | Todo |
| [T05](T05-workspaces-api.md) | Workspaces API | A | T02 | Todo |
| [T06](T06-documents-write-versioning.md) | Documents — write + versioning | B | T02 | Todo |
| [T07](T07-documents-read-search-stats.md) | Documents — list/search/stats/tags | B | T06 | Todo |
| [T08](T08-comments-api.md) | Comments API | A | T02, T06 | Todo |
| [T09](T09-tags-api.md) | Tags API | A | T02 | Todo |
| [T10](T10-audit-log-signal-api.md) | Audit log signal + endpoint | B | T02, T06 | Todo |
| [T11](T11-project-deliverables.md) | Project deliverables | A + B | all | Todo |

## Suggested split

- **Teammate A:** T01 + T02 (foundation, lead), T05 Workspaces, T09 Tags, T08 Comments.
- **Teammate B:** T03 Middleware (start early, parallel to T02), T04 Users, T06 + T07 Documents, T10 Audit log.
- **Together:** T11 (each contributes their endpoints to the Postman collection and README section).

## Rubric coverage map (100 marks)

| Rubric section | Marks | Covered by |
| -------------- | ----- | ---------- |
| Models & Migrations | 20 | T02 |
| Serializers & Validation | 15 | T04, T05, T06, T08 |
| ViewSets & Routing | 15 | T04–T10 |
| QuerySets & Filtering | 15 | T07, T08, T10 |
| Aggregations | 10 | T05 (detail + summary), T07 (stats) |
| Transactions & Integrity | 10 | T05 (workspace+admin), T06 (doc+version) |
| Middleware & Signals | 10 | T03 (middleware), T10 (signal) |
| Code Quality & Setup | 5 | T01, T11 |
