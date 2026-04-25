import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")


def seed_products():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    cur = conn.cursor()

    products = [
        ("iPhone 15", "Apple smartphone with A16 chip", 25, 79999),
        ("Samsung Galaxy S23", "Android phone with AMOLED display", 30, 74999),
        ("Dell XPS 13", "Ultra portable laptop", 10, 120000),
        ("MacBook Air M2", "Apple laptop with M2 chip", 12, 115000),
        ("HP Pavilion", "Mid-range laptop for office work", 20, 65000),
        ("Sony Headphones", "Noise cancelling headphones", 40, 29999),
        ("Boat Earbuds", "Affordable wireless earbuds", 100, 1999),
        ("JBL Speaker", "Portable Bluetooth speaker", 60, 4999),
        ("Logitech Mouse", "Wireless ergonomic mouse", 80, 2999),
        ("Mechanical Keyboard", "RGB gaming keyboard", 50, 4999),

        ("Gaming Chair", "Ergonomic chair for gamers", 15, 15999),
        ("Office Chair", "Comfortable office chair", 25, 8999),
        ("Study Table", "Wooden study desk", 18, 7000),
        ("LED Monitor 24 inch", "Full HD display monitor", 22, 12000),
        ("4K Monitor", "Ultra HD professional monitor", 8, 35000),

        ("External HDD 1TB", "Portable hard drive", 40, 4500),
        ("SSD 1TB", "High speed storage", 35, 9000),
        ("Pendrive 64GB", "USB flash drive", 120, 700),
        ("Router WiFi 6", "High speed internet router", 28, 6000),
        ("Webcam HD", "HD webcam for meetings", 45, 2500),

        ("Smartwatch", "Fitness tracking smartwatch", 30, 5000),
        ("Apple Watch", "Premium smartwatch", 20, 45000),
        ("Fitness Band", "Health tracking band", 50, 2500),
        ("Bluetooth Tracker", "Track your items", 70, 1500),

        ("Power Bank 20000mAh", "Fast charging power bank", 60, 2000),
        ("Charger 65W", "Fast laptop charger", 40, 3000),
        ("USB-C Cable", "Durable charging cable", 150, 500),
        ("Extension Board", "Multi plug extension", 90, 800),

        ("Backpack Laptop", "Waterproof laptop bag", 35, 2500),
        ("Travel Bag", "Large capacity travel bag", 20, 4000),
        ("Wallet Leather", "Premium leather wallet", 60, 1200),

        ("Running Shoes", "Comfortable sports shoes", 50, 3000),
        ("Sneakers", "Casual stylish sneakers", 70, 3500),
        ("Formal Shoes", "Office wear shoes", 30, 4000),

        ("T-shirt Cotton", "Comfortable cotton t-shirt", 100, 800),
        ("Jeans Denim", "Slim fit denim jeans", 80, 2000),
        ("Jacket Winter", "Warm winter jacket", 40, 3500),

        ("Microwave Oven", "Kitchen appliance", 15, 8000),
        ("Air Fryer", "Healthy cooking device", 25, 7000),
        ("Electric Kettle", "Quick boiling kettle", 60, 1500),

        ("Water Bottle", "Reusable steel bottle", 100, 600),
        ("Gym Dumbbells", "Adjustable weights", 20, 5000),
        ("Yoga Mat", "Non-slip exercise mat", 45, 1200),

        ("Notebook Pack", "Set of notebooks", 150, 500),
        ("Ball Pen Pack", "Smooth writing pens", 200, 300),
        ("Desk Lamp", "LED study lamp", 50, 900)
    ]

    cur.executemany("""
    INSERT INTO products (name, description, quantity, price)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name) DO NOTHING;
    """, products)

    conn.commit()
    print("✅ 50 products inserted successfully")

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed_products()