from decimal import Decimal
from sqlite3 import Connection

from app.services.cart.schemas import CartItemResponse, CartResponse


def get_product_for_cart(connection: Connection, product_id: int):
    return connection.execute(
        """
        SELECT
            products.id,
            products.sku,
            products.name,
            products.price,
            products.currency,
            inventory_items.available_quantity
        FROM products
        JOIN inventory_items ON inventory_items.product_id = products.id
        WHERE products.id = ? AND products.is_active = 1;
        """,
        (product_id,),
    ).fetchone()


def get_user_cart(connection: Connection, user_id: int) -> CartResponse:
    rows = connection.execute(
        """
        SELECT
            cart_items.product_id,
            cart_items.quantity,
            products.sku,
            products.name AS product_name,
            products.price,
            products.currency,
            inventory_items.available_quantity
        FROM cart_items
        JOIN products ON products.id = cart_items.product_id
        JOIN inventory_items ON inventory_items.product_id = cart_items.product_id
        WHERE cart_items.user_id = ?
        ORDER BY cart_items.created_at, cart_items.id;
        """,
        (user_id,),
    ).fetchall()

    items: list[CartItemResponse] = []
    total_amount = Decimal("0")
    total_items = 0
    currency = "INR"

    for row in rows:
        unit_price = Decimal(row["price"])
        line_total = unit_price * row["quantity"]
        total_amount += line_total
        total_items += row["quantity"]
        currency = row["currency"]
        items.append(
            CartItemResponse(
                product_id=row["product_id"],
                sku=row["sku"],
                product_name=row["product_name"],
                quantity=row["quantity"],
                unit_price=unit_price,
                line_total=line_total,
                available_quantity=row["available_quantity"],
            )
        )

    return CartResponse(
        user_id=user_id,
        total_items=total_items,
        total_amount=total_amount,
        currency=currency,
        items=items,
    )
