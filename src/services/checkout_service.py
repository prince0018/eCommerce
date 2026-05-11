from src.repositories import cart_repository
from src.services.cart_service import format_cart_rows


def checkout_cart(user_id: int):
    rows = cart_repository.get_cart_items(user_id)

    if not rows:
        return {
            "message": "Cart is empty",
            "items": [],
            "total_amount": 0,
        }

    items, subtotal = format_cart_rows(rows)
    tax = round(subtotal * 0.18, 2)
    delivery_fee = 50 if subtotal < 500 else 0

    return {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "delivery_fee": delivery_fee,
        "total_amount": subtotal + tax + delivery_fee,
    }
