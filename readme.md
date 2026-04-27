# eCommerce API

A Python-based REST API for managing an online store with product inventory, shopping cart, and user authentication.

## Overview

This is a starter eCommerce platform built with:
- **FastAPI** — modern, fast web framework for APIs
- **PostgreSQL** — relational database for products, users, and cart data
- **OAuth2 + JWT** — secure user authentication and token-based access control
- **Pydantic** — request/response validation

## Features

### Product Management
- List all products from inventory with details (price, stock, description).
- Seed initial product data into the database.
- Filter and search products.

### User Authentication
- User registration (email, password, full name).
- Login via username/password to receive JWT access token.
- Token-based authentication for protected endpoints.
- User data persisted in PostgreSQL.

### Shopping Cart
- Add products to cart (per user).
- View cart contents with product details and total price.
- Update quantity or remove items.
- Clear entire cart.

### Checkout
- Place orders from cart items.
- Order data saved to database.

## Project Structure

```
eCommerce/
├── main.py                    # FastAPI app entrypoint, router registration
├── .env                       # Environment variables (DB, secrets)
├── requirements.txt           # Python dependencies
├── readme.md                  # This file
├── constants/
│   └── constants.py           # App-wide constants
├── src/
│   └── api/
│       ├── auth/              # Authentication (routes, JWT, password hashing)
│       │   ├── routes.py
│       │   └── auth.py
│       ├── db/
│       │   ├── connection.py  # PostgreSQL connection helper
│       │   ├── seeding.py     # Seed initial product data
│       │   ├── users.py       # User DB helpers
│       │   └── cart/
│       │       └── crud/
│       │           ├── create.py    # Add to cart
│       │           ├── read.py      # Get cart
│       │           ├── update.py    # Update cart quantity
│       │           └── delete.py    # Remove from cart / clear cart
│       ├── inventory/
│       │   └── inventoryStock.py    # List all products
│       └── order/
│           └── checkoutCart.py      # Checkout / place order
└── tests/                     # Unit tests (coming soon)
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Step 1: Clone & Navigate
```bash
cd /Users/prince/dev/projects/genAI/python_projects/eCommerce
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or: .venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create/update `.env` file with your PostgreSQL credentials:
```env
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
```

### Step 5: Seed Data
Run the seeding script to create tables and populate initial products:
```bash
python src/api/db/seeding.py
```

## Running the Application

### Option 1: Module Mode (Recommended)
```bash
uvicorn src.api.main:app --reload
```

### Option 2: Direct Run
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

Interactive API docs: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /auth/register` — Create new user account
  - Body: `{ "email": "user@example.com", "password": "secret", "full_name": "John Doe" }`
  - Returns: user id, email, full_name

- `POST /auth/token` — Login and get access token
  - Body (form-data): `username=user@example.com&password=secret`
  - Returns: `{ "access_token": "...", "token_type": "bearer" }`

### Inventory
- `GET /inventory/products` — List all products
  - Returns: array of products with id, name, description, stock, price, created_at

### Cart (Requires Authentication)
- `POST /cart/add` — Add product to cart
  - Header: `Authorization: Bearer {access_token}`
  - Body: `{ "user_id": 1, "product_id": 5, "quantity": 2 }`
  - Returns: success message

- `GET /cart/{user_id}` — Get user's cart
  - Header: `Authorization: Bearer {access_token}`
  - Returns: cart items with totals and grand total

- `PUT /cart/update` — Update cart item quantity
  - Header: `Authorization: Bearer {access_token}`
  - Body: `{ "user_id": 1, "product_id": 5, "quantity": 3 }`
  - Returns: success message

- `DELETE /cart/clear` — Clear entire cart
  - Header: `Authorization: Bearer {access_token}`
  - Body: `{ "user_id": 1 }`
  - Returns: success message

### Orders
- `POST /order/checkout` — Place order from cart
  - Header: `Authorization: Bearer {access_token}`
  - Body: `{ "user_id": 1 }`
  - Returns: order confirmation with order id

## Database Schema

### users
```sql
id (SERIAL PRIMARY KEY)
email (TEXT UNIQUE NOT NULL)
full_name (TEXT)
hashed_password (TEXT NOT NULL)
created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### products
```sql
id (SERIAL PRIMARY KEY)
name (TEXT UNIQUE NOT NULL)
description (TEXT)
stock (INT NOT NULL)
price (NUMERIC NOT NULL)
created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### cart
```sql
id (SERIAL PRIMARY KEY)
user_id (INT NOT NULL FOREIGN KEY -> users.id)
product_id (INT NOT NULL FOREIGN KEY -> products.id)
quantity (INT NOT NULL)
created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
UNIQUE(user_id, product_id)
```

### orders (optional, for checkout)
```sql
id (SERIAL PRIMARY KEY)
user_id (INT NOT NULL FOREIGN KEY -> users.id)
total_price (NUMERIC(12,2))
status (TEXT DEFAULT 'pending')
created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

