import streamlit as st


left_space, content, right_space = st.columns([1, 8, 1])

with content:
    st.title("AI Barista")

    st.info(
        "The AI Barista is not connected yet. "
        "You can browse products and place orders on Menu & Order."
    )

    st.page_link(
        "app_pages/menu.py",
        label="Go to Menu & Order",
        icon=":material/shopping_cart:",
    )