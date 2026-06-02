from __future__ import annotations

from pydantic import BaseModel

from app.schemas.product import ProductResponse


class DashboardSummary(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    low_stock_count: int
    low_stock_products: list[ProductResponse]
