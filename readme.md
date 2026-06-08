# eCommerce Platform

This project is a FastAPI-based eCommerce backend with a simple frontend, SQLite persistence, authentication, cart, catalog, inventory, and order flows.

The application starts from [`app/main.py`](./app/main.py). On startup it:

1. Initializes the SQLite database in `data/catalog.db`.
2. Imports products from DummyJSON.
3. Serves the storefront at `/` and the API at `/docs`.

## What You Need

- Python 3.11 or newer
- `pip`
- Internet access for the initial DummyJSON import, unless you run in cache-only mode

## Quick Start

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your local environment variables:

```bash
cp .env.example .env
```

Update `.env` if needed. The key values are:

- `JWT_SECRET`: Required for auth tokens. Use a long, random value.
- `USD_TO_INR_RATE`: Conversion rate used when importing DummyJSON prices. Default: `95.5`.
- `DUMMYJSON_SYNC_INTERVAL_HOURS`: How often the catalog refreshes. Default: `24`.
- `DUMMYJSON_USE_CACHE_ONLY`: Set to `1`, `true`, or `yes` to skip network access and use `data/dummyjson_products.json`.

Start the app:

```bash
uvicorn app.main:app --reload
```

Open these URLs in your browser:

- `http://127.0.0.1:8000` for the storefront
- `http://127.0.0.1:8000/docs` for the interactive API docs

## First Run Behavior

When the server starts for the first time, it creates the local SQLite database and imports the DummyJSON catalog.

If you want to force a full catalog import manually, run:

```bash
python -m app.catalog_import
```

## Running Tests

The repository includes pytest-based tests. Run them with:

```bash
pytest
```

## Project Layout

```text
app/
  main.py
  database.py
  catalog_import.py
  frontend/
    index.html
    styles.css
    app.js
  services/
    auth/
    cart/
    catalog/
    inventory/
    orders/
data/
  catalog.db
  dummyjson_products.json
tests/
requirements.txt
```

## Service Overview

- `catalog`: Product data and product listing APIs.
- `inventory`: Stock quantity, reservation, and purchase handling.
- `orders`: Order creation and order history.
- `auth`: User registration, login, and JWT authentication.
- `cart`: Per-user shopping carts and checkout flow.
- `frontend`: The browser UI for browsing products, signing in, and checking out.
- `catalog_import.py`: DummyJSON synchronization and USD-to-INR conversion.
- `database.py`: Shared SQLite initialization and connections.
- `main.py`: FastAPI application setup and route registration.

## API Summary

- `GET /health`: Health check
- `GET /products`: List products
- `GET /products/{product_id}`: View one product
- `POST /products`: Create a product
- `PATCH /products/{product_id}/stock`: Update product stock
- `GET /inventory`: List inventory
- `GET /inventory/{product_id}`: View inventory for one product
- `PATCH /inventory/{product_id}`: Set stock quantity
- `POST /inventory/{product_id}/reserve`: Reserve stock
- `POST /inventory/{product_id}/purchase`: Deduct stock after purchase
- `GET /orders`: List orders
- `GET /orders/{order_id}`: View one order
- `POST /orders`: Create an order
- `POST /auth/register`: Register a user
- `POST /auth/login`: Log in and receive a bearer token
- `GET /auth/me`: Read the signed-in user profile
- `GET /cart`: View the current user cart
- `POST /cart/items`: Add an item to cart
- `PATCH /cart/items/{product_id}`: Update cart item quantity
- `DELETE /cart/items/{product_id}`: Remove one cart item
- `DELETE /cart`: Clear the cart
- `POST /cart/checkout`: Create an order from the cart

Protected routes require:

```text
Authorization: Bearer <access_token>
```

## Notes

- The SQLite schema is created automatically in `data/catalog.db` if it does not already exist.
- Product prices are imported from DummyJSON in USD and stored in INR.
- Local stock changes made by inventory and orders are preserved on later catalog refreshes.
