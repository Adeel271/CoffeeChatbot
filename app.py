import base64
import streamlit as st
from database import get_products
from pathlib import Path


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

display_banner_path = Path(__file__).resolve().parent / "assets" / "coffee-banner-variety.png"
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