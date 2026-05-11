from fastapi import HTTPException, status

from src.core.security import create_access_token, hash_password, verify_password
from src.repositories import user_repository


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized or "." not in normalized.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email address is required",
        )
    return normalized


def _public_user(row):
    return {
        "id": row[0],
        "email": row[1],
        "full_name": row[2],
        "created_at": row[3].isoformat() if row[3] else None,
    }


def register_user(email: str, password: str, full_name: str | None):
    normalized_email = _normalize_email(email)

    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 6 characters long",
        )

    user_repository.ensure_users_table()

    try:
        user = user_repository.create_user(
            normalized_email,
            full_name,
            hash_password(password),
        )
    except Exception as exc:
        if "duplicate key" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            ) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "message": "User registered successfully",
        "user": _public_user(user),
    }


def login_user(email: str, password: str):
    normalized_email = _normalize_email(email)
    user_repository.ensure_users_table()
    user = user_repository.get_user_by_email(normalized_email)

    if not user or not verify_password(password, user[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": str(user[0]),
            "email": user[1],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user[0],
            "email": user[1],
            "full_name": user[2],
        },
    }


def get_authenticated_user(user_id: int):
    user_repository.ensure_users_table()
    user = user_repository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": _public_user(user)}
