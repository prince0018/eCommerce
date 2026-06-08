from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.catalog_import import import_dummyjson_products
from app.database import initialize_database
from app.services.auth.routes import router as auth_router
from app.services.cart.routes import router as cart_router
from app.services.catalog.routes import router as catalog_router
from app.services.inventory.routes import router as inventory_router
from app.services.orders.routes import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database schema and preload products before the app starts serving traffic.
    initialize_database()
    import_dummyjson_products()
    yield


app = FastAPI(
    title="eCommerce Services",
    description="Catalog, Inventory, Order, Auth/User, and Cart APIs.",
    version="0.1.0",
    lifespan=lifespan,
)

# Serve the built-in frontend directly from the backend package.
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def storefront() -> FileResponse:
    # Serve the homepage.
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    # Return a simple health status.
    return {"status": "ok", "service": "ecommerce"}


app.include_router(catalog_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(auth_router)
app.include_router(cart_router)
