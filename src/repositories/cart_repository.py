from src.db.connection import get_connection


def ensure_cart_table(cur) -> None:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT REFERENCES products(id),
            quantity INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id)
        );
    """)


def add_or_update_cart_item(user_id: int, product_id: int, quantity: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            ensure_cart_table(cur)

            cur.execute(
                """
                SELECT quantity FROM cart
                WHERE user_id = %s AND product_id = %s;
                """,
                (user_id, product_id),
            )
            existing = cur.fetchone()

            if existing:
                new_quantity = existing[0] + quantity
                cur.execute(
                    """
                    UPDATE cart
                    SET quantity = %s
                    WHERE user_id = %s AND product_id = %s;
                    """,
                    (new_quantity, user_id, product_id),
                )
                return "Quantity updated in cart"

            cur.execute(
                """
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s);
                """,
                (user_id, product_id, quantity),
            )
            return "Product added to cart"


def get_cart_items(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    c.quantity,
                    (p.price * c.quantity) AS total_price
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = %s;
            """, (user_id,))
            return cur.fetchall()


def update_cart_item(user_id: int, product_id: int, quantity: int) -> str | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s;",
                (user_id, product_id),
            )
            existing = cur.fetchone()

            if not existing:
                return None

            if quantity <= 0:
                cur.execute(
                    "DELETE FROM cart WHERE user_id = %s AND product_id = %s;",
                    (user_id, product_id),
                )
                return "Item removed from cart"

            cur.execute(
                "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s;",
                (quantity, user_id, product_id),
            )
            return "Cart updated"


def clear_cart(user_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM cart WHERE user_id = %s LIMIT 1;",
                (user_id,),
            )
            has_items = cur.fetchone()

            if not has_items:
                return False

            cur.execute(
                "DELETE FROM cart WHERE user_id = %s;",
                (user_id,),
            )
            return True
