from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderLineCreate(BaseModel):
    product_id: str = Field(min_length=1)
    qty: int = Field(ge=1)


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=1)
    lines: list[OrderLineCreate] = Field(min_length=1)


class OrderLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    qty: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    customer_name: str
    total: Decimal
    status: str
    created_at: datetime
    lines: list[OrderLineResponse]
