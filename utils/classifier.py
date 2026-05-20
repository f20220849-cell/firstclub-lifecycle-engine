import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TODAY = datetime(2026, 5, 20)

SEGMENT_CONFIG = {
    "New": {
        "color": "#4A9EFF",
        "bg": "#EBF4FF",
        "icon": "🌱",
        "description": "First order placed. The aha moment is everything right now.",
    },
    "Forming": {
        "color": "#F59E0B",
        "bg": "#FFFBEB",
        "icon": "🔄",
        "description": "2 to 4 orders in. Gift period ending. Habit not yet formed.",
    },
    "Habitual": {
        "color": "#10B981",
        "bg": "#ECFDF5",
        "icon": "⭐",
        "description": "Regular cadence. High LTV potential. Expand their basket.",
    },
    "Drifting": {
        "color": "#F97316",
        "bg": "#FFF7ED",
        "icon": "⚠️",
        "description": "Order frequency is dropping. Intervention window is open.",
    },
    "Churned": {
        "color": "#EF4444",
        "bg": "#FEF2F2",
        "icon": "❌",
        "description": "No order in 30+ days. Win-back is the only play.",
    },
}

INTERVENTION_PLAYBOOK = {
    "New": {
        "goal": "Get them to order 2",
        "timing": "48 hours after first delivery",
        "channel": "WhatsApp + Push",
        "offer_type": "No discount. Quality education.",
        "hypothesis": "If we surface the quality story behind what they already bought, they order again within 7 days.",
        "metric": "Order 2 conversion rate within D7",
        "target_lift": "30% of new customers place order 2 within 7 days",
    },
    "Forming": {
        "goal": "Lock in the habit before gift period ends",
        "timing": "Day of 3rd order delivery",
        "channel": "WhatsApp + Email",
        "offer_type": "Category discovery gift. Not a discount.",
        "hypothesis": "Introducing one new category before gift 3 expires increases 4th order rate by 25%.",
        "metric": "Order 4 rate within 14 days of order 3",
        "target_lift": "40% of forming customers place order 4 within 14 days",
    },
    "Habitual": {
        "goal": "Expand basket width by one new category",
        "timing": "Day after their typical order cycle",
        "channel": "In-app + Push",
        "offer_type": "Free sample of top-rated item in an untried category.",
        "hypothesis": "Habitual customers who try a new category in month 2 have 2x LTV vs those who stay single-category.",
        "metric": "New category trial rate and repeat in that category within 30 days",
        "target_lift": "35% of habitual customers try a new category within 30 days",
    },
    "Drifting": {
        "goal": "Re-establish order cadence before full churn",
        "timing": "Day 12 of inactivity",
        "channel": "WhatsApp + Push + Email",
        "offer_type": "Replenishment reminder tied to what they actually buy.",
        "hypothesis": "Personalised replenishment nudge at day 12 re-engages 30% of drifting customers before they hit day 30.",
        "metric": "Re-order rate within 7 days of intervention",
        "target_lift": "30% of drifting customers place an order within 7 days",
    },
    "Churned": {
        "goal": "Win back with a quality-led reason to return",
        "timing": "Day 35 of inactivity",
        "channel": "WhatsApp + Email",
        "offer_type": "New product drop in their favourite category. No discount.",
        "hypothesis": "Quality-led win-back (new arrival vs discount) has lower CAC and higher 90-day retention for FirstClub's customer profile.",
        "metric": "Re-activation rate and 30-day retention post win-back",
        "target_lift": "15% of churned customers place an order within 14 days",
    },
}


def classify_customer(row):
    today = TODAY
    last_order = pd.to_datetime(row["last_order_date"])
    days_since = (today - last_order).days
    total_orders = row["total_orders"]

    if total_orders == 1:
        return "New"
    elif total_orders <= 4 and days_since <= 14:
        return "Forming"
    elif total_orders >= 5 and days_since <= 10:
        return "Habitual"
    elif days_since >= 30:
        return "Churned"
    elif days_since >= 11:
        return "Drifting"
    elif total_orders >= 4:
        return "Habitual"
    else:
        return "Forming"


def compute_metrics(customers_df, orders_df):
    customers_df = customers_df.copy()
    customers_df["segment"] = customers_df.apply(classify_customer, axis=1)

    customers_df["last_order_date"] = pd.to_datetime(customers_df["last_order_date"])
    customers_df["acquisition_date"] = pd.to_datetime(customers_df["acquisition_date"])
    customers_df["days_since_last_order"] = (TODAY - customers_df["last_order_date"]).dt.days
    customers_df["days_as_customer"] = (TODAY - customers_df["acquisition_date"]).dt.days
    customers_df["avg_order_value"] = (customers_df["total_spend"] / customers_df["total_orders"]).round(0)

    segment_summary = customers_df.groupby("segment").agg(
        count=("customer_id", "count"),
        avg_orders=("total_orders", "mean"),
        avg_spend=("total_spend", "mean"),
        avg_aov=("avg_order_value", "mean"),
    ).round(1).reset_index()

    return customers_df, segment_summary


def get_untried_categories(customer_row, all_categories):
    tried = set(c.strip() for c in str(customer_row.get("preferred_categories", "")).split(","))
    untried = [c for c in all_categories if c not in tried]
    return untried[:2] if untried else ["Nutrition", "Cold Pressed Oils"]


def compute_retention_curve(orders_df):
    orders_df = orders_df.copy()
    orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])

    order_num = orders_df.sort_values("order_date").groupby("customer_id").cumcount() + 1
    orders_df["order_num"] = order_num

    total_customers = orders_df["customer_id"].nunique()
    retention = {}
    for n in range(1, 9):
        count = orders_df[orders_df["order_num"] >= n]["customer_id"].nunique()
        retention[f"Order {n}"] = round((count / total_customers) * 100, 1)

    return retention


def compute_category_penetration(customers_df):
    all_cats = {}
    for cats in customers_df["preferred_categories"].dropna():
        for c in cats.split(","):
            c = c.strip()
            if c:
                all_cats[c] = all_cats.get(c, 0) + 1
    total = len(customers_df)
    return {k: round(v / total * 100, 1) for k, v in sorted(all_cats.items(), key=lambda x: -x[1])}
