from fastapi import APIRouter, Depends, HTTPException

from src.core.security import get_current_user_id, require_same_user
from src.services import checkout_service

router = APIRouter(prefix="/cart", tags=["checkout"])


@router.get("/checkout/{user_id}")
def checkout_cart(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    require_same_user(user_id, current_user_id)

    try:
        return checkout_service.checkout_cart(user_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
