from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.database import get_connection
from app.services.auth.security import get_current_user
from app.services.cart.schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from app.services.cart.service import get_product_for_cart, get_user_cart
from app.services.orders.routes import create_order
from app.services.orders.schemas import OrderCreate, OrderItemCreate, OrderResponse


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
def get_cart(current_user=Depends(get_current_user)) -> CartResponse:
    with get_connection() as connection:
        return get_user_cart(connection, current_user["id"])


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(
    item_request: CartItemCreate,
    current_user=Depends(get_current_user),
) -> CartResponse:
    with get_connection() as connection:
        product = get_product_for_cart(connection, item_request.product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        existing_item = connection.execute(
            """
            SELECT quantity
            FROM cart_items
            WHERE user_id = ? AND product_id = ?;
            """,
            (current_user["id"], item_request.product_id),
        ).fetchone()
        new_quantity = item_request.quantity
        if existing_item is not None:
            new_quantity += existing_item["quantity"]

        if new_quantity > product["available_quantity"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Requested cart quantity exceeds available stock",
            )

        connection.execute(
            """
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET
                quantity = excluded.quantity,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (current_user["id"], item_request.product_id, new_quantity),
        )
        return get_user_cart(connection, current_user["id"])


@router.patch("/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    product_id: int,
    item_update: CartItemUpdate,
    current_user=Depends(get_current_user),
) -> CartResponse:
    with get_connection() as connection:
        product = get_product_for_cart(connection, product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        if item_update.quantity > product["available_quantity"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Requested cart quantity exceeds available stock",
            )

        cursor = connection.execute(
            """
            UPDATE cart_items
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND product_id = ?;
            """,
            (item_update.quantity, current_user["id"], product_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product is not in the cart",
            )

        return get_user_cart(connection, current_user["id"])


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    product_id: int,
    current_user=Depends(get_current_user),
) -> Response:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?;",
            (current_user["id"], product_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product is not in the cart",
            )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user=Depends(get_current_user)) -> Response:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM cart_items WHERE user_id = ?;",
            (current_user["id"],),
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout_cart(current_user=Depends(get_current_user)) -> OrderResponse:
    with get_connection() as connection:
        cart = get_user_cart(connection, current_user["id"])

    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty",
        )

    order = create_order(
        OrderCreate(
            customer_id=str(current_user["id"]),
            items=[
                OrderItemCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                for item in cart.items
            ],
        )
    )

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM cart_items WHERE user_id = ?;",
            (current_user["id"],),
        )

    return order
