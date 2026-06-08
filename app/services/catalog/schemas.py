from decimal import Decimal

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=40)
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=5, max_length=500)
    category: str = Field(..., min_length=2, max_length=80)
    brand: str = Field(..., min_length=2, max_length=80)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    stock_quantity: int = Field(..., ge=0)
    thumbnail: str | None = None
    images: list[str] = Field(default_factory=list)


class ProductSummary(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: str
    source: str
    source_price_usd: Decimal | None = None
    discount_percentage: float | None = None
    rating: float | None = None
    tags: list[str] = Field(default_factory=list)


class ProductResponse(ProductSummary):
    source_data: dict[str, Any] | None = None


class ProductListResponse(BaseModel):
    count: int
    products: list[ProductSummary]


class StockUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0)
