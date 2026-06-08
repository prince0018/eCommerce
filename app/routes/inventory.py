from fastapi import APIRouter, HTTPException, status

from app.database import get_connection
from app.schemas import (
    InventoryItemResponse,
    InventoryListResponse,
    InventoryPurchaseRequest,
    InventoryQuantityUpdate,
    InventoryReserveRequest,
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


def get_inventory_row(connection, product_id: int):
    return connection.execute(
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
        WHERE inventory_items.product_id = ? AND products.is_active = 1;
        """,
        (product_id,),
    ).fetchone()


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
def set_available_quantity(
    product_id: int,
    quantity_update: InventoryQuantityUpdate,
) -> InventoryItemResponse:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE inventory_items
            SET available_quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?;
            """,
            (quantity_update.available_quantity, product_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

        connection.execute(
            "UPDATE products SET stock_quantity = ? WHERE id = ?;",
            (quantity_update.available_quantity, product_id),
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

        if row["available_quantity"] < reserve_request.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock available",
            )

        connection.execute(
            """
            UPDATE inventory_items
            SET
                available_quantity = available_quantity - ?,
                reserved_quantity = reserved_quantity + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?;
            """,
            (reserve_request.quantity, reserve_request.quantity, product_id),
        )
        connection.execute(
            """
            UPDATE products
            SET stock_quantity = stock_quantity - ?
            WHERE id = ?;
            """,
            (reserve_request.quantity, product_id),
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

        if row["available_quantity"] < purchase_request.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock available",
            )

        connection.execute(
            """
            UPDATE inventory_items
            SET
                available_quantity = available_quantity - ?,
                sold_quantity = sold_quantity + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?;
            """,
            (purchase_request.quantity, purchase_request.quantity, product_id),
        )
        connection.execute(
            """
            UPDATE products
            SET stock_quantity = stock_quantity - ?
            WHERE id = ?;
            """,
            (purchase_request.quantity, product_id),
        )
        updated_row = get_inventory_row(connection, product_id)

    return serialize_inventory(updated_row)
