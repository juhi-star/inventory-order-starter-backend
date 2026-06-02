# Backend — Inventory & Order Management API

FastAPI + SQLAlchemy 2 (async) + Alembic + Pydantic v2 + JWT/Argon2id.

## Prerequisites

- Python 3.11 (other versions are not pinned)
- Postgres 15 (or run via `docker compose up postgres -d` from the project root)
- Optional: Redis 7 for caching

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env`. The defaults assume host-mapped Postgres at `localhost:5432`. Generate a real `JWT_SECRET`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Database

Apply migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Run

```bash
uvicorn app.main:app --reload
```

- API base: `http://localhost:8000/api/v1`
- Swagger UI: `http://localhost:8000/docs`
- Liveness: `GET /api/v1/health/live`
- Admin is auto-seeded on first boot from `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`.

## Auth quickstart

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"admin@example.com","password":"<your seed password>"}'
```

Returns `{ user, tokens: { access_token, refresh_token, ... } }`. Use the access token as `Authorization: Bearer <token>` for protected routes.

## Seeding additional users

Admin is auto-seeded on first boot. For any further users, use the bundled CLI:

```bash
source .venv/bin/activate
python -m scripts.seed_user --email alice@example.com --password "strongpwd" --full-name "Alice Chen"
python -m scripts.seed_user --email admin2@example.com --password "strongpwd" --role admin
```

The script Argon2-hashes the password, rejects duplicates, and prints the new user's id on success. Requires `alembic upgrade head` to have been run.

## Tests

```bash
pytest -q
```

Tests use in-memory SQLite via `aiosqlite`; no Postgres needed for the suite.

## Lint / type-check / format

```bash
ruff check .
ruff format .
mypy app
```

## Layout

```
app/
  api/v1/        routes + deps
  core/          config, logging, middleware, limiter, security
  db/            base + session
  models/        SQLAlchemy mapped classes
  repositories/  data-access helpers
  schemas/       Pydantic models
  services/      orchestration (auth_service, admin_seed)
alembic/         migrations
tests/           pytest
```

## Docker

To run alongside Redis and Postgres and the frontend, use `docker compose up` from the project root.
