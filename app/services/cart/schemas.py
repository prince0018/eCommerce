from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    product_id: int
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    available_quantity: int


class CartResponse(BaseModel):
    user_id: int
    total_items: int
    total_amount: Decimal
    currency: str
    items: list[CartItemResponse]
