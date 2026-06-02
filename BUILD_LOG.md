# Build log

> Fill this in as you go. The evaluator reads this to understand your process,
> not just your output. **Brevity is fine; honesty matters.** Cut corners are
> expected — document them so we can tell the difference between an oversight
> and a deliberate trade-off.

## Time spent

| Bucket                          | Hours |
| ------------------------------- | ----- |
| Reading spec + planning         |       |
| Backend (domain + API + tests)  |       |
| Concurrency strategy + test     |       |
| Auth                            |       |
| Frontend (UI + state + tests)   |       |
| Docker / deployment             |       |
| Docs (DESIGN.md + ADRs)         |       |
| **Total**                       |       |

## Key decisions

For each non-trivial choice, one line. Link to the ADR if you wrote one.

- [ ] Concurrency strategy: pessimistic | optimistic — see [ADR-NNNN](docs/adr/NNNN-...md)
- [ ] Password hashing: Argon2id | bcrypt — reason:
- [ ] Refresh token shape: opaque rotating | JWT — reason:
- [ ] Cache strategy for dashboard: TTL | event-invalidated — reason:
- [ ] State management split: RTK slices per feature | single store — reason:
- [ ] Form validation: Zod schemas colocated with feature | shared — reason:

## What I cut and why

State explicitly. Examples:

- Skipped pagination on `GET /customers` because list is bounded by seed data. Would add `?page=` + `?page_size=` for production.
- No CSRF protection because tokens are sent via `Authorization` header, not cookies.
- No request-level retry on the frontend axios client. Would add for idempotent GETs only.

## Known issues / rough edges

Anything you would fix with another hour:

-
-

## What I would do next

Three bullets, time-boxed.

- Next 2 hours:
- Next 1 day:
- Next 1 week:

## Notes to the reviewer

Anything that is non-obvious from the code: surprising patterns, intentional
omissions, places where you disagreed with the spec and chose differently.
