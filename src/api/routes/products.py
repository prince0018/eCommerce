from fastapi import APIRouter, HTTPException

from src.services import product_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/products")
def list_products():
    try:
        return product_service.list_products()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
