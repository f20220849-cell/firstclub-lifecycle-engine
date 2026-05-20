# FirstClub Lifecycle Engine

A growth intelligence tool built for FirstClub's growth team. It classifies every customer into a lifecycle stage in real time, prescribes the exact intervention to run for each segment, and generates personalised campaign briefs using AI.

Built as a portfolio project for the FirstClub PS-II Growth Internship application.

---

## What It Does

**Overview Dashboard**
- Full lifecycle breakdown across five segments: New, Forming, Habitual, Drifting, Churned
- Retention curve by order number with cliff detection
- Category penetration heatmap
- At-risk customer count in real time

**Segment Explorer**
- Deep dive into any lifecycle segment
- AOV distribution, order frequency histogram
- Full customer list with sortable metrics

**Intervention Planner**
- For each segment: goal, channel, timing, offer type, hypothesis, and success metric
- Revenue impact estimator with adjustable lift assumptions
- Based on FirstClub's brand positioning (quality-led, not discount-led)

**Campaign Brief Generator**
- Select any customer
- AI generates a personalised WhatsApp message, push notification, subject line, and quality hook
- Briefs are tailored to the customer's actual purchase history and lifecycle stage
- Powered by Claude (Anthropic)

---

## The Problem It Solves

FirstClub has a 60% repeat purchase rate and an AOV of Rs 1,050, nearly double the industry average. But without a systematic lifecycle engine, the growth team has no early warning system for churn and no playbook for what intervention to run at each stage.

This tool gives the growth team exactly that: a daily operating instrument to identify who is drifting, what to say to them, and how to measure if it worked.

---

## Setup

```bash
git clone https://github.com/yourusername/firstclub-lifecycle-engine
cd firstclub-lifecycle-engine
pip install -r requirements.txt
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

Run the app:

```bash
streamlit run app.py
```

The app ships with 200 synthetic but realistic customers and 1500+ orders. You can also upload your own CSV files matching the schema below.

---

## CSV Schema

**customers.csv**

| Column | Type | Description |
|--------|------|-------------|
| customer_id | string | Unique customer ID |
| acquisition_date | YYYY-MM-DD | First order date |
| total_orders | int | Total orders placed |
| total_spend | float | Cumulative spend in Rs |
| preferred_categories | string | Comma-separated category names |
| last_order_date | YYYY-MM-DD | Most recent order date |

**orders.csv**

| Column | Type | Description |
|--------|------|-------------|
| customer_id | string | Links to customers.csv |
| order_id | string | Unique order ID |
| order_date | YYYY-MM-DD | Date of order |
| order_value | float | Order value in Rs |
| categories | string | Comma-separated categories in this order |
| items | string | Comma-separated item names |

---

## Lifecycle Segments

| Segment | Definition | Priority |
|---------|------------|----------|
| New | 1 order only | High: get order 2 within 7 days |
| Forming | 2 to 4 orders, ordered within 14 days | High: lock in habit before gift period ends |
| Habitual | 5+ orders, ordered within 10 days | Medium: expand basket width |
| Drifting | Any orders, 11 to 29 days since last order | Critical: re-engage before day 30 |
| Churned | Any orders, 30+ days since last order | Win-back: quality-led re-activation |

---

## Tech Stack

- Streamlit for the frontend
- Pandas and NumPy for data processing
- Plotly for charts
- Anthropic Claude API for campaign brief generation
- Python 3.10+

---

## About

Built by Aditya for the FirstClub PS-II Growth Internship (First Semester 2026-27). The tool demonstrates end-to-end growth thinking: problem framing, data analysis, intervention design, and measurement planning.
