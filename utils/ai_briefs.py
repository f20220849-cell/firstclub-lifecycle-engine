import random

QUALITY_HOOKS = {
    "Fruits": "Our Alphonso mangoes are sourced directly from Ratnagiri and arrive within 48 hours of harvest.",
    "Vegetables": "Every vegetable on FirstClub is checked for pesticide residue before it reaches your doorstep.",
    "Dairy": "Our A2 Gir Cow milk is blind-tested against 20 brands. It came first. That is why it is here.",
    "Bakery": "Our sourdough is baked fresh every morning with no preservatives. It is gone by afternoon.",
    "Eggs": "Our free-range eggs come from hens that are never given growth hormones or antibiotics.",
    "Staples": "Our stone-ground atta retains the bran and germ that commercial brands strip away.",
    "Packaged Snacks": "Every snack on FirstClub passes our 200-ingredient banned list. Most popular brands do not.",
    "Beverages": "Our cold brew is made with single-origin beans and brewed for 18 hours. No shortcuts.",
    "Cold Pressed Oils": "Our groundnut oil is cold-pressed at under 40 degrees to retain nutrients destroyed by heat refining.",
    "Nutrition": "Our supplements are third-party tested for heavy metals and label accuracy before listing.",
}

WHATSAPP_TEMPLATES = {
    "New": [
        "Hi, your first order just gave us a lot to work with. The {category} you picked is one of our most reordered items. {quality_hook} Whenever you are ready for round two, we are here.",
        "Your first order is in. Here is something worth knowing about what you just got: {quality_hook} Most of our customers reorder within the week. We think you will too.",
        "Welcome to FirstClub. The {category} in your last order went through our blind test before making it to the platform. {quality_hook} Your next order is a tap away.",
    ],
    "Forming": [
        "You have tried us {orders} times now. Before your gift wraps up, there is one category most of our regulars wish they had tried earlier: {category}. {quality_hook}",
        "Your third order is also your last gift. We wanted to make sure you knew about {category} before that changes. {quality_hook} Worth exploring.",
        "You are three orders in. The customers who stick with us longest almost always branched into {category} around this point. {quality_hook}",
    ],
    "Habitual": [
        "You have been ordering {category} consistently. Our {new_category} section just got restocked with something that pairs well with what you already buy. {quality_hook}",
        "Quick note: we added something to {new_category} that our {category} regulars have been asking about. {quality_hook} Thought you should know first.",
        "You know our {category} well. Here is something from {new_category} that is made with the same sourcing standard. {quality_hook}",
    ],
    "Drifting": [
        "It has been {days} days since your last order. Your usual {category} is still here, and so is the quality standard that got you here in the first place. {quality_hook}",
        "Your {category} might be running low. {quality_hook} Nothing has changed on our end. Whenever you are ready.",
        "We noticed a gap since your last {category} order. {quality_hook} Your cart is saved. Pick up where you left off.",
    ],
    "Churned": [
        "It has been a while. We have added new items to {category} since your last order that were not there before. {quality_hook} Worth a look if you are curious.",
        "Something new landed in {category} that we think matches what you were buying earlier. {quality_hook} No pressure, just thought it was worth a mention.",
        "We expanded our {category} range recently. {quality_hook} If that is what brought you here originally, there is more of it now.",
    ],
}

PUSH_TEMPLATES = {
    "New": [
        "Your {category} order. The quality story behind it.",
        "Order 2 is better than order 1. Here is why.",
        "What makes your {category} different from every other platform.",
    ],
    "Forming": [
        "One category you have not tried yet. It is worth it.",
        "Your gift period ends soon. Explore {new_category} before it does.",
        "3 orders in. Time to go a little wider.",
    ],
    "Habitual": [
        "New in {new_category}. Made for {category} regulars.",
        "Something new that matches your taste in {category}.",
        "Your next favourite might be in {new_category}.",
    ],
    "Drifting": [
        "Your {category} is probably running low.",
        "{days} days since your last order. Your cart is saved.",
        "Still here. Still the same quality. Your {category} awaits.",
    ],
    "Churned": [
        "New {category} arrivals since your last order.",
        "Something changed in {category}. Take a look.",
        "We added to {category}. Thought you should know.",
    ],
}

SUBJECT_LINES = {
    "New": [
        "What just arrived in your kitchen",
        "Your first order. Here is what went into it.",
        "The story behind your {category}",
    ],
    "Forming": [
        "One more category before your gift ends",
        "Three orders in. One more thing to try.",
        "Before your gift wraps up",
    ],
    "Habitual": [
        "New in {new_category}. Made for you.",
        "Something that pairs with your {category}",
        "Your next FirstClub favourite",
    ],
    "Drifting": [
        "Your {category} is probably running low",
        "Still here. Still quality.",
        "Nothing has changed. Everything is still here.",
    ],
    "Churned": [
        "What is new in {category} since you left",
        "Something worth coming back for",
        "New arrivals in {category}",
    ],
}

