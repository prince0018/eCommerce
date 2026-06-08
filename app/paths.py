from pathlib import Path


# Keep all filesystem locations in one place so the backend code reads naturally.
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "catalog.db"
CACHE_PATH = DATA_DIR / "dummyjson_products.json"
