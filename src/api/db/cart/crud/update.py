from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.db.connection import get_connection

router = APIRouter()


class UpdateCartRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int


@router.put("/cart/update")
def update_cart(data: UpdateCartRequest):
    """Update quantity for a product in user's cart. If quantity <= 0 the item is removed."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check product exists in cart
        cur.execute(
            "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s;",
            (data.user_id, data.product_id)
        )
        existing = cur.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Cart item not found")

        if data.quantity <= 0:
            # Remove item
            cur.execute(
                "DELETE FROM cart WHERE user_id = %s AND product_id = %s;",
                (data.user_id, data.product_id)
            )
            message = "Item removed from cart"
        else:
            # Update quantity
            cur.execute(
                "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s;",
                (data.quantity, data.user_id, data.product_id)
            )
            message = "Cart updated"

        conn.commit()
        cur.close()
        conn.close()

        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))