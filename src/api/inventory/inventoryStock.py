# ...existing code...
from fastapi import APIRouter, HTTPException
from api.db.connection import get_connection

router = APIRouter()


@router.get("/inventory/products")
def list_products():
    """Return all products from the products table."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, description, stock, price, created_at
                    FROM products;
                """)
                rows = cur.fetchall()

                products = []
                for row in rows:
                    products.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "stock": row[3],
                        "price": float(row[4]) if row[4] is not None else None,
                        "created_at": row[5].isoformat() if row[5] else None
                    })

        return {"products": products}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ...existing code...