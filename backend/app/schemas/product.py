from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=3, max_length=32, pattern=r"^[A-Z0-9-]+$")
    price: Decimal = Field(ge=Decimal("0.00"), decimal_places=2)
    qty: int = Field(ge=0, default=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    sku: str | None = Field(default=None, min_length=3, max_length=32, pattern=r"^[A-Z0-9-]+$")
    price: Decimal | None = Field(default=None, ge=Decimal("0.00"), decimal_places=2)
    qty: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sku: str
    price: Decimal
    qty: int
    created_at: datetime