## Usage Example (Flow)

1. **Register a user**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"john@example.com", "password":"secure123", "full_name":"John Doe"}'
   ```

2. **Login and get token**
   ```bash
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=john@example.com&password=secure123"
   ```

3. **Browse products**
   ```bash
   curl http://localhost:8000/inventory/products
   ```

4. **Add to cart** (use token from step 2)
   ```bash
   curl -X POST http://localhost:8000/cart/add \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user_id":1, "product_id":3, "quantity":2}'
   ```

5. **View cart**
   ```bash
   curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
     http://localhost:8000/cart/1
   ```

6. **Checkout**
   ```bash
   curl -X POST http://localhost:8000/order/checkout \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user_id":1}'
   ```

## Future Enhancements

- [ ] Social login (Google, GitHub OAuth).
- [ ] Email verification on registration.
- [ ] Product search and filtering.
- [ ] Payment gateway integration (Stripe, Razorpay).
- [ ] Order history and tracking.
- [ ] Product reviews and ratings.
- [ ] Admin dashboard for inventory management.
- [ ] Unit and integration tests (pytest).
- [ ] API rate limiting and security headers.
- [ ] Docker containerization.

## Notes & Best Practices

- Keep `.env` file with secrets **out of version control** (already in `.gitignore`).
- Use strong SECRET_KEY in production (generate with `openssl rand -hex 32`).
- Always use HTTPS in production.
- Set short token expiration times and implement refresh tokens.
- Validate user input and use Pydantic models.
- Convert currency values to Decimal type to avoid float rounding errors.
- Add unit tests before adding new features.

## Troubleshooting

### Import errors (ModuleNotFoundError)
- Run with: `uvicorn src.api.main:app --reload`
- Or ensure `src/` folder has `__init__.py` files.

### Database connection fails
- Check `.env` credentials match your PostgreSQL setup.
- Ensure PostgreSQL is running: `psql -U postgres`
- Verify database exists: `psql -l` or run seeding script.

### No products in inventory
- Run: `python src/api/db/seeding.py` to populate initial data.

## License & Contribution

This is a starter project — adapt and extend freely. Open issues or PRs for improvements.

## Contact

For questions, reach out or check the project issues.
### User Authentication & Data Management

The application implements a user-based authentication system using JSON Web Tokens (JWT). A single shared database schema is used to manage all users and their associated data.

A centralized table structure is maintained for entities such as cart_items and wishlist, where each record is linked to a specific user through a user_id field. Instead of creating separate tables per user, this approach ensures scalability and efficient data management.

When a user logs in, a JWT token containing the user_id is generated. For every authenticated request, this token is sent in the request header and decoded on the backend to extract the user's identity.

Using this user_id, SQL queries are executed to retrieve user-specific data. For example:

- Fetch cart items:
  SELECT * FROM cart_items WHERE user_id = <user_id>;

- Fetch wishlist items:
  SELECT * FROM wishlist WHERE user_id = <user_id>;

This design allows multiple users to share the same tables while ensuring that each user can only access their own data through backend-controlled queries.

Overall, the system follows a scalable and secure approach by combining JWT-based authentication with relational database design using user-specific filtering.