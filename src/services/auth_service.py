# Import HTTP exception handling and status codes from FastAPI
from fastapi import HTTPException, status

# Import security utilities: token creation, password hashing, and verification
from src.core.security import create_access_token, hash_password, verify_password
# Import the user repository (database access layer for user operations)
from src.repositories import user_repository


def _normalize_email(email: str) -> str:
    """
    Normalize and validate email address.
    
    Purpose:
    - Remove leading/trailing whitespace from email
    - Convert email to lowercase (emails are case-insensitive)
    - Validate email format (must contain @ and domain extension like .com)
    
    Args:
        email (str): Raw email input from user
    
    Returns:
        str: Normalized (lowercase, trimmed) email
    
    Raises:
        HTTPException: If email format is invalid (no @ or no .)
    """
    # Strip whitespace and convert to lowercase for consistency
    normalized = email.strip().lower()
    
    # Validate email format: must have @ and . after @
    # Example: user@example.com is valid, but user@example or user is not
    if "@" not in normalized or "." not in normalized.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email address is required",
        )
    return normalized


def _public_user(row):
    """
    Convert raw database user row into a public-safe user response.
    
    Purpose:
    - Extract only safe user data to return to clients
    - Never expose sensitive data (like password hashes)
    - Format data into a clean dictionary for API responses
    - Convert timestamps to ISO format (standard date/time format)
    
    Args:
        row (tuple): Database row containing (id, email, full_name, created_at, ...)
    
    Returns:
        dict: Safe user data with: id, email, full_name, created_at
    
    Note:
        This function ensures we NEVER accidentally send password hashes
        or other sensitive data to the client.
    """
    return {
        "id": row[0],                                           # User's unique identifier
        "email": row[1],                                        # User's email address
        "full_name": row[2],                                    # User's full name
        "created_at": row[3].isoformat() if row[3] else None,  # Account creation timestamp (ISO format)
    }



def register_user(email: str, password: str, full_name: str | None):
    """
    Register a new user account.
    
    Flow:
    1. Validate and normalize email (remove whitespace, lowercase, check format)
    2. Validate password strength (minimum 6 characters)
    3. Ensure users table exists in database
    4. Hash password using bcrypt (never store plain passwords)
    5. Save user to database
    6. Return success message with user data
    
    Args:
        email (str): User's email address
        password (str): User's chosen password (plain text)
        full_name (str | None): User's full name (optional)
    
    Returns:
        dict: Success message and user data
        Example: {
            "message": "User registered successfully",
            "user": {
                "id": 1,
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2026-05-11T10:00:00"
            }
        }
    
    Raises:
        HTTPException: If email is invalid, password too short, 
                      or email already exists
    """
    # Step 1: Normalize email (remove spaces, lowercase, validate format)
    normalized_email = _normalize_email(email)

    # Step 2: Validate password strength
    # Require minimum 6 characters for security
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 6 characters long",
        )

    # Step 3: Ensure users table exists (creates if not present)
    user_repository.ensure_users_table()

    # Step 4 & 5: Hash password and save user to database
    try:
        # hash_password() uses bcrypt to securely hash the password
        # Never store plain passwords in database!
        user = user_repository.create_user(
            normalized_email,
            full_name,
            hash_password(password),  # Convert plain password to hash
        )
    except Exception as exc:
        # Handle database errors
        # Check if error is due to duplicate email (unique constraint violation)
        if "duplicate key" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            ) from exc
        # For any other error, return generic error message
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Step 6: Return success response with user data
    return {
        "message": "User registered successfully",
        "user": _public_user(user),  # Return only safe user data
    }



def login_user(email: str, password: str):
    """
    Authenticate user and issue JWT access token.
    
    Flow:
    1. Normalize and validate email format
    2. Ensure users table exists
    3. Find user in database by email
    4. Verify password matches stored hash
    5. If credentials valid: create JWT token containing user_id and email
    6. Return token to user for future authenticated requests
    
    Args:
        email (str): User's email address
        password (str): User's password (plain text)
    
    Returns:
        dict: JWT access token and user data
        Example: {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        }
    
    Raises:
        HTTPException: If email/password are incorrect
    
    Note:
        - Password is verified using bcrypt (never stored as plain text)
        - JWT token is valid for 24 hours (configurable in settings)
        - Token should be stored in browser and sent with each request
    """
    # Step 1: Normalize email (lowercase, strip whitespace, validate format)
    normalized_email = _normalize_email(email)
    
    # Step 2: Ensure users table exists in database
    user_repository.ensure_users_table()
    
    # Step 3: Query database for user with this email
    user = user_repository.get_user_by_email(normalized_email)

    # Step 4: Verify user exists AND password matches
    # user[3] is the hashed password from database
    # verify_password() uses bcrypt to compare plain password with hash
    if not user or not verify_password(password, user[3]):
        # Return generic error to prevent email enumeration attacks
        # Don't say "email not found" vs "password wrong" separately
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},  # Tell client to use Bearer token
        )

    # Step 5: Create JWT token for authenticated requests
    # Token payload contains user_id (as "sub") and email
    # This token will be verified in future requests without querying database again
    access_token = create_access_token(
        data={
            "sub": str(user[0]),  # Subject: user's unique ID
            "email": user[1],     # Include email in token for reference
        }
    )

    # Step 6: Return token and user data to frontend
    return {
        "access_token": access_token,      # Token to use in Authorization header
        "token_type": "bearer",            # How to use token: "Bearer <token>"
        "user": {                          # User data to display on frontend
            "id": user[0],
            "email": user[1],
            "full_name": user[2],
        },
    }


def get_authenticated_user(user_id: int):
    """
    Retrieve current authenticated user's details.
    
    Purpose:
    - Used in protected endpoints (endpoints that require JWT token)
    - Returns user data for the logged-in user
    - Extracts user_id from JWT token and fetches full user details
    
    Flow:
    1. Ensure users table exists
    2. Query database for user by user_id
    3. Return user data in safe format
    
    Args:
        user_id (int): User's unique identifier (extracted from JWT token)
    
    Returns:
        dict: User data
        Example: {
            "user": {
                "id": 1,
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2026-05-11T10:00:00"
            }
        }
    
    Raises:
        HTTPException: If user not found (404 error)
    
    Usage:
        This function is called by protected endpoints like GET /auth/me
        The user_id comes from the JWT token decoded in the route handler.
    """
    # Step 1: Ensure users table exists in database
    user_repository.ensure_users_table()
    
    # Step 2: Query database for user with this ID
    user = user_repository.get_user_by_id(user_id)

    # Step 3: Return 404 if user not found
    # This can happen if user was deleted but token still exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ## Step 4: Return user data in safe format (no passwords, hashes, etc.)
    return {"user": _public_user(user)}

