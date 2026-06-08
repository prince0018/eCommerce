from fastapi import APIRouter, HTTPException, status

from app.database import get_connection
from app.services.inventory.schemas import (
    InventoryItemResponse,
    InventoryListResponse,
    InventoryPurchaseRequest,
    InventoryQuantityUpdate,
    InventoryReserveRequest,
)
from app.services.inventory.service import (
    get_inventory_row,
    reduce_available_stock,
    reserve_available_stock,
    set_available_quantity,
)


router = APIRouter(prefix="/inventory", tags=["inventory"])


def serialize_inventory(row) -> InventoryItemResponse:
    return InventoryItemResponse(
        product_id=row["product_id"],
        sku=row["sku"],
        product_name=row["product_name"],
        available_quantity=row["available_quantity"],
        reserved_quantity=row["reserved_quantity"],
        sold_quantity=row["sold_quantity"],
        updated_at=row["updated_at"],
    )


@router.get("", response_model=InventoryListResponse)
def list_inventory() -> InventoryListResponse:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                inventory_items.product_id,
                inventory_items.sku,
                products.name AS product_name,
                inventory_items.available_quantity,
                inventory_items.reserved_quantity,
                inventory_items.sold_quantity,
                inventory_items.updated_at
            FROM inventory_items
            JOIN products ON products.id = inventory_items.product_id
            WHERE products.is_active = 1
            ORDER BY products.name;
            """
        ).fetchall()

    inventory = [serialize_inventory(row) for row in rows]
    return InventoryListResponse(count=len(inventory), inventory=inventory)


@router.get("/{product_id}", response_model=InventoryItemResponse)
def get_inventory(product_id: int) -> InventoryItemResponse:
    with get_connection() as connection:
        row = get_inventory_row(connection, product_id)

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return serialize_inventory(row)


@router.patch("/{product_id}", response_model=InventoryItemResponse)
def update_available_quantity(
    product_id: int,
    quantity_update: InventoryQuantityUpdate,
) -> InventoryItemResponse:
    with get_connection() as connection:
        if not set_available_quantity(
            connection,
            product_id,
            quantity_update.available_quantity,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

        row = get_inventory_row(connection, product_id)

    return serialize_inventory(row)


@router.post("/{product_id}/reserve", response_model=InventoryItemResponse)
def reserve_stock(
    product_id: int,
    reserve_request: InventoryReserveRequest,
) -> InventoryItemResponse:
    with get_connection() as connection:
        row = get_inventory_row(connection, product_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

        if not reserve_available_stock(connection, product_id, reserve_request.quantity):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock available",
            )

        updated_row = get_inventory_row(connection, product_id)

    return serialize_inventory(updated_row)


@router.post("/{product_id}/purchase", response_model=InventoryItemResponse)
def purchase_stock(
    product_id: int,
    purchase_request: InventoryPurchaseRequest,
) -> InventoryItemResponse:
    with get_connection() as connection:
        row = get_inventory_row(connection, product_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

        if not reduce_available_stock(connection, product_id, purchase_request.quantity):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock available",
            )

        updated_row = get_inventory_row(connection, product_id)

    return serialize_inventory(updated_row)
