import streamlit as st

from database import get_products, update_product


left_space, menu_column, right_space = st.columns([1, 8, 1])

with menu_column:
    st.title("Manage Invetory")
    
    
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