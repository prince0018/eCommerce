from src.repositories import product_repository


def list_products():
    products = []

    for row in product_repository.list_products():
        products.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "stock": row[3],
            "price": float(row[4]) if row[4] is not None else None,
            "created_at": row[5].isoformat() if row[5] else None,
        })

    return {"products": products}
