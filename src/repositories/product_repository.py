from src.db.connection import get_connection


def list_products():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, description, stock, price, created_at
                FROM products;
            """)
            return cur.fetchall()


def get_product_by_id(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, stock FROM products WHERE id = %s;",
                (product_id,),
            )
            return cur.fetchone()
