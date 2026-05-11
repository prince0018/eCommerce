import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-before-production")
    access_token_expire_minutes = 60


settings = Settings()
