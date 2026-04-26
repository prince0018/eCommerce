"""Application entrypoint and router wiring for the eCommerce API.

This file creates a FastAPI app and includes routers defined under
`src/api/...`. When running directly (python main.py) the src folder
is added to sys.path so imports work during development. Recommended
run mode for full package import resolution is: `python -m src.api.main`
or via uvicorn: `uvicorn src.api.main:app --reload`.
"""

import os
import sys
from fastapi import FastAPI

# When running main.py directly, ensure src/ is on sys.path so
# package imports like `from api.db.cart.crud.create import router` work.
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


def create_app() -> FastAPI:
    app = FastAPI(title="eCommerce API")

    # Import routers from the src package (use absolute package imports)
    from src.api.db.cart.crud.create import router as cart_create_router
    from src.api.db.cart.crud.read import router as cart_read_router
    from src.api.db.cart.crud.update import router as cart_update_router
    from src.api.db.cart.crud.delete import router as cart_delete_router
    from src.api.order.checkoutCart import router as checkout_router
    from src.api.inventory.inventoryStock import router as inventory_router
    from src.api.db.seeding import seed_products

    # Include cart routers under /cart with a 'cart' tag
    app.include_router(cart_create_router, prefix="", tags=["cart"])
    app.include_router(cart_read_router, prefix="", tags=["cart"])
    app.include_router(cart_update_router, prefix="", tags=["cart"])
    app.include_router(cart_delete_router, prefix="", tags=["cart"])

    # Inventory router
    app.include_router(inventory_router, prefix="", tags=["inventory"])

    # Checkout router
    app.include_router(checkout_router, prefix="", tags=["checkout"])

    # Add a simple seeding endpoint (calls the seed function)
    @app.post("/seed", tags=["seeding"])
    def run_seed():
        seed_products()
        return {"message": "Seed completed"}

    return app
.

app = create_app()


if __name__ == "__main__":
    # Allow running directly for development: uvicorn is recommended.
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)