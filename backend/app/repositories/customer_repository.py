from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, customer_id: str) -> Customer | None:
        return await self._session.get(Customer, customer_id)

    async def get_by_email(self, email: str) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self, *, search: str = "", skip: int = 0, limit: int = 100
    ) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.created_at.desc())
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Customer.full_name.ilike(pattern), Customer.email.ilike(pattern))
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, search: str = "") -> int:
        stmt = select(func.count()).select_from(Customer)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Customer.full_name.ilike(pattern), Customer.email.ilike(pattern))
            )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def create(
        self, *, full_name: str, email: str, phone: str
    ) -> Customer:
        customer = Customer(full_name=full_name, email=email.lower(), phone=phone)
        self._session.add(customer)
        await self._session.flush()
        return customer

    async def update(
        self,
        customer: Customer,
        *,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Customer:
        if full_name is not None:
            customer.full_name = full_name
        if email is not None:
            customer.email = email.lower()
        if phone is not None:
            customer.phone = phone
        await self._session.flush()
        return customer

    async def delete(self, customer: Customer) -> None:
        await self._session.delete(customer)
        await self._session.flush()
