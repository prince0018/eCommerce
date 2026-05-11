from fastapi import APIRouter, Depends, HTTPException

from src.core.security import get_current_user_id, require_same_user
from src.schemas.cart import AddToCartRequest, ClearCartRequest, UpdateCartRequest
from src.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add")
def add_to_cart(
    data: AddToCartRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    require_same_user(data.user_id, current_user_id)

    try:
        return cart_service.add_to_cart(data.user_id, data.product_id, data.quantity)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{user_id}")
def get_cart(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    require_same_user(user_id, current_user_id)

    try:
        return cart_service.get_cart(user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/update")
def update_cart(
    data: UpdateCartRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    require_same_user(data.user_id, current_user_id)

    try:
        return cart_service.update_cart(data.user_id, data.product_id, data.quantity)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/clear")
def clear_cart(
    data: ClearCartRequest,
    current_user_id: int = Depends(get_current_user_id),
):
    require_same_user(data.user_id, current_user_id)

    try:
        return cart_service.clear_cart(data.user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
