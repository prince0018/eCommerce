import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.request import Request, urlopen

from app.database import BASE_DIR, get_connection, initialize_database


DUMMYJSON_URL = "https://dummyjson.com/products?limit=0"
CACHE_PATH = BASE_DIR / "data" / "dummyjson_products.json"
USD_TO_INR_RATE = Decimal(os.getenv("USD_TO_INR_RATE", "95.5"))
SYNC_INTERVAL_HOURS = int(os.getenv("DUMMYJSON_SYNC_INTERVAL_HOURS", "24"))


def load_cached_catalog() -> dict:
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def fetch_dummyjson_catalog() -> dict:
    if os.getenv("DUMMYJSON_USE_CACHE_ONLY", "").lower() in {"1", "true", "yes"}:
        return load_cached_catalog()

    request = Request(
        DUMMYJSON_URL,
        headers={"User-Agent": "eCommerce-Catalog-Importer/1.0"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except Exception:
        return load_cached_catalog()


def should_sync_catalog() -> bool:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'dummyjson_last_sync';"
        ).fetchone()

    if row is None:
        return True

    last_sync = datetime.fromisoformat(row["value"])
    return datetime.now(timezone.utc) - last_sync >= timedelta(
        hours=SYNC_INTERVAL_HOURS
    )


def convert_usd_to_inr(usd_price: int | float | str) -> Decimal:
    return (Decimal(str(usd_price)) * USD_TO_INR_RATE).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )


def import_dummyjson_products(force: bool = False) -> int:
    initialize_database()
    if not force and not should_sync_catalog():
        return 0

    catalog = fetch_dummyjson_catalog()
    products = catalog.get("products", [])

    with get_connection() as connection:
        previous_sync = connection.execute(
            "SELECT value FROM app_metadata WHERE key = 'dummyjson_last_sync';"
        ).fetchone()
        first_sync = previous_sync is None

        for product in products:
            price_inr = convert_usd_to_inr(product["price"])
            brand = product.get("brand") or "Unbranded"
            images = product.get("images") or []

            connection.execute(
                """
                INSERT INTO products (
                    id,
                    sku,
                    name,
                    description,
                    category,
                    brand,
                    price,
                    currency,
                    stock_quantity,
                    is_active,
                    source,
                    source_price_usd,
                    discount_percentage,
                    rating,
                    thumbnail,
                    images_json,
                    tags_json,
                    raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'INR', ?, 1, 'dummyjson', ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    sku = excluded.sku,
                    name = excluded.name,
                    description = excluded.description,
                    category = excluded.category,
                    brand = excluded.brand,
                    price = excluded.price,
                    currency = excluded.currency,
                    stock_quantity = excluded.stock_quantity,
                    is_active = excluded.is_active,
                    source = excluded.source,
                    source_price_usd = excluded.source_price_usd,
                    discount_percentage = excluded.discount_percentage,
                    rating = excluded.rating,
                    thumbnail = excluded.thumbnail,
                    images_json = excluded.images_json,
                    tags_json = excluded.tags_json,
                    raw_json = excluded.raw_json;
                """,
                (
                    product["id"],
                    product["sku"],
                    product["title"],
                    product["description"],
                    product["category"],
                    brand,
                    str(price_inr),
                    product["stock"],
                    str(product["price"]),
                    product.get("discountPercentage"),
                    product.get("rating"),
                    product.get("thumbnail"),
                    json.dumps(images),
                    json.dumps(product.get("tags") or []),
                    json.dumps(product),
                ),
            )
            connection.execute(
                """
                INSERT INTO inventory_items (product_id, sku, available_quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    sku = excluded.sku,
                    available_quantity = CASE
                        WHEN ? THEN excluded.available_quantity
                        ELSE inventory_items.available_quantity
                    END,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    product["id"],
                    product["sku"],
                    product["stock"],
                    first_sync,
                ),
            )

        connection.execute(
            """
            INSERT INTO app_metadata (key, value)
            VALUES ('dummyjson_last_sync', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """,
            (datetime.now(timezone.utc).isoformat(),),
        )

    return len(products)


if __name__ == "__main__":
    imported_count = import_dummyjson_products(force=True)
    print(
        f"Imported {imported_count} DummyJSON products at "
        f"1 USD = {USD_TO_INR_RATE} INR"
    )
