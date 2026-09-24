import sqlite3

from database import DATABASE_PATH

# Initialize the orders database and provide functions to place orders. Connect SQLite.


def initialise_orders():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkout_key TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total_pence INTEGER NOT NULL CHECK(total_pence >= 0),
                    payment_status TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id INTEGER NOT NULL REFERENCES orders(order_id),
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    unit_price_pence INTEGER NOT NULL CHECK(unit_price_pence >= 0),
                    PRIMARY KEY(order_id, product_id)
                )
            """)

    finally:
        connection.close()
        
        # Setting up the database tables for orders and order items, ensuring that they exist before any operations are performed.


def place_order(basket, checkout_key):
    if not basket:
        raise ValueError("Your basket is empty.")

    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.execute("BEGIN IMMEDIATE")

        existing = connection.execute(
            "SELECT order_id, total_pence FROM orders WHERE checkout_key = ?",
            (checkout_key,),
        ).fetchone()

        if existing:
            connection.rollback()
            return dict(existing)

        lines = []
        total = 0

        for product_id, item in basket.items():
            quantity = item["quantity"]

            if type(quantity) is not int or quantity <= 0:
                raise ValueError(
                    "Each quantity must be a positive whole number."
                )

            product = connection.execute(
                "SELECT * FROM products WHERE product_id = ?",
                (product_id,),
            ).fetchone()

            if product is None:
                raise ValueError(
                    "A product is no longer available. "
                    "Remove it from your basket."
                )

            if product["price_pence"] != item["price_pence"]:
                raise ValueError(
                    f"The price of {product['name']} changed. "
                    "Remove it and add it again to review the new price."
                )

            if product["stock_quantity"] < quantity:
                raise ValueError(
                    f"Not enough stock for {product['name']}. "
                    "Reduce its quantity or remove it."
                )

            total += product["price_pence"] * quantity
            lines.append((product, quantity))

        cursor = connection.execute(
            "INSERT INTO orders "
            "(checkout_key, total_pence, payment_status) "
            "VALUES (?, ?, ?)",
            (checkout_key, total, "simulated_paid"),
        )

        order_id = cursor.lastrowid

        for product, quantity in lines:
            connection.execute(
                "INSERT INTO order_items "
                "(order_id, product_id, product_name, quantity, unit_price_pence) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    order_id,
                    product["product_id"],
                    product["name"],
                    quantity,
                    product["price_pence"],
                ),
            )

            connection.execute(
                "UPDATE products "
                "SET stock_quantity = stock_quantity - ? "
                "WHERE product_id = ?",
                (quantity, product["product_id"]),
            )

        connection.commit()

        return {
            "order_id": order_id,
            "total_pence": total,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()