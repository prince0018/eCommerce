"""Application entrypoint and router wiring for the eCommerce API.

This file creates a FastAPI app and includes routers defined under
`src/api/routes`. When running directly (python main.py) the src folder
is added to sys.path so imports work during development.
"""

import os
import sys
from fastapi import FastAPI

# When running main.py directly, ensure src/ is on sys.path.
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


def create_app() -> FastAPI:
    app = FastAPI(title="eCommerce API")

    from src.api.routes import auth, cart, checkout, products
    from src.db.seeding import seed_products

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(cart.router)
    app.include_router(checkout.router)

    # Add a simple seeding endpoint (calls the seed function)
    @app.post("/seed", tags=["seeding"])
    def run_seed():
        seed_products()
        return {"message": "Seed completed"}

    return app

app = create_app()


if __name__ == "__main__":
    # Allow running directly for development: uvicorn is recommended.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
