import hmac

import streamlit as st

from database import get_products, update_product

# Prompt for the administrator password to manage inventory. The password is stored in Streamlit secrets.

def check_inventory_password():
    entered_password = st.session_state.pop(
        "inventory_password_input", ""
    )
    saved_password = st.secrets["INVENTORY_PASSWORD"]

    password_matches = hmac.compare_digest(
        entered_password.encode("utf-8"),
        saved_password.encode("utf-8"),
    )
    
    # Setting validation parameters in session state to control access to inventory management.

    st.session_state["inventory_authenticated"] = password_matches
    st.session_state["inventory_login_failed"] = not password_matches
    
    # Validation parameters cleared - if fail restrict access. 


def logout_inventory():
    for key in (
        "inventory_authenticated",
        "inventory_login_failed",
        "inventory_password_input",
        "loaded_inventory_id",
        "inventory_notice",
    ):
        st.session_state.pop(key, None)


left_space, menu_column, right_space = st.columns([1, 8, 1])

with menu_column:
    st.title("Manage Inventory")

    try:
        configured_password = st.secrets["INVENTORY_PASSWORD"]
    except (KeyError, FileNotFoundError):
        st.error("Inventory access has not been configured.")
        st.stop()

    if not isinstance(configured_password, str) or not configured_password:
        st.error("The inventory password must be a non-empty string.")
        st.stop()

    if not st.session_state.get("inventory_authenticated", False):
        st.info("Enter the administrator password to manage inventory.")

        with st.form("inventory_login_form"):
            st.text_input(
                "Administrator password",
                type="password",
                key="inventory_password_input",
            )

            st.form_submit_button(
                "Log in",
                on_click=check_inventory_password,
            )

        if st.session_state.get("inventory_login_failed", False):
            st.error("Incorrect password. Please try again.")

        st.stop()

    st.button("Log out", on_click=logout_inventory)

    
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