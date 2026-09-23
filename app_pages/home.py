from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

# Picks up the image file from the system to intergrate the banner image.

banner_path = BASE_DIR / "assets" / "coffee-banner-variety.png"

st.image(str(banner_path), width="stretch")

# Text alignment and styling parameters are set using HTML and CSS to create a visually appealing welcome message for the coffee shop.

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

# Spacing is added to create a applealing layout and improve readability.

left_space, content, right_space = st.columns([1, 8, 1])

with content:
    st.write(
        "Explore Our Menu To Find Your Favourite Brew - Click Below To Get Started!"
        
    )
    
    # A link is provided to navigate to the menu page with an icon and label for user interaction.

    st.page_link(
        "app_pages/menu.py",
        label="Browse the menu and order",
        icon=":material/shopping_cart:",
    )