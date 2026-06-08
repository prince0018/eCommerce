from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    id: int
    sku: str
    name: str
    description: str
    category: str
    brand: str
    price: Decimal
    currency: str
    stock_quantity: int
    is_active: bool
    created_at: datetime
