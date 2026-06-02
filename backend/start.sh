#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --no-access-log --workers "${UVICORN_WORKERS:-4}"
