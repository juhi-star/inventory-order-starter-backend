# Design

> Fill this document out as you build. The evaluator reads this first. A scaffolded
> implementation with a thorough `DESIGN.md` ranks higher than a fully built one
> with no design notes.

## 1. Scope and goals

- One-paragraph summary of what this service does.
- Out-of-scope items (state them explicitly).
- Non-functional targets (p95 latency, RPS, durability, recovery objectives).

## 2. Domain model

- ERD (mermaid `erDiagram` or PNG checked into `docs/img/`).
- Entities: Product, Customer, Order, OrderItem, User, AuditEvent.
- Invariants (call these out explicitly):
  - Product SKU is globally unique.
  - Customer email is globally unique (case-insensitive).
  - `Product.quantity_on_hand >= 0` at all times.
  - `OrderItem.quantity > 0`.
  - `Order.total` is server-computed; never trusted from the client.

## 3. API surface

- All endpoints under `/api/v1/`.
- Error envelope: `{ "error": { "code", "message", "details", "request_id" } }`.
- Pagination shape: `{ "items": [...], "page", "page_size", "total" }`.
- Idempotency: which mutating endpoints accept `Idempotency-Key`, how long keys are retained, and the replay semantics.

## 4. Concurrency strategy (the headline decision)

State the chosen strategy and **why**:

- **Pessimistic** (`SELECT ... FOR UPDATE` on product rows inside the order transaction):
  - Pro: simple, correct under contention.
  - Con: lock duration scales with order size; risk of deadlock if rows are not locked in a stable order (lock by ascending `product_id`).
- **Optimistic** (`version` column + `UPDATE ... WHERE version = :v`, retry on 0 rows affected):
  - Pro: no DB-side locking; better under low contention.
  - Con: client-visible retry budget; livelock under heavy contention.

Document:

- Which one you chose.
- Lock ordering (if pessimistic) or retry budget (if optimistic).
- The integration test that proves it works (file path + scenario).
- What happens on the loser: HTTP **409 Conflict** with `error.code = "oversell"`, including the SKU and the available quantity at the time of conflict.

## 5. Caching strategy

- What is cached (e.g. `GET /dashboard/summary`).
- TTL and invalidation triggers.
- Stampede protection (single-flight / jittered TTL).
- Failure mode when Redis is down: serve uncached, log a warning, do **not** fail the request.

## 6. Authentication and authorization

- Access token: JWT, 15-minute TTL, HS256, claim shape `{ sub, iat, exp, type: "access" }`.
- Refresh token: opaque rotation or JWT with `type: "refresh"`; one active refresh per device.
- Password hashing: Argon2id (default) with bcrypt fallback for legacy hashes.
- Rate limit on `/auth/login`: 5 attempts per IP per 5 minutes, then 429.
- Audit events written on login success, login failure, refresh, logout.

## 7. Observability

- Structured JSON logs (`structlog`) with `request_id`, `path`, `method`, `status_code`, `duration_ms`, `user_id` (when authenticated).
- `X-Request-ID` propagated end-to-end; generated if absent.
- Health: `/health/live` (process up), `/health/ready` (DB + Redis reachable).
- Metrics: `/metrics` exposes Prometheus counters for request totals, latency histogram, and oversell-conflict count.

## 8. Security posture

- Threat model summary (STRIDE-lite is fine).
- Secrets: only via environment, never committed; `.env` is git-ignored.
- CORS allowlist driven by `APP_CORS_ORIGINS`.
- Security headers on the frontend (see `frontend/nginx.conf`).
- Argon2id parameters and rationale.

## 9. Failure modes and recovery

- Postgres down: API returns 503 at `/health/ready`; `/health/live` stays 200; clients see 503 on writes.
- Redis down: degraded cache, requests succeed.
- Partial deploy: migrations are forward-compatible (additive); never drop a column in the same release that stops writing to it.

## 10. Trade-offs accepted

State the trade-offs you knowingly accepted. Examples:

- "Optimistic locking chosen because expected contention is low (<10 concurrent orders/sec per SKU); accepted 3-retry budget."
- "Single-region deploy; no multi-region failover for this take-home."
- "Audit events stored in the same Postgres database; in production we would ship them to a separate write-only store."

## 11. 10x scale considerations

Pick three of the following and describe what would change:

- Read scaling: read replicas, query splitting.
- Order throughput: sharding by `customer_id` or `product_id` range; queue-based reservation.
- Cache: Redis cluster, per-key partitioning.
- Background jobs: separate worker process (RQ/Arq/Dramatiq) for stock reconciliation.
- Deployment: blue/green or canary; feature flags.

## 12. What you would do next

Three bullets, time-boxed (e.g. "Next 2 days: ...", "Next 1 week: ...", "Next 1 month: ...").
