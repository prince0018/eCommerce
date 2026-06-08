import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "catalog.db"


def add_missing_product_columns(connection: sqlite3.Connection) -> None:
    existing_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(products);").fetchall()
    }
    new_columns = {
        "source": "TEXT NOT NULL DEFAULT 'manual'",
        "source_price_usd": "TEXT",
        "discount_percentage": "REAL",
        "rating": "REAL",
        "thumbnail": "TEXT",
        "images_json": "TEXT NOT NULL DEFAULT '[]'",
        "tags_json": "TEXT NOT NULL DEFAULT '[]'",
        "raw_json": "TEXT",
    }

    for column_name, definition in new_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE products ADD COLUMN {column_name} {definition};"
            )


def initialize_database() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT NOT NULL,
                price TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        add_missing_product_columns(connection)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_items (
                product_id INTEGER PRIMARY KEY,
                sku TEXT UNIQUE NOT NULL,
                available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
                reserved_quantity INTEGER NOT NULL DEFAULT 0 CHECK (reserved_quantity >= 0),
                sold_quantity INTEGER NOT NULL DEFAULT 0 CHECK (sold_quantity >= 0),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                customer_id TEXT NOT NULL,
                status TEXT NOT NULL,
                total_amount TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price TEXT NOT NULL,
                line_total TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_items(sku);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);"
        )


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
