import streamlit as st
from database import get_products


st.set_page_config(page_title="One Stop Coffee")

st.title("One Stop Coffee")
st.write("Welcome! I Am Your Digital Barista - Let's Get Your Day Started In Style :)")


st.subheader("Our Brew")

products = get_products()
menu_rows = []


for product in products:

    if product["stock_quantity"] > 0:
        availability = "Available"
    else:
        availability = "Out of Stock"

    menu_rows.append({
            "Product": product["name"],
            "Category": product["category"],
            "Price": f"£{product['price_pence'] / 100:.f}",
            "Availability": availability,
            "Description": product["description"],
        })

st.dataframe(menu_rows, hide_index=True)