RATIONALE_TEMPLATES = {
    "New": "This customer placed their first order {days} days ago and has not reordered yet. The window for habit formation is open and the quality story is the strongest lever at this stage, not a discount. Leading with what makes the product different reinforces the reason they chose FirstClub in the first place.",
    "Forming": "This customer has placed {orders} orders and is still in the gift period. The highest-risk moment is when the gift programme ends and there is no engineered reason to return. Introducing a new category now builds a wider habit before that cliff arrives.",
    "Habitual": "This customer orders {category} regularly with an average spend of Rs {aov}. The next lever is basket width. Customers who try a second category by order 6 have significantly higher 90-day LTV. A quality-led introduction to {new_category} is the right move.",
    "Drifting": "This customer has not ordered in {days} days, which puts them at the edge of the churn window. A replenishment reminder tied to their actual purchase history performs better than a generic win-back at this stage because it feels contextual, not automated.",
    "Churned": "This customer has been inactive for {days} days. Discount-led win-back attracts low-quality reactivations with poor 30-day retention. A quality signal around a new arrival in their preferred category targets the original motivation for joining FirstClub.",
}

ALL_CATEGORIES = list(QUALITY_HOOKS.keys())


def get_primary_category(preferred_categories_str):
    cats = [c.strip() for c in str(preferred_categories_str).split(",") if c.strip()]
    for c in cats:
        if c in QUALITY_HOOKS:
            return c
    return random.choice(ALL_CATEGORIES)


def get_new_category(preferred_categories_str):
    tried = set(c.strip() for c in str(preferred_categories_str).split(","))
    untried = [c for c in ALL_CATEGORIES if c not in tried]
    return untried[0] if untried else random.choice(ALL_CATEGORIES)


def fill_template(template, context):
    try:
        return template.format(**context)
    except KeyError:
        return template


def generate_campaign_brief(segment, customer_data, intervention_config):
    preferred_cats = customer_data.get("preferred_categories", "Dairy")
    total_orders = int(customer_data.get("total_orders", 3))
    avg_aov = int(customer_data.get("avg_order_value", 950))
    days_since = int(customer_data.get("days_since_last_order", 5))

    category = get_primary_category(preferred_cats)
    new_category = get_new_category(preferred_cats)
    quality_hook = QUALITY_HOOKS.get(category, QUALITY_HOOKS["Dairy"])

    context = {
        "category": category,
        "new_category": new_category,
        "quality_hook": quality_hook,
        "orders": total_orders,
        "aov": f"{avg_aov:,}",
        "days": days_since,
    }

    whatsapp_raw = random.choice(WHATSAPP_TEMPLATES.get(segment, WHATSAPP_TEMPLATES["New"]))
    push_raw = random.choice(PUSH_TEMPLATES.get(segment, PUSH_TEMPLATES["New"]))
    subject_raw = random.choice(SUBJECT_LINES.get(segment, SUBJECT_LINES["New"]))
    rationale_raw = RATIONALE_TEMPLATES.get(segment, RATIONALE_TEMPLATES["New"])

    return {
        "subject_line": fill_template(subject_raw, context),
        "whatsapp_message": fill_template(whatsapp_raw, context),
        "push_notification": fill_template(push_raw, context),
        "quality_hook": quality_hook,
        "campaign_rationale": fill_template(rationale_raw, context),
    }


def generate_segment_insight(segment, segment_data, retention_curve):
    count = segment_data.get("count", 0)
    avg_orders = round(segment_data.get("avg_orders", 0), 1)
    avg_spend = int(segment_data.get("avg_spend", 0))

    insights = {
        "New": f"There are {count} customers who placed exactly one order and have not returned yet. This is the highest-leverage cohort in the business right now. Getting order 2 within 7 days triples the probability of long-term retention.",
        "Forming": f"{count} customers are in the gift period with an average of {avg_orders} orders each. The cliff after gift 3 is the single most predictable churn event in the lifecycle. Introducing a new category before order 4 is the most effective way to extend habit formation.",
        "Habitual": f"These {count} customers are placing {avg_orders} orders on average with a cumulative spend of Rs {avg_spend:,}. They are the core of the business. The next move is basket width, not frequency. One new category trial by order 6 correlates with 2x LTV.",
        "Drifting": f"{count} customers are showing declining frequency and are approaching the 30-day churn window. Intervention at day 12 recovers significantly more customers than waiting until day 25. Every day of delay reduces win-back probability.",
        "Churned": f"{count} customers have been inactive for 30 or more days. Discount-led win-back for this segment produces low-quality reactivations with poor retention. A quality-led approach targeting their original category preference performs better on 90-day LTV.",
    }

    return insights.get(segment, f"{count} customers in this segment with average spend of Rs {avg_spend:,}.")
