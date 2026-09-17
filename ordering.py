import sqlite3
from uuid import uuid4

import streamlit as st

from database import get_products
from order_database import initialise_orders, place_order


def basket_changed():
    st.session_state["checkout_key"] = str(uuid4())
    st.session_state.pop("order_confirmation", None)


def render_ordering():
    initialise_orders()

    if "basket" not in st.session_state:
        st.session_state["basket"] = {}

    if "checkout_key" not in st.session_state:
        st.session_state["checkout_key"] = str(uuid4())

    basket = st.session_state["basket"]

    # Read current stock independently of the displayed menu filters.
    products = get_products()
    products_by_id = {
        product["product_id"]: product
        for product in products
    }

    available_ids = [
        product["product_id"]
        for product in products
        if product["stock_quantity"] > 0
    ]

    st.divider()
    st.subheader("Place an order")

    st.caption(
        "Choose from all available products. "
        "Items are not reserved until you place your order."
    )

    if "basket_notice" in st.session_state:
        st.success(st.session_state.pop("basket_notice"))

    if "order_confirmation" in st.session_state:
        confirmation = st.session_state["order_confirmation"]

        st.success(
            f"Order #{confirmation['order_id']} placed successfully. "
            f"Total: £{confirmation['total_pence'] / 100:.2f}. "
            "Simulated payment completed — no money was charged."
        )

    if available_ids:
        selected_id = st.selectbox(
            "Choose an item",
            options=available_ids,
            format_func=lambda product_id: (
                f"{products_by_id[product_id]['name']} — "
                f"£{products_by_id[product_id]['price_pence'] / 100:.2f}"
            ),
            key="order_product",
        )

        selected_product = products_by_id[selected_id]

        st.caption(
            f"{selected_product['stock_quantity']} currently available"
        )

        with st.form("add_to_basket_form"):
            quantity = st.number_input(
                "Quantity to add",
                min_value=1,
                value=1,
                step=1,
            )

            add_clicked = st.form_submit_button("Add to basket")

        if add_clicked:
            existing_item = basket.get(selected_id)
            existing_quantity = (
                existing_item["quantity"] if existing_item else 0
            )

            requested_quantity = existing_quantity + int(quantity)

            if (
                existing_item
                and existing_item["price_pence"]
                != selected_product["price_pence"]
            ):
                st.error(
                    "This item's price changed. "
                    "Remove it from your basket and add it again."
                )

            elif requested_quantity > selected_product["stock_quantity"]:
                st.error(
                    "There is not enough stock for that quantity, "
                    "including any already in your basket."
                )

            else:
                basket[selected_id] = {
                    "name": selected_product["name"],
                    "price_pence": selected_product["price_pence"],
                    "quantity": requested_quantity,
                }

                basket_changed()

                st.session_state["basket_notice"] = (
                    f"Added {int(quantity)} × "
                    f"{selected_product['name']} to your basket."
                )

                st.rerun()

    else:
        st.info("No products are currently available to add.")

    st.subheader("Your basket")

    if not basket:
        st.info("Your basket is empty.")
        return

    for product_id, item in list(basket.items()):
        line_total = item["price_pence"] * item["quantity"]

        st.write(
            f"{item['name']} — "
            f"£{item['price_pence'] / 100:.2f} each — "
            f"Subtotal £{line_total / 100:.2f}"
        )

        with st.form(
            key=f"basket_item_{product_id}_{item['quantity']}"
        ):
            revised_quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=int(item["quantity"]),
                step=1,
            )

            update_clicked = st.form_submit_button("Update quantity")
            remove_clicked = st.form_submit_button("Remove item")

        if remove_clicked:
            del basket[product_id]
            basket_changed()
            st.rerun()

        if update_clicked:
            current_product = products_by_id.get(product_id)

            if (
                current_product is None
                or revised_quantity > current_product["stock_quantity"]
            ):
                st.error(
                    "That quantity is unavailable. "
                    "Choose a lower quantity or remove the item."
                )

            else:
                basket[product_id]["quantity"] = int(revised_quantity)
                basket_changed()
                st.rerun()

    total = sum(
        item["price_pence"] * item["quantity"]
        for item in basket.values()
    )

    st.subheader(f"Total: £{total / 100:.2f}")

    if st.button("Empty basket", key="empty_basket"):
        st.session_state["basket"] = {}
        basket_changed()
        st.rerun()

    st.info(
        "Review your basket, then click Place order to confirm your order. "
    )

    if st.button(
        "Place Order",
        type="primary",
        key="place_order",
    ):
        try:
            confirmation = place_order(
                basket,
                st.session_state["checkout_key"],
            )

        except ValueError as error:
            st.error(str(error))

        except sqlite3.Error:
            st.error(
                "The order could not be saved. "
                "Your basket has been kept. Please try again."
            )

        else:
            st.session_state["order_confirmation"] = confirmation
            st.session_state["basket"] = {}
            st.session_state["checkout_key"] = str(uuid4())
            st.rerun()