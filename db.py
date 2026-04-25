import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# Load env variables
DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")


def create_database():
    # connect to default postgres DB
    conn = psycopg2.connect(
        dbname="postgres",
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    # check if DB exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"✅ Database '{DB_NAME}' created")
    else:
        print(f"ℹ️ Database '{DB_NAME}' already exists")

    cur.close()
    conn.close()


def setup_tables():
    # connect to your actual DB
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    cur = conn.cursor()

    # create table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        quantity INT,
        price DECIMAL
    );
    """)

    # insert sample data
    cur.execute("""
    INSERT INTO products (name, quantity, price)
    VALUES (%s, %s, %s);
    """, ("Laptop", 10, 75000))

    conn.commit()
    print("✅ Table created and data inserted")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database()
    setup_tables()