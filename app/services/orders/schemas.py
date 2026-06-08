from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=2, max_length=80)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: str
    status: str
    total_amount: Decimal
    currency: str
    created_at: str
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    count: int
    orders: list[OrderResponse]
