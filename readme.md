# eCommerce (starter)

- Small Python/Postgres demo app for product inventory and a shopping cart.
- Purpose: learning DB-backed CRUD workflows, seeding data, and basic cart operations.

Key features
- Product management: add and seed sample products.
- Cart operations: add items to cart (support for quantity and total price).
- Simple scripts to create tables and seed data.
- Configuration via .env (Postgres connection settings).

Quick start
- Prerequisites: Python 3.8+, PostgreSQL, pip.
- Install deps:
    - pip install -r requirements.txt
- Configure DB:
    - Create a .env with DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- Set up schema and seed:
    - python db.py            # create database / run setup
    - python src/tables/create_cart_table.py
    - python seed.py
- Run basic scripts:
    - python add_product.py
    - python add_to_cart.py
    - python main.py

Notes & next steps
- Use Decimal for money handling and connection context managers for safety.
- Add operations: get_cart, remove_from_cart, update quantity, empty cart.
- Consider adding migrations (alembic) and unit tests (pytest).

License & contribution
- Minimal starter: adapt freely. Open issues / PRs for improvements.