from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderLine
from app.models.product import Product


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: str) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.lines))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, *, skip: int = 0, limit: int = 100) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.lines))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(Order)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def create(
        self,
        *,
        customer_id: str,
        customer_name: str,
        lines_data: list[tuple[Product, int]],
    ) -> Order:
        order_lines: list[OrderLine] = []
        total = Decimal("0.00")

        for product, qty in lines_data:
            unit_price = product.price
            subtotal = unit_price * qty
            total += subtotal
            order_lines.append(
                OrderLine(
                    product_id=product.id,
                    product_name=product.name,
                    qty=qty,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )
            )

        order = Order(
            customer_id=customer_id,
            customer_name=customer_name,
            total=total,
            status="placed",
            lines=order_lines,
        )
        self._session.add(order)
        await self._session.flush()
        return order

    async def cancel(self, order: Order) -> Order:
        order.status = "cancelled"
        await self._session.flush()
        return order

    async def count_by_status(self, status: str) -> int:
        stmt = select(func.count()).select_from(Order).where(Order.status == status)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
