import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "catalog.db"


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
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_items(sku);"
        )


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
