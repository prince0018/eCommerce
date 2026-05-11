from fastapi import HTTPException

from src.repositories import cart_repository, product_repository


def format_cart_rows(rows):
    cart_items = []
    grand_total = 0

    for row in rows:
        total_price = float(row[4])
        cart_items.append({
            "product_id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "quantity": row[3],
            "total_price": total_price,
        })
        grand_total += total_price

    return cart_items, grand_total


def add_to_cart(user_id: int, product_id: int, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be greater than 0")

    product = product_repository.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    message = cart_repository.add_or_update_cart_item(user_id, product_id, quantity)
    return {"message": message}


def get_cart(user_id: int):
    rows = cart_repository.get_cart_items(user_id)

    if not rows:
        return {"message": "Cart is empty", "cart": []}

    cart_items, grand_total = format_cart_rows(rows)
    return {
        "cart": cart_items,
        "grand_total": grand_total,
    }


def update_cart(user_id: int, product_id: int, quantity: int):
    message = cart_repository.update_cart_item(user_id, product_id, quantity)

    if not message:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"message": message}


def clear_cart(user_id: int):
    deleted_items = cart_repository.clear_cart(user_id)

    if not deleted_items:
        return {"message": "Cart already empty"}

    return {"message": "Cart cleared successfully"}
