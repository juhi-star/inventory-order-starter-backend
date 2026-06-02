from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.deps import CurrentUser, DbSession
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.dashboard import DashboardSummary
from app.schemas.product import ProductResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    session: DbSession,
    current_user: CurrentUser,
) -> DashboardSummary:
    product_repo = ProductRepository(session)
    customer_repo = CustomerRepository(session)
    order_repo = OrderRepository(session)

    total_products = await product_repo.count()
    total_customers = await customer_repo.count()
    total_orders = await order_repo.count()
    low_stock_count = await product_repo.low_stock_count(threshold=10)
    low_stock_products = await product_repo.low_stock_products(threshold=10, limit=10)

    return DashboardSummary(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_count=low_stock_count,
        low_stock_products=[ProductResponse.model_validate(p) for p in low_stock_products],
    )
