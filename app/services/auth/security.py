import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection


JWT_SECRET = os.getenv("JWT_SECRET", "development-secret-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60
PASSWORD_ITERATIONS = 600_000
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    # Hash passwords with PBKDF2 and a random salt before storing them.
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(password_hash).decode()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    # Compare hashes in constant time to avoid timing leaks.
    try:
        algorithm, iterations, salt_value, expected_value = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.b64decode(salt_value),
            int(iterations),
        )
        return hmac.compare_digest(
            base64.b64encode(actual_hash).decode(),
            expected_value,
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    # Encode the signed-in user id with an expiry time.
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    # Shared dependency for protected endpoints.
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the bearer token and recover the user id from its subject.
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise credentials_error from exc

    with get_connection() as connection:
        # Fetch the active user record for the authenticated request.
        user = connection.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1;",
            (user_id,),
        ).fetchone()

    if user is None:
        raise credentials_error

    return user
