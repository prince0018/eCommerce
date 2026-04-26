from db.connection import get_connection


def add_to_cart(user_id, product_id, quantity):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check if product already exists
        cur.execute("""
            SELECT quantity FROM cart
            WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))

        result = cur.fetchone()

        if result:
            new_quantity = result[0] + quantity

            cur.execute("""
                UPDATE cart
                SET quantity = %s
                WHERE user_id = %s AND product_id = %s
            """, (new_quantity, user_id, product_id))

            print("🔁 Updated quantity")

        else:
            cur.execute("""
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (user_id, product_id, quantity))

            print("🆕 Added to cart")

        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)


# test run
if __name__ == "__main__":
    add_to_cart(1, 2, 3)