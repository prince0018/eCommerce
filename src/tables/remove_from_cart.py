from db.connection import get_connection


def remove_from_cart(user_id, product_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check if product exists in cart
        cur.execute("""
            SELECT * FROM cart
            WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))

        result = cur.fetchone()

        if not result:
            print("⚠️ Product not found in cart")
        else:
            cur.execute("""
                DELETE FROM cart
                WHERE user_id = %s AND product_id = %s
            """, (user_id, product_id))

            print("🗑️ Product removed from cart")

        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)


# test run
if __name__ == "__main__":
    remove_from_cart(1, 2)