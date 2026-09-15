import base64
import streamlit as st
from database import get_products, update_product
from pathlib import Path
from html import escape

st.set_page_config(page_title="One Stop Coffee")

# Adding a red strip - ssplit background to make it more interactive using html / CSS

banner_path = Path(__file__).resolve().parent / "assets" / "coffee-banner.png"
background_image = base64.b64encode(banner_path.read_bytes()).decode("utf-8")

# Adding interactive background of the app

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

# Adding coffee banner to the welcome page

display_banner_path = (
    Path(__file__).resolve().parent / "assets" / "coffee-banner-variety.png"
)
st.image(str(display_banner_path), width="stretch")

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


# Creating an interactive menu for user convinience

products = get_products()

left_space, menu_column, right_space = st.columns([1, 8, 1])

with menu_column:
    st.subheader("Menu")

    if not products:
        st.info("We are sorry - Menu is empty :(")

    else:
        categories = ["All categories"] + sorted(
            {product["category"] for product in products}
        )

        highest_price = max(product["price_pence"] for product in products) / 100

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

            menu_rows.append(
                {
                    "Product": product["name"],
                    "Category": product["category"],
                    "Price": f"£{product['price_pence'] / 100:.2f}",
                    "Availability": availability,
                    "Description": product["description"],
                }
            )

        st.caption(f"{len(menu_rows)} matching products")

        if menu_rows:
            st.dataframe(
                menu_rows,
                hide_index=True,
                width="stretch",
            )
        else:
            st.info(
                "Oops - I couldn't find your brew :( "
                "Please try another category or increase your budget."
            )

            # Adding filters to manage inventory

with menu_column:
    st.divider()

    if "inventory_notice" in st.session_state:
        st.success(st.session_state.pop("inventory_notice"))

        with st.expander("Manage inventory"):
            st.caption("Inventory Editor")

            if products:
                products_by_id = {
                    product["product_id"]: product for products in product
                }

                selected_id = st.selectbox(
                    "Select a product to update",
                    options=list(products_by_id),
                    format_func=lambda product_id: (products_by_id[product_id]["name"]),
                    key="inventory_product",
                )

                # This input in streamlit library will enable parameters to set the product price in correct format

                selected_product = products_by_id[selected_id]

                with st.form(key=f"inventory_form_{selected_id}"):
                    new_price = st.number_input(
                        "Product price (£)",
                        main_value=0.0,
                        value=float(selected_product["price_pence"] / 100),
                        step=0.10,
                        format="%.2f",
                        key=f"price_{selected_id}",
                    )

                # These parameters will enable the app to add new products

                new_stock = st.number_input(
                    "Stock quantity",
                    min_value=0,
                    value=int(selected_product["stock_quantity"]),
                    step=1,
                    key=f"stock_{selected_id}",
                )

                save_clicked = st.form_submit_button("Save changes")

                if save_clicked:
                    update_product(
                        selected_id,
                        round(new_price * 100),
                        int(new_stock),
                    )

                    st.session_state["inventory_notice"] = (
                        f"save changes for {selected_product["name"]}."
                    )

                    st.rerun()

                else:
                    st.info("No products to update")
