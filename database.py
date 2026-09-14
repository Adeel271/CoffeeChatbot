import csv
import sqlite3
from pathlib import Path

# Creating CSV Read Paths 

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "coffee_shop.db"
MENU_PATH = BASE_DIR / "menu.csv"

def initialise_database():

    with MENU_PATH.open(newline="" , encoding="utf-8-sig") as  menu_file:
        products = list(csv.DictReader(menu_file))

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        with connection:


            connection.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price_pence INTEGER NOT NULL CHECK (price_pence >= 0),
                    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
                    description TEXT NOT NULL
                )
            """)

            # Allocating variable values to connections (products)

            for product in products:

                 connection.execute ("""
                    INSERT INTO products (
                        product_id,
                        name,
                        category,
                        price_pence,
                        stock_quantity,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(product_id) DO NOTHING
                """, (
                    int(product["product_id"]),
                    product["name"],
                    product["category"],
                    int(product["price_pence"]),
                    int(product["stock_quantity"]),
                    product["description"],
                ))

            count = connection.execute(
                "SELECT COUNT(*) FROM products"
            ).fetchone()[0]

            # Getting the product count from the database depending on the availability of the product


            print(f"Databse ready: {count} products stored.")


    finally:

            connection.close()


# Connecting the app to the database

def get_products():

     connection = sqlite3.connect(DATABASE_PATH)
     connection.row_factory = sqlite3.Row


     query = connection.execute(
               "SELECT product_id, name, category, price_pence, "
               "stock_quantity, description "
               "FROM products"
               "ORDER By product_id"
          )
     try:
          products = connection.execute(query).fetchall()
          return products
     finally:
          connection.close()

              


if __name__ == "__main__":
     initialise_database()






