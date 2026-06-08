from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.database import get_connection
from app.services.inventory.service import reduce_available_stock
from app.services.orders.schemas import (
    OrderCreate,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
)


router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_with_items(connection, order_id: int) -> OrderResponse | None:
    # Load one order with its items.
    order = connection.execute(
        "SELECT * FROM orders WHERE id = ?;",
        (order_id,),
    ).fetchone()

    if order is None:
        return None

    item_rows = connection.execute(
        """
        SELECT
            order_items.product_id,
            order_items.sku,
            order_items.product_name,
            order_items.quantity,
            order_items.unit_price,
            order_items.line_total
        FROM order_items
        WHERE order_items.order_id = ?
        ORDER BY order_items.id;
        """,
        (order_id,),
    ).fetchall()

    return OrderResponse(
        id=order["id"],
        order_number=order["order_number"],
        customer_id=order["customer_id"],
        status=order["status"],
        total_amount=Decimal(order["total_amount"]),
        currency=order["currency"],
        created_at=order["created_at"],
        items=[
            OrderItemResponse(
                product_id=item["product_id"],
                sku=item["sku"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=Decimal(item["unit_price"]),
                line_total=Decimal(item["line_total"]),
            )
            for item in item_rows
        ],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_request: OrderCreate) -> OrderResponse:
    # Create the order and its line items.
    with get_connection() as connection:
        product_ids = [item.product_id for item in order_request.items]
        if len(product_ids) != len(set(product_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate products are not allowed in one order",
            )

        order_items: list[dict[str, object]] = []
        total_amount = Decimal("0")
        currency = "INR"

        for item in order_request.items:
            product = connection.execute(
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
                (item.product_id,),
            ).fetchone()

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found",
                )

            if product["available_quantity"] < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Not enough stock for product {item.product_id}",
                )

            unit_price = Decimal(product["price"])
            line_total = unit_price * item.quantity
            total_amount += line_total
            currency = product["currency"]
            order_items.append(
                {
                    "product_id": product["id"],
                    "sku": product["sku"],
                    "product_name": product["name"],
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                }
            )

        cursor = connection.execute(
            """
            INSERT INTO orders (order_number, customer_id, status, total_amount, currency)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                f"ORD-{uuid4().hex[:10].upper()}",
                order_request.customer_id,
                "CONFIRMED",
                str(total_amount),
                currency,
            ),
        )
        order_id = cursor.lastrowid

        for item in order_items:
            if not reduce_available_stock(
                connection,
                item["product_id"],
                item["quantity"],
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Not enough stock for product {item['product_id']}",
                )

            connection.execute(
                """
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    sku,
                    product_name,
                    quantity,
                    unit_price,
                    line_total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    order_id,
                    item["product_id"],
                    item["sku"],
                    item["product_name"],
                    item["quantity"],
                    str(item["unit_price"]),
                    str(item["line_total"]),
                ),
            )

        created_order = get_order_with_items(connection, order_id)

    return created_order


@router.get("", response_model=OrderListResponse)
def list_orders() -> OrderListResponse:
    # Return all orders in reverse order.
    with get_connection() as connection:
        order_rows = connection.execute(
            "SELECT id FROM orders ORDER BY created_at DESC, id DESC;"
        ).fetchall()
        orders = [
            get_order_with_items(connection, order_row["id"])
            for order_row in order_rows
        ]

    return OrderListResponse(count=len(orders), orders=orders)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int) -> OrderResponse:
    # Return one order by id.
    with get_connection() as connection:
        order = get_order_with_items(connection, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order
