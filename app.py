import streamlit as st
from database import get_products


st.set_page_config(page_title="One Stop Coffee")

# Adding a red strip - ssplit background to make it more interactive using html / CSS

st.html("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        135deg,
        #0D0D0D 0%,
        #0D0D0D 38%,
        #9B111E 38%,
        #9B111E 62%,
        #0D0D0D 62%,
        #0D0D0D 100%
    );
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: transparent;
}
</style>
""")

st.title("One Stop Coffee")
st.write("Welcome to One Stop Coffee Shop -  Let's Get Your Day Started In Style :)")


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
            "Price": f"£{product['price_pence'] / 100:.2f}",
            "Availability": availability,
            "Description": product["description"],
        })

st.dataframe(menu_rows, hide_index=True)