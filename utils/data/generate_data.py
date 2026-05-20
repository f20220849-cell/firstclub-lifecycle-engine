import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

CATEGORIES = [
    "Fruits", "Vegetables", "Dairy", "Bakery", "Eggs",
    "Staples", "Packaged Snacks", "Beverages", "Cold Pressed Oils", "Nutrition"
]

PRODUCTS = {
    "Fruits": ["Alphonso Mangoes", "Organic Strawberries", "Dragon Fruit", "Seedless Grapes", "Kiwi"],
    "Vegetables": ["Cherry Tomatoes", "Baby Spinach", "Bell Peppers", "Zucchini", "Broccoli"],
    "Dairy": ["A2 Gir Cow Milk", "Akshaykalpa Curd", "Artisan Paneer", "Greek Yogurt", "Cultured Butter"],
    "Bakery": ["Sourdough Boule", "Multigrain Sandwich Loaf", "Almond Croissant", "Rye Bread", "Banana Walnut Loaf"],
    "Eggs": ["Free Range Brown Eggs", "Desi Eggs", "Omega-3 Eggs"],
    "Staples": ["Stone Ground Atta", "Organic Basmati Rice", "Cold Pressed Coconut Oil", "Toor Dal", "Red Poha"],
    "Packaged Snacks": ["Whole Truth Protein Bar", "Yoga Bar", "Millet Cookies", "Roasted Makhana", "Seed Mix"],
    "Beverages": ["Cold Brew Coffee", "Tulsi Green Tea", "Kokum Sherbet", "Tender Coconut Water", "Adaptogen Latte"],
    "Cold Pressed Oils": ["Cold Pressed Groundnut Oil", "Extra Virgin Olive Oil", "Sesame Oil", "Flaxseed Oil"],
    "Nutrition": ["Ashwagandha Powder", "Moringa Capsules", "Spirulina", "Collagen Peptides"]
}

def generate_customers(n=200):
    customers = []
    base_date = datetime(2025, 6, 1)
    today = datetime(2026, 5, 20)

    segments = {
        "habitual": 0.30,
        "forming": 0.20,
        "new": 0.15,
        "drifting": 0.20,
        "churned": 0.15,
    }

    segment_list = []
    for seg, pct in segments.items():
        segment_list.extend([seg] * int(n * pct))
    while len(segment_list) < n:
        segment_list.append("forming")
    random.shuffle(segment_list)

    orders = []
    customer_records = []

    for i in range(n):
        cid = f"FC{1000 + i}"
        seg = segment_list[i]
        name = f"Customer {cid}"

        # acquisition date
        acq_date = base_date + timedelta(days=random.randint(0, 180))

        # assign preferred categories (1 to 3)
        n_cats = random.randint(1, 3)
        preferred_cats = random.sample(CATEGORIES, n_cats)

        # number of orders and recency based on segment
        if seg == "habitual":
            n_orders = random.randint(8, 25)
            last_order_days_ago = random.randint(1, 7)
        elif seg == "forming":
            n_orders = random.randint(2, 4)
            last_order_days_ago = random.randint(3, 14)
        elif seg == "new":
            n_orders = 1
            last_order_days_ago = random.randint(0, 7)
        elif seg == "drifting":
            n_orders = random.randint(4, 10)
            last_order_days_ago = random.randint(12, 25)
        else:  # churned
            n_orders = random.randint(2, 6)
            last_order_days_ago = random.randint(30, 90)

        last_order_date = today - timedelta(days=last_order_days_ago)

        # generate order dates going backwards
        order_dates = sorted([
            last_order_date - timedelta(days=random.randint(0, max(1, (last_order_date - acq_date).days)))
            for _ in range(n_orders)
        ])
        order_dates[-1] = last_order_date

        # generate orders
        total_spend = 0
        order_ids = []
        for j, od in enumerate(order_dates):
            oid = f"ORD{i*100 + j}"
            order_ids.append(oid)

            # expand categories over time for habitual users
            cats_this_order = preferred_cats.copy()
            if seg == "habitual" and j > 3:
                extra = random.sample([c for c in CATEGORIES if c not in preferred_cats], k=min(2, len(CATEGORIES) - len(preferred_cats)))
                cats_this_order.extend(extra)

            n_items = random.randint(3, 8)
            order_cats = random.choices(cats_this_order, k=n_items)
            items = [random.choice(PRODUCTS[c]) for c in order_cats]
            order_value = round(random.uniform(600, 1800), 0)
            total_spend += order_value

            orders.append({
                "customer_id": cid,
                "order_id": oid,
                "order_date": od.strftime("%Y-%m-%d"),
                "order_value": order_value,
                "categories": ", ".join(set(order_cats)),
                "items": ", ".join(items[:4]),
                "segment_true": seg
            })

        customer_records.append({
            "customer_id": cid,
            "acquisition_date": acq_date.strftime("%Y-%m-%d"),
            "total_orders": n_orders,
            "total_spend": round(total_spend, 0),
            "preferred_categories": ", ".join(preferred_cats),
            "last_order_date": last_order_date.strftime("%Y-%m-%d"),
            "segment_true": seg
        })

    return pd.DataFrame(customer_records), pd.DataFrame(orders)


if __name__ == "__main__":
    customers, orders = generate_customers(200)
    customers.to_csv("customers.csv", index=False)
    orders.to_csv("orders.csv", index=False)
    print(f"Generated {len(customers)} customers and {len(orders)} orders")
