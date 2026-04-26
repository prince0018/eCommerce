from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_connection

router = APIRouter()


class AddToCartRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int


@router.post("/cart/add")
def add_to_cart(data: AddToCartRequest):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # ✅ Step 0: Ensure cart table exists
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

        # 🔍 Step 1: Check product exists
        cur.execute(
            "SELECT id, stock FROM products WHERE id = %s;",
            (data.product_id,)
        )
        product = cur.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 🔍 Step 2: Check existing cart item
        cur.execute("""
            SELECT quantity FROM cart
            WHERE user_id = %s AND product_id = %s
        """, (data.user_id, data.product_id))

        existing = cur.fetchone()

        if existing:
            new_quantity = existing[0] + data.quantity

            cur.execute("""
                UPDATE cart
                SET quantity = %s
                WHERE user_id = %s AND product_id = %s
            """, (new_quantity, data.user_id, data.product_id))

            message = "Quantity updated in cart"

        else:
            cur.execute("""
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (data.user_id, data.product_id, data.quantity))

            message = "Product added to cart"

        conn.commit()

        cur.close()
        conn.close()

        return {"message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))