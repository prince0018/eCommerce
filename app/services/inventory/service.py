from sqlite3 import Connection


def get_inventory_row(connection: Connection, product_id: int):
    # Inventory is stored separately from product details, so we join both tables here.
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


def set_available_quantity(connection: Connection, product_id: int, quantity: int) -> bool:
    # Direct admin-style update for the current stock level.
    cursor = connection.execute(
        """
        UPDATE inventory_items
        SET available_quantity = ?, updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ?;
        """,
        (quantity, product_id),
    )

    if cursor.rowcount == 0:
        return False

    connection.execute(
        "UPDATE products SET stock_quantity = ? WHERE id = ?;",
        (quantity, product_id),
    )
    return True


def reduce_available_stock(connection: Connection, product_id: int, quantity: int) -> bool:
    # Final stock deduction after a successful order.
    cursor = connection.execute(
        """
        UPDATE inventory_items
        SET
            available_quantity = available_quantity - ?,
            sold_quantity = sold_quantity + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ? AND available_quantity >= ?;
        """,
        (quantity, quantity, product_id, quantity),
    )

    if cursor.rowcount == 0:
        return False

    connection.execute(
        """
        UPDATE products
        SET stock_quantity = stock_quantity - ?
        WHERE id = ?;
        """,
        (quantity, product_id),
    )
    return True


def reserve_available_stock(connection: Connection, product_id: int, quantity: int) -> bool:
    # Checkout flow can reserve stock before payment is finalized.
    cursor = connection.execute(
        """
        UPDATE inventory_items
        SET
            available_quantity = available_quantity - ?,
            reserved_quantity = reserved_quantity + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE product_id = ? AND available_quantity >= ?;
        """,
        (quantity, quantity, product_id, quantity),
    )

    if cursor.rowcount == 0:
        return False

    connection.execute(
        """
        UPDATE products
        SET stock_quantity = stock_quantity - ?
        WHERE id = ?;
        """,
        (quantity, product_id),
    )
    return True
