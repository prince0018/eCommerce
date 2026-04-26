from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.db.connection import get_connection

router = APIRouter()


# ✅ Request schema
class ClearCartRequest(BaseModel):
    user_id: int


@router.delete("/cart/clear")
def clear_cart(data: ClearCartRequest):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Optional: check if cart has items
        cur.execute(
            "SELECT * FROM cart WHERE user_id = %s;",
            (data.user_id,)
        )
        items = cur.fetchall()

        if not items:
            return {"message": "Cart already empty"}

        # ✅ Delete all items for this user
        cur.execute(
            "DELETE FROM cart WHERE user_id = %s;",
            (data.user_id,)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Cart cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))