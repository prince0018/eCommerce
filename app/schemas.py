from decimal import Decimal

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


class ProductResponse(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: str


class ProductListResponse(BaseModel):
    count: int
    products: list[ProductResponse]


class StockUpdate(BaseModel):
    stock_quantity: int = Field(..., ge=0)


class InventoryItemResponse(BaseModel):
    product_id: int
    sku: str
    product_name: str
    available_quantity: int
    reserved_quantity: int
    sold_quantity: int
    updated_at: str


class InventoryListResponse(BaseModel):
    count: int
    inventory: list[InventoryItemResponse]


class InventoryQuantityUpdate(BaseModel):
    available_quantity: int = Field(..., ge=0)


class InventoryReserveRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class InventoryPurchaseRequest(BaseModel):
    quantity: int = Field(..., gt=0)
