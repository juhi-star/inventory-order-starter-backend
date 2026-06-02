# Inventory & Order Management — Starter Scaffold

> Starter repo for the **Senior Software Engineer** take-home assessment.
> Boilerplate is done. Your job is the interesting parts.

## What is here

A minimal, working skeleton you can `docker compose up` immediately:

- **Backend**: FastAPI (Python 3.11), SQLAlchemy 2 async, Alembic, Pydantic v2 — wired together with a working `/health/live` endpoint. All resource routers are stubs.
- **Frontend**: React 18 + TypeScript (strict) + Vite + Tailwind + shadcn/ui ready. Axios client + RTK store wired. App shows a placeholder page.
- **Infra**: `docker-compose.yml` for `frontend` / `backend` / `postgres` / `redis` with healthchecks and named volumes.
- **CI**: GitHub Actions running lint + tests + image builds on PR.
- **Docs**: `DESIGN.md` template + ADR templates.

## What you must build

Everything else. See the assessment spec for the full requirement list. In rough order of importance:

1. Domain models (Products, Customers, Orders, OrderItems, AuditEvents) + Alembic migrations
2. Auth (JWT access + refresh, Argon2/bcrypt password hashing, login + refresh endpoints)
3. Products / Customers / Orders CRUD with the contract in the spec
4. **Concurrency-safe order creation** (this is the headline requirement — see `docs/DESIGN.md`)
5. Dashboard endpoint with Redis caching
6. React UI for Auth, Dashboard, Products, Customers, Orders
7. Tests — including the required concurrent-order integration test
8. Deployment to Render/Railway/Fly + Vercel/Netlify + Docker Hub

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Then:
- Frontend: http://localhost:5173
- Backend Swagger: http://localhost:8000/docs
- Backend liveness: http://localhost:8000/health/live

## Local dev (without Docker)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Make targets

```
make up        # docker compose up --build
make down      # docker compose down
make logs      # tail logs
make test      # run backend + frontend tests
make lint      # run all linters
make fmt       # format code
make migrate m="..."  # create alembic migration
```

## Repository layout

```
.
├── backend/                 FastAPI service
│   ├── app/
│   │   ├── api/v1/          Routers (one file per resource)
│   │   ├── core/            Config, logging, security
│   │   ├── db/              SQLAlchemy engine + session
│   │   ├── models/          ORM models (you write these)
│   │   ├── schemas/         Pydantic request/response (you write these)
│   │   ├── services/        Business logic (you write these)
│   │   ├── repositories/    Data access (you write these)
│   │   └── main.py          FastAPI app factory
│   ├── alembic/             Migrations (you generate these)
│   ├── tests/               Pytest suite
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                React + TS SPA
│   ├── src/
│   │   ├── App.tsx          Routes
│   │   ├── main.tsx         Entry point
│   │   ├── index.css        Tailwind + shadcn tokens
│   │   ├── components/ui/   shadcn-generated components live here
│   │   ├── features/        Feature folders (you build these)
│   │   ├── lib/             api client, utils
│   │   ├── store/           Redux Toolkit
│   │   └── test/            Vitest setup
│   ├── Dockerfile
│   ├── nginx.conf           Prod static serving
│   └── package.json
├── docs/
│   ├── DESIGN.md            You fill this in
│   └── adr/                 You add ADRs here
├── .github/workflows/
│   └── ci.yml
├── docker-compose.yml
├── docker-compose.override.yml   Dev hot-reload overlays
└── .env.example
```

## Rules of the road

- Read the assessment spec end-to-end before writing code.
- Read `docs/DESIGN.md` and start filling it in before you finish coding.
- Add an ADR every time you make a non-trivial decision (concurrency, auth, state, caching, ORM).
- Commits should be conventional and atomic. Don't squash everything into one commit.
- No `as any`, no `@ts-ignore`, no `# type: ignore` without a one-line justification on the same line.
- If `docker compose up --build` from a fresh clone does not work, it does not count as submitted.
