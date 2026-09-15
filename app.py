import base64
from html import escape
from pathlib import Path
from ordering import render_ordering

import streamlit as st

from database import get_products, update_product


st.set_page_config(
    page_title="One Stop Coffee",
    layout="wide",
)

# Locate the project folder and background image.
BASE_DIR = Path(__file__).resolve().parent
background_path = BASE_DIR / "assets" / "coffee-banner.png"

background_image = base64.b64encode(
    background_path.read_bytes()
).decode("utf-8")

# Apply the background and remove space around the banner.
st.html(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(
            rgba(0, 0, 0, 0.65),
            rgba(0, 0, 0, 0.65)
        ),
        url("data:image/png;base64,{background_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    min-height: 100vh;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

[data-testid="stMainBlockContainer"] {{
    max-width: 100%;
    padding-top: 0;
    padding-left: 0;
    padding-right: 0;
}}
</style>
""")

# Display the full-width coffee banner.
display_banner_path = BASE_DIR / "assets" / "coffee-banner-variety.png"

st.image(
    str(display_banner_path),
    width="stretch",
)

# Display the centred heading and welcome message.
st.html("""
<div style="text-align: center; padding: 24px 16px;">
    <h1 style="color: white; margin: 0 0 12px 0;">
        One Stop Coffee
    </h1>
    <p style="color: white; font-size: 18px; margin: 0;">
        Welcome to One Stop Coffee Shop - Let's Get Your Day Started In Style :)
    </p>
</div>
""")

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
                "Choose a category",
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

        else:
            st.info(
                "Oops - I couldn't find your brew :( "
                "Please try another category or increase your budget."
            )
            
with menu_column:
    render_ordering()


# Update existing product prices and stock.

with menu_column:
    st.divider()

    if "inventory_notice" in st.session_state:
        st.success(st.session_state.pop("inventory_notice"))

    with st.expander("Manage inventory"):
        st.caption("Local prototype inventory editor")

        # Read the latest saved values.
        inventory_products = get_products()

        if inventory_products:
            inventory_by_id = {
                product["product_id"]: product
                for product in inventory_products
            }
            
            inventory_options = {
                f"{product['product_id']} — {product['name']}":
                product["product_id"]
                for product in inventory_products
            }
            
            with st.form("inventory_product_loader"):
                selected_inventory_label = st.selectbox(
                    "Select a product to update",
                    options=list(inventory_options),
                    key="inventory_load_selection",
                )

                load_clicked = st.form_submit_button("Load product")

            if load_clicked:
                st.session_state["loaded_inventory_id"] = (
                    inventory_options[selected_inventory_label]
                )

            inventory_id = st.session_state.get("loaded_inventory_id")

            if inventory_id not in inventory_by_id:
                st.info("Choose a product and click Load product.")
                st.stop()

            inventory_product = inventory_by_id[inventory_id]

            saved_price = int(inventory_product["price_pence"])
            saved_stock = int(inventory_product["stock_quantity"])

            st.caption(
                f"Saved in database: "
                f"{inventory_product['name']} — "
                f"£{saved_price / 100:.2f} — "
                f"Stock: {saved_stock}"
            )

            record_key = (
                f"inventory_v2_{inventory_id}_"
                f"{saved_price}_{saved_stock}"
            )

            with st.form(key=f"form_{record_key}"):
                new_price = st.number_input(
                    "Product price (£)",
                    min_value=0.0,
                    value=float(saved_price / 100),
                    step=0.10,
                    format="%.2f",
                    key=f"price_{record_key}",
                )

                new_stock = st.number_input(
                    "Stock quantity",
                    min_value=0,
                    value=saved_stock,
                    step=1,
                    key=f"stock_{record_key}",
                )

                save_clicked = st.form_submit_button("Save changes")

            if save_clicked:
                update_product(
                    inventory_id,
                    round(new_price * 100),
                    int(new_stock),
                )

                st.session_state["inventory_notice"] = (
                    f"Saved changes for {inventory_product['name']}."
                )

                st.rerun()

        else:
            st.info("There are no products to update.")