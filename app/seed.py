from app.database import get_connection, initialize_database


PRODUCTS = [
    ("IPHONE-15", "iPhone 15", "Apple smartphone with A16 chip", "Mobiles", "Apple", 79999, 25),
    ("GALAXY-S23", "Samsung Galaxy S23", "Android phone with AMOLED display", "Mobiles", "Samsung", 74999, 30),
    ("DELL-XPS-13", "Dell XPS 13", "Ultra portable laptop", "Laptops", "Dell", 120000, 10),
    ("MACBOOK-AIR-M2", "MacBook Air M2", "Apple laptop with M2 chip", "Laptops", "Apple", 115000, 12),
    ("HP-PAVILION", "HP Pavilion", "Mid-range laptop for office work", "Laptops", "HP", 65000, 20),
    ("SONY-HEADPHONES", "Sony Headphones", "Noise cancelling headphones", "Audio", "Sony", 29999, 40),
    ("BOAT-EARBUDS", "Boat Earbuds", "Affordable wireless earbuds", "Audio", "boAt", 1999, 100),
    ("JBL-SPEAKER", "JBL Speaker", "Portable Bluetooth speaker", "Audio", "JBL", 4999, 60),
    ("LOGITECH-MOUSE", "Logitech Mouse", "Wireless ergonomic mouse", "Accessories", "Logitech", 2999, 80),
    ("MECH-KEYBOARD", "Mechanical Keyboard", "RGB gaming keyboard", "Accessories", "Generic", 4999, 50),
    ("GAMING-CHAIR", "Gaming Chair", "Ergonomic chair for gamers", "Furniture", "Generic", 15999, 15),
    ("OFFICE-CHAIR", "Office Chair", "Comfortable office chair", "Furniture", "Generic", 8999, 25),
    ("STUDY-TABLE", "Study Table", "Wooden study desk", "Furniture", "Generic", 7000, 18),
    ("LED-MONITOR-24", "LED Monitor 24 inch", "Full HD display monitor", "Monitors", "Generic", 12000, 22),
    ("MONITOR-4K", "4K Monitor", "Ultra HD professional monitor", "Monitors", "Generic", 35000, 8),
    ("HDD-1TB", "External HDD 1TB", "Portable hard drive", "Storage", "Generic", 4500, 40),
    ("SSD-1TB", "SSD 1TB", "High speed storage", "Storage", "Generic", 9000, 35),
    ("PENDRIVE-64GB", "Pendrive 64GB", "USB flash drive", "Storage", "Generic", 700, 120),
    ("ROUTER-WIFI-6", "Router WiFi 6", "High speed internet router", "Networking", "Generic", 6000, 28),
    ("WEBCAM-HD", "Webcam HD", "HD webcam for meetings", "Accessories", "Generic", 2500, 45),
    ("SMARTWATCH", "Smartwatch", "Fitness tracking smartwatch", "Wearables", "Generic", 5000, 30),
    ("APPLE-WATCH", "Apple Watch", "Premium smartwatch", "Wearables", "Apple", 45000, 20),
    ("FITNESS-BAND", "Fitness Band", "Health tracking band", "Wearables", "Generic", 2500, 50),
    ("BLUETOOTH-TRACKER", "Bluetooth Tracker", "Track your items", "Accessories", "Generic", 1500, 70),
    ("POWER-BANK-20000", "Power Bank 20000mAh", "Fast charging power bank", "Power", "Generic", 2000, 60),
    ("CHARGER-65W", "Charger 65W", "Fast laptop charger", "Power", "Generic", 3000, 40),
    ("USB-C-CABLE", "USB-C Cable", "Durable charging cable", "Power", "Generic", 500, 150),
    ("EXTENSION-BOARD", "Extension Board", "Multi plug extension", "Power", "Generic", 800, 90),
    ("BACKPACK-LAPTOP", "Backpack Laptop", "Waterproof laptop bag", "Bags", "Generic", 2500, 35),
    ("TRAVEL-BAG", "Travel Bag", "Large capacity travel bag", "Bags", "Generic", 4000, 20),
    ("WALLET-LEATHER", "Wallet Leather", "Premium leather wallet", "Accessories", "Generic", 1200, 60),
    ("RUNNING-SHOES", "Running Shoes", "Comfortable sports shoes", "Footwear", "Generic", 3000, 50),
    ("SNEAKERS", "Sneakers", "Casual stylish sneakers", "Footwear", "Generic", 3500, 70),
    ("FORMAL-SHOES", "Formal Shoes", "Office wear shoes", "Footwear", "Generic", 4000, 30),
    ("TSHIRT-COTTON", "T-shirt Cotton", "Comfortable cotton t-shirt", "Clothing", "Generic", 800, 100),
    ("JEANS-DENIM", "Jeans Denim", "Slim fit denim jeans", "Clothing", "Generic", 2000, 80),
    ("JACKET-WINTER", "Jacket Winter", "Warm winter jacket", "Clothing", "Generic", 3500, 40),
    ("MICROWAVE-OVEN", "Microwave Oven", "Kitchen appliance", "Kitchen", "Generic", 8000, 15),
    ("AIR-FRYER", "Air Fryer", "Healthy cooking device", "Kitchen", "Generic", 7000, 25),
    ("ELECTRIC-KETTLE", "Electric Kettle", "Quick boiling kettle", "Kitchen", "Generic", 1500, 60),
    ("WATER-BOTTLE", "Water Bottle", "Reusable steel bottle", "Fitness", "Generic", 600, 100),
    ("GYM-DUMBBELLS", "Gym Dumbbells", "Adjustable weights", "Fitness", "Generic", 5000, 20),
    ("YOGA-MAT", "Yoga Mat", "Non-slip exercise mat", "Fitness", "Generic", 1200, 45),
    ("NOTEBOOK-PACK", "Notebook Pack", "Set of notebooks", "Stationery", "Generic", 500, 150),
    ("BALL-PEN-PACK", "Ball Pen Pack", "Smooth writing pens", "Stationery", "Generic", 300, 200),
    ("DESK-LAMP", "Desk Lamp", "LED study lamp", "Stationery", "Generic", 900, 50),
]


def seed_products() -> None:
    initialize_database()

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO products (
                sku, name, description, category, brand, price, stock_quantity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sku) DO NOTHING;
            """,
            PRODUCTS,
        )
        connection.execute(
            """
            INSERT INTO inventory_items (product_id, sku, available_quantity)
            SELECT id, sku, stock_quantity
            FROM products
            WHERE id NOT IN (SELECT product_id FROM inventory_items);
            """
        )
