from fastapi import APIRouter, HTTPException
from db.connection import get_connection

router = APIRouter()


@router.get("/cart/checkout/{user_id}")
def checkout_cart(user_id: int):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # ✅ Fetch cart items + total
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
            return {
                "message": "Cart is empty",
                "items": [],
                "total_amount": 0
            }

        items = []
        subtotal = 0

        for row in rows:
            item = {
                "product_id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": row[3],
                "total_price": float(row[4])
            }
            subtotal += float(row[4])
            items.append(item)

        # 💰 Additional charges (basic example)
        tax = round(subtotal * 0.18, 2)   # 18% GST
        delivery_fee = 50 if subtotal < 500 else 0

        total_amount = subtotal + tax + delivery_fee

        return {
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "delivery_fee": delivery_fee,
            "total_amount": total_amount
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()