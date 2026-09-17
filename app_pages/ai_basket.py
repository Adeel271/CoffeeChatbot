import streamlit as st

from database import get_products
from ordering import basket_changed


BASKET_TOOL = {
    "name": "add_to_basket",
    "description": (
        "Add products to the customer's basket only when they request it. "
        "Use exact product IDs from the menu. "
        "Include all requested items in one call. "
        "Quantities are additional quantities, not replacement totals. "
        "Ask for clarification if the products or quantities are ambiguous."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "product_id": {"type": "INTEGER"},
                        "quantity": {"type": "INTEGER"},
                    },
                    "required": ["product_id", "quantity"],
                },
            }
        },
        "required": ["items"],
    },
}

CLEAR_BASKET_TOOL = {
    "name": "clear_basket",
    "description": (
        "Empty the customer's entire basket only when they explicitly "
        "ask to clear or empty it, or remove all items. "
        "Do not use this to remove a single product."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
}


def apply_basket_calls(calls):
    clear_calls = [
        call for call in calls
        if call.name == "clear_basket"
    ]

    if clear_calls:
        # Avoid partially carrying out mixed add-and-clear requests.
        if len(calls) != 1:
            return (
                "Please ask me to empty the basket first, "
                "then tell me which items to add."
            )

        if not st.session_state.get("basket"):
            return "Your basket is already empty."

        st.session_state["basket"] = {}
        basket_changed()

        return "Your basket has been emptied. No order was placed."

    requested = {}

    # Validate every requested action before changing anything.
    for call in calls:
        if call.name != "add_to_basket":
            return "Nothing was added: that basket action is not supported."

        items = (call.args or {}).get("items")

        if not isinstance(items, list) or not items:
            return "Nothing was added. Please specify the items and quantities."

        for item in items:
            if not isinstance(item, dict):
                return "Nothing was added. Please specify the items again."

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if (
                type(product_id) is not int
                or type(quantity) is not int
                or quantity < 1
            ):
                return (
                    "Nothing was added. Please use positive whole-number "
                    "quantities."
                )

            requested[product_id] = (
                requested.get(product_id, 0) + quantity
            )

    products = {
        product["product_id"]: dict(product)
        for product in get_products()
    }

    # Work on a copy so a failed check leaves the basket unchanged.
    updated_basket = {
        product_id: dict(item)
        for product_id, item in st.session_state.get("basket", {}).items()
    }

    added_lines = []

    for product_id, quantity in requested.items():
        product = products.get(product_id)

        if product is None:
            return "Nothing was added: an item could not be found on the menu."

        existing = updated_basket.get(product_id)
        existing_quantity = existing["quantity"] if existing else 0

        if (
            existing
            and existing["price_pence"] != product["price_pence"]
        ):
            return (
                f"Nothing was added: the price of {product['name']} changed. "
                "Please remove that item in Menu & Order and add it again."
            )

        new_quantity = existing_quantity + quantity

        if new_quantity > product["stock_quantity"]:
            return (
                f"Nothing was added: only {product['stock_quantity']} × "
                f"{product['name']} are currently available, and you already "
                f"have {existing_quantity} in your basket."
            )

        updated_basket[product_id] = {
            "name": product["name"],
            "price_pence": product["price_pence"],
            "quantity": new_quantity,
        }

        added_lines.append(
            f"- {quantity} × {product['name']} — "
            f"£{quantity * product['price_pence'] / 100:.2f}"
        )

    total = sum(
        item["price_pence"] * item["quantity"]
        for item in updated_basket.values()
    )

    receipt = (
        "Added to your basket:\n\n"
        + "\n".join(added_lines)
        + f"\n\nYour basket total is £{total / 100:.2f}."
        + "\n\nOpen Menu & Order to review your basket and place your order. "
        "Items are not reserved until checkout."
    )

    st.session_state["basket"] = updated_basket
    basket_changed()

    return receipt