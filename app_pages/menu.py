from html import escape


import streamlit as st

from database import get_products
from ordering import render_ordering

# Read current product information from the database.
products = get_products()

# Keep the menu narrower than the banner.
left_space, menu_column, right_space = st.columns([1, 8, 1])

with menu_column:
    st.subheader("Menu")

    if not products:
        st.info("We are sorry - Menu is empty :(")

    else:
        # Build category options from the stored products.
        categories = ["All categories"] + sorted({
            product["category"] for product in products
        })

        highest_price = max(
            product["price_pence"] for product in products
        ) / 100

        category_column, budget_column = st.columns(2)

        with category_column:
            selected_category = st.selectbox(
                "Select a category",
                options=categories,
            )

        with budget_column:
            maximum_price = st.number_input(
                "Maximum price per item (£)",
                min_value=0.0,
                value=float(highest_price),
                step=0.10,
                format="%.2f",
            )

        available_only = st.checkbox(
            "Show available items only",
            value=False,
        )

        # Convert the selected budget to pence for comparison.
        budget_pence = round(maximum_price * 100)
        menu_rows = []
        
        # For each product, check if it matches the selected category, budget, and availability.

        for product in products:
            if (
                selected_category != "All categories"
                and product["category"] != selected_category
            ):
                continue

            if product["price_pence"] > budget_pence:
                continue

            if available_only and product["stock_quantity"] <= 0:
                continue

            if product["stock_quantity"] > 0:
                availability = "Available"
            else:
                availability = "Out of Stock"

            menu_rows.append({
                "Product": product["name"],
                "Category": product["category"],
                "Price": f"£{product['price_pence'] / 100:.2f}",
                "Availability": availability,
                "Description": product["description"],
            })

        st.caption(f"{len(menu_rows)} matching products")

        # Display an HTML table without using PyArrow as PyArrow gets blocked by windows security settings.
        if menu_rows:
            columns = [
                "Product",
                "Category",
                "Price",
                "Availability",
                "Description",
            ]

            header_html = "".join(
                f"<th>{escape(column)}</th>"
                for column in columns
            )

            rows_html = ""

            for row in menu_rows:
                cells_html = "".join(
                    f"<td>{escape(str(row[column]))}</td>"
                    for column in columns
                )
                
                # CSS styling for the table is applied to make it visually appealing and readable, with a black background and white text. 

                rows_html += f"<tr>{cells_html}</tr>"

            st.html(f"""
                <style>
                .coffee-menu {{
                    width: 100%;
                    border-collapse: collapse;
                    background: black;
                    color: white;
                }}

                .coffee-menu th,
                .coffee-menu td {{
                    padding: 12px;
                    border: 1px solid dimgray;
                    text-align: left;
                }}

                .coffee-menu th {{
                    background: darkslategray;
                }}
                </style>

                <div style="overflow-x: auto;">
                    <table class="coffee-menu">
                        <thead>
                            <tr>{header_html}</tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            """)
            
            # If no matching products are found, display an informational message.

        else:
            st.info(
                "Oops - I couldn't find your brew :( "
                "Please try another category or increase your budget."
            )
            
with menu_column:
    render_ordering()