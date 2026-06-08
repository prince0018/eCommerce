from pydantic import BaseModel, Field


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
