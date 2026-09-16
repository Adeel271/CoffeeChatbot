import base64
from pathlib import Path
from uuid import uuid4

import streamlit as st


st.set_page_config(
    page_title="One Stop Coffee",
    layout="wide",
)

# Shared state survives navigation between pages.
if "basket" not in st.session_state:
    st.session_state["basket"] = {}

if "checkout_key" not in st.session_state:
    st.session_state["checkout_key"] = str(uuid4())

BASE_DIR = Path(__file__).resolve().parent
background_path = BASE_DIR / "assets" / "coffee-banner.png"

background_image = base64.b64encode(
    background_path.read_bytes()
).decode("utf-8")

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
    background: black;
}}

[data-testid="stMainBlockContainer"] {{
    max-width: 100%;
    padding-top: 4rem;
    padding-left: 0;
    padding-right: 0;
}}
</style>
""")

page = st.navigation(
    [
        st.Page(
            "app_pages/home.py",
            title="Home",
            icon=":material/home:",
            default=True,
        ),
        st.Page(
            "app_pages/menu.py",
            title="Menu & Order",
            icon=":material/shopping_cart:",
        ),
        st.Page(
            "app_pages/barista.py",
            title="AI Barista",
            icon=":material/chat:",
        ),
        st.Page(
            "app_pages/inventory.py",
            title="Manage Inventory",
            icon=":material/inventory_2:",
        ),
    ],
    position="top",
)

page.run()