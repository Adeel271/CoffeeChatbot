# One Stop Coffee

**Author:** Sikander Adeel Cheema  
**Student ID:** **14207662**

One Stop Coffee is a Python and Streamlit coffee-shop application for browsing products, building a basket, placing orders, and managing inventory. Product information and completed orders are stored in a local SQLite database.

## Features

- Browse product names, categories, descriptions, prices, and availability.
- Filter the menu by category, maximum price, and stock availability.
- Add products to a basket, update quantities, remove individual items, or empty the basket.
- Keep basket contents when moving between pages within the same session.
- View item subtotals and the overall basket total in pounds sterling.
- Validate current prices and stock before completing an order.
- Save completed orders and reduce stock quantities together in a database transaction.
- Display an order number and total after successful checkout.
- Restrict inventory editing to users with the administrator password.
- Update existing product prices and stock quantities through the inventory page.

Checkout uses simulated payment. No money is charged.

## Technology

| Component | Purpose |
| --- | --- |
| Python | Application logic |
| Streamlit | Pages, navigation, forms, and session state |
| SQLite | Product, inventory, and order storage |
| CSV | Initial product data |
| HTML and CSS | Menu presentation and page styling |

## Installation

Python, pip, and Git are required for the following steps. Git is unnecessary when using an extracted copy of the project.

### 1. Get the project

```bash
git clone https://github.com/Adeel271/CoffeeChatbot.git
cd CoffeeChatbot
```

Alternatively, extract the project archive and open a terminal in the folder containing `app.py`.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure inventory access

Create or update `.streamlit/secrets.toml` and set `INVENTORY_PASSWORD` to the administrator password as a quoted TOML string. This file is excluded from version control by the project's `.gitignore`.

### 5. Initialise the product database

```bash
python database.py
```

This creates the products table and imports records from `menu.csv`. Existing product IDs are preserved, so running the command again does not reset their saved prices or stock quantities.

### 6. Start the application

```bash
python -m streamlit run app.py
```

Open the local address displayed in the terminal. Order tables are created when the ordering interface loads.

## Using the Application

### Browse and order

1. Open **Menu & Order**.
2. Set the category, price, and availability filters.
3. Select a product under **Place an order**, enter a quantity, and choose **Add to basket**.
4. Review the basket and update or remove items as needed.
5. Select **Place Order** to complete checkout.

The product selector includes all available products independently of the menu filters. Adding an item to the basket does not reserve stock. Checkout checks availability and prices again before saving the order. A successful order clears the basket and displays confirmation.

### Manage inventory

1. Open **Manage Inventory** and enter the administrator password.
2. Expand the inventory editor.
3. Select a product and choose **Load product**.
4. Enter the revised price and stock quantity.
5. Select **Save changes**.
6. Select **Log out** when finished.

## Main Project Files

| Path | Purpose |
| --- | --- |
| `app.py` | Application entry point, navigation, and shared state |
| `app_pages/` | Application pages |
| `database.py` | Product database creation, retrieval, and updates |
| `ordering.py` | Basket interface and checkout controls |
| `order_database.py` | Order storage and checkout validation |
| `menu.csv` | Initial product records |
| `requirements.txt` | Dependency versions |
| `.streamlit/config.toml` | Streamlit configuration |
| `assets/` | Page banners and background images |
| `test_evidence/` | Screenshots documenting application checks |

## Data Storage

The application stores data in `coffee_shop.db`:

- **products:** product details, prices in pence, and stock quantities.
- **orders:** order identifiers, checkout keys, timestamps, totals, and payment status.
- **order_items:** purchased products, quantities, and unit prices recorded at checkout.

Basket contents are held in session state. Completed orders and inventory changes persist in the database. Unique checkout keys prevent the same checkout request from creating duplicate orders.

## Test Evidence

The supplied `test_evidence/` folder includes screenshots covering menu filtering, basket changes, checkout confirmation, saved orders, stock persistence, price updates, and inventory login checks.
