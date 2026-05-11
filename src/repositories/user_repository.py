from src.db.connection import get_connection


def ensure_users_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


def create_user(email: str, full_name: str | None, hashed_password: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, full_name, hashed_password)
                VALUES (%s, %s, %s)
                RETURNING id, email, full_name, created_at;
                """,
                (email, full_name, hashed_password),
            )
            return cur.fetchone()


def get_user_by_email(email: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, email, full_name, hashed_password
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )
            return cur.fetchone()


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, email, full_name, created_at
                FROM users
                WHERE id = %s;
                """,
                (user_id,),
            )
            return cur.fetchone()
