import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")


def add_to_cart(product_name, quantity):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        cur = conn.cursor()

        # 🔍 Get product details
        cur.execute("""
        SELECT id, price, quantity FROM products WHERE name = %s;
        """, (product_name,))
        
        product = cur.fetchone()

        if not product:
            print("❌ Product not found")
            return

        product_id, price, available_qty = product

        # ⚠️ Check stock
        if quantity > available_qty:
            print("❌ Not enough stock available")
            return

        total_price = price * quantity

        # 🛒 Insert into cart
        cur.execute("""
        INSERT INTO cart (product_id, quantity, total_price)
        VALUES (%s, %s, %s);
        """, (product_id, quantity, total_price))

        # 🔄 Reduce stock from products
        cur.execute("""
        UPDATE products
        SET quantity = quantity - %s
        WHERE id = %s;
        """, (quantity, product_id))

        conn.commit()

        print(f"✅ Added to cart: {product_name} (x{quantity})")

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    add_to_cart("iPhone 15", 2)