from fastapi import APIRouter, HTTPException
from api.db.connection import get_connection

router = APIRouter()


@router.get("/cart/{user_id}")
def get_cart(user_id: int):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

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

        rows = cur.fetchall()

        if not rows:
            return {"message": "Cart is empty", "cart": []}

        cart_items = []
        grand_total = 0

        for row in rows:
            item = {
                "product_id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": row[3],
                "total_price": float(row[4])
            }
            grand_total += float(row[4])
            cart_items.append(item)

        return {
            "cart": cart_items,
            "grand_total": grand_total
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()