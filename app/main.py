from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import initialize_database
from app.routes.inventory import router as inventory_router
from app.routes.products import router as products_router
from app.seed import seed_products


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    seed_products()
    yield


app = FastAPI(
    title="eCommerce Catalog Service",
    description="Catalog API for product information in the eCommerce platform.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "catalog"}


app.include_router(products_router)
app.include_router(inventory_router)
