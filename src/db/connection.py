import psycopg2

from src.core.config import settings


def get_connection():
    return psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        connect_timeout=5,
    )
