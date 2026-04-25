import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")


def create_cart_table():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            product_id INT REFERENCES products(id),
            quantity INT NOT NULL,
            total_price NUMERIC NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        print("✅ Cart table created (or already exists)")

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    create_cart_table()