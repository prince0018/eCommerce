from fastapi import APIRouter, Depends, status

from src.core.security import get_current_user_id
from src.schemas.auth import LoginRequest, RegisterRequest
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest):
    return auth_service.register_user(data.email, data.password, data.full_name)


@router.post("/token")
def login_for_access_token(data: LoginRequest):
    return auth_service.login_user(data.email, data.password)


@router.get("/me")
def get_authenticated_user(current_user_id: int = Depends(get_current_user_id)):
    return auth_service.get_authenticated_user(current_user_id)
