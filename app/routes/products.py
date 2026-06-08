from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from app.database import get_connection
from app.schemas import ProductCreate, ProductListResponse, ProductResponse, StockUpdate


router = APIRouter(prefix="/products", tags=["products"])


def serialize_product(row) -> ProductResponse:
    return ProductResponse(
        id=row["id"],
        sku=row["sku"],
        name=row["name"],
        description=row["description"],
        category=row["category"],
        brand=row["brand"],
        price=Decimal(row["price"]),
        currency=row["currency"],
        stock_quantity=row["current_stock"] if "current_stock" in row.keys() else row["stock_quantity"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
    )


@router.get("", response_model=ProductListResponse)
def list_products(
    category: str | None = None,
    search: str | None = Query(default=None, min_length=2),
    in_stock: bool | None = None,
) -> ProductListResponse:
    query = """
        SELECT
            products.*,
            COALESCE(inventory_items.available_quantity, products.stock_quantity) AS current_stock
        FROM products
        LEFT JOIN inventory_items ON inventory_items.product_id = products.id
        WHERE products.is_active = 1
    """
    params: list[object] = []

    if category:
        query += " AND lower(products.category) = lower(?)"
        params.append(category)

    if search:
        query += " AND (lower(products.name) LIKE lower(?) OR lower(products.description) LIKE lower(?))"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    if in_stock is True:
        query += " AND COALESCE(inventory_items.available_quantity, products.stock_quantity) > 0"
    elif in_stock is False:
        query += " AND COALESCE(inventory_items.available_quantity, products.stock_quantity) = 0"

    query += " ORDER BY products.category, products.name"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    products = [serialize_product(row) for row in rows]
    return ProductListResponse(count=len(products), products=products)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int) -> ProductResponse:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                products.*,
                COALESCE(inventory_items.available_quantity, products.stock_quantity) AS current_stock
            FROM products
            LEFT JOIN inventory_items ON inventory_items.product_id = products.id
            WHERE products.id = ? AND products.is_active = 1
            """,
            (product_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return serialize_product(row)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate) -> ProductResponse:
    with get_connection() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO products (
                    sku, name, description, category, brand, price, currency, stock_quantity
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    product.sku,
                    product.name,
                    product.description,
                    product.category,
                    product.brand,
                    str(product.price),
                    product.currency.upper(),
                    product.stock_quantity,
                ),
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product SKU already exists or product data is invalid",
            ) from exc

        row = connection.execute(
            """
            SELECT
                products.*,
                COALESCE(inventory_items.available_quantity, products.stock_quantity) AS current_stock
            FROM products
            LEFT JOIN inventory_items ON inventory_items.product_id = products.id
            WHERE products.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        connection.execute(
            """
            INSERT INTO inventory_items (product_id, sku, available_quantity)
            VALUES (?, ?, ?);
            """,
            (row["id"], row["sku"], row["stock_quantity"]),
        )

    return serialize_product(row)


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(product_id: int, stock_update: StockUpdate) -> ProductResponse:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE products
            SET stock_quantity = ?
            WHERE id = ? AND is_active = 1;
            """,
            (stock_update.stock_quantity, product_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        connection.execute(
            """
            INSERT INTO inventory_items (product_id, sku, available_quantity)
            SELECT id, sku, ?
            FROM products
            WHERE id = ?
            ON CONFLICT(product_id) DO UPDATE SET
                available_quantity = excluded.available_quantity,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (stock_update.stock_quantity, product_id),
        )
        row = connection.execute(
            """
            SELECT
                products.*,
                COALESCE(inventory_items.available_quantity, products.stock_quantity) AS current_stock
            FROM products
            LEFT JOIN inventory_items ON inventory_items.product_id = products.id
            WHERE products.id = ?
            """,
            (product_id,),
        ).fetchone()

    return serialize_product(row)
