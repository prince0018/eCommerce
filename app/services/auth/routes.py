from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_connection
from app.services.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user) -> UserResponse:
    # Convert database rows into the response model used by the API.
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=bool(user["is_active"]),
        created_at=user["created_at"],
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_request: UserRegister) -> UserResponse:
    with get_connection() as connection:
        # Prevent duplicate accounts for the same email address.
        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?;",
            (user_request.email,),
        ).fetchone()
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        cursor = connection.execute(
            """
            INSERT INTO users (email, full_name, password_hash)
            VALUES (?, ?, ?);
            """,
            (
                user_request.email,
                user_request.full_name.strip(),
                hash_password(user_request.password),
            ),
        )
        # Return the freshly created user record.
        user = connection.execute(
            "SELECT * FROM users WHERE id = ?;",
            (cursor.lastrowid,),
        ).fetchone()

    return serialize_user(user)


@router.post("/login", response_model=TokenResponse)
def login_user(login_request: UserLogin) -> TokenResponse:
    with get_connection() as connection:
        # Only active users can log in.
        user = connection.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1;",
            (login_request.email.strip().lower(),),
        ).fetchone()

    if user is None or not verify_password(login_request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Return both the token and the user profile so the frontend can update immediately.
    return TokenResponse(
        access_token=create_access_token(user["id"]),
        user=serialize_user(user),
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user=Depends(get_current_user)) -> UserResponse:
    # Return the signed-in user profile.
    return serialize_user(current_user)
