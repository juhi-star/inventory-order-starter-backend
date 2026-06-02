from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, product_id: str) -> Product | None:
        return await self._session.get(Product, product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku.upper())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, *, search: str = "", skip: int = 0, limit: int = 100) -> list[Product]:
        stmt = select(Product).order_by(Product.created_at.desc())
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, search: str = "") -> int:
        stmt = select(func.count()).select_from(Product)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
            )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def create(
        self, *, name: str, sku: str, price: Decimal, qty: int
    ) -> Product:
        product = Product(name=name, sku=sku.upper(), price=price, qty=qty)
        self._session.add(product)
        await self._session.flush()
        return product

    async def update(
        self,
        product: Product,
        *,
        name: str | None = None,
        sku: str | None = None,
        price: Decimal | None = None,
        qty: int | None = None,
    ) -> Product:
        if name is not None:
            product.name = name
        if sku is not None:
            product.sku = sku.upper()
        if price is not None:
            product.price = price
        if qty is not None:
            product.qty = qty
        await self._session.flush()
        return product

    async def delete(self, product: Product) -> None:
        await self._session.delete(product)
        await self._session.flush()

    async def adjust_stock(self, product: Product, *, delta: int) -> Product:
        product.qty += delta
        if product.qty < 0:
            product.qty = 0
        await self._session.flush()
        return product

    async def low_stock_products(self, *, threshold: int = 10, limit: int = 10) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.qty <= threshold)
            .order_by(Product.qty.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def low_stock_count(self, *, threshold: int = 10) -> int:
        stmt = select(func.count()).select_from(Product).where(Product.qty <= threshold)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
