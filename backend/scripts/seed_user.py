"""Seed a single user into the database.

Usage:
    python -m scripts.seed_user --email alice@example.com --password "strongpwd"
    python -m scripts.seed_user --email admin@example.com --password "strongpwd" --role admin
    python scripts/seed_user.py --email "bob@example.com" --password "pw" --full-name "Bob"

Prerequisites:
    - backend venv active: `source .venv/bin/activate`
    - DATABASE_URL set (via .env or shell) and migrations applied: `alembic upgrade head`
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a user in the database.")
    parser.add_argument("--email", required=True, help="Login email (lowercased).")
    parser.add_argument("--password", required=True, help="Plaintext password (will be Argon2 hashed).")
    parser.add_argument("--full-name", default="", help="Display name. Optional.")
    parser.add_argument(
        "--role",
        default="user",
        choices=["user", "admin"],
        help="User role. Defaults to 'user'.",
    )
    return parser.parse_args(argv)


async def seed_user(*, email: str, password: str, full_name: str, role: str) -> int:
    async with SessionLocal() as session:
        users = UserRepository(session)
        existing = await users.get_by_email(email)
        if existing is not None:
            print(
                f"error: user with email {email!r} already exists (id={existing.id})",
                file=sys.stderr,
            )
            return 1
        user = await users.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        await session.commit()
        print(f"created user id={user.id} email={user.email} role={user.role}")
        return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(
        seed_user(
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            role=args.role,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
