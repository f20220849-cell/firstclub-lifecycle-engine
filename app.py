import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.classifier import (
    classify_customer, compute_metrics, compute_retention_curve,
    compute_category_penetration, get_untried_categories,
    SEGMENT_CONFIG, INTERVENTION_PLAYBOOK, TODAY
)
from utils.ai_briefs import generate_campaign_brief, generate_segment_insight

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="FirstClub Lifecycle Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main {
    background-color: #FAFAF7;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
    color: #1A1A1A;
}

.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #1A1A1A;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}

.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #6B7280;
    font-weight: 400;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.metric-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #1A1A1A;
    line-height: 1;
}

.metric-label {
    font-size: 0.8rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

.segment-card {
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #E5E7EB;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
}

.segment-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}

.segment-icon {
    font-size: 1.4rem;
    margin-right: 0.5rem;
}

.segment-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    font-weight: 400;
}

.segment-count {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: #1A1A1A;
}

.intervention-card {
    background: white;
    border-radius: 14px;
    padding: 1.6rem;
    border: 1px solid #E5E7EB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}

.intervention-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6B7280;
    margin-bottom: 0.3rem;
}

.intervention-value {
    font-size: 0.95rem;
    color: #1A1A1A;
    line-height: 1.5;
}

.brief-card {
    background: #F9FFF9;
    border-radius: 14px;
    padding: 1.6rem;
    border: 1px solid #D1FAE5;
    margin-bottom: 1rem;
}

.brief-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #059669;
    margin-bottom: 0.4rem;
}

.brief-value {
    font-size: 0.95rem;
    color: #1A1A1A;
    line-height: 1.6;
}

.tag {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-bottom: 0.3rem;
}

.stButton > button {
    background: #1A1A1A;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #374151;
    transform: translateY(-1px);
}

.divider {
    border: none;
    border-top: 1px solid #E5E7EB;
    margin: 1.5rem 0;
}

.sidebar-section {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9CA3AF;
    margin-bottom: 0.5rem;
    margin-top: 1rem;
}

.customer-row {
    background: white;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    border: 1px solid #E5E7EB;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
}

.insight-box {
    background: #FFFBEB;
    border-left: 3px solid #F59E0B;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.92rem;
    color: #1A1A1A;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ---- LOAD DATA ----
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    customers = pd.read_csv(os.path.join(base, "customers.csv"))
    orders = pd.read_csv(os.path.join(base, "orders.csv"))
    return customers, orders


def load_uploaded_data(customers_file, orders_file):
    customers = pd.read_csv(customers_file)
    orders = pd.read_csv(orders_file)
    return customers, orders


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='font-family: DM Serif Display, serif; font-size: 1.4rem; color: #1A1A1A;'>FirstClub</div>
        <div style='font-size: 0.75rem; color: #6B7280; letter-spacing: 0.05em; text-transform: uppercase;'>Lifecycle Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>Data Source</div>", unsafe_allow_html=True)
    data_source = st.radio(
        "",
        ["Use sample data", "Upload your own CSV"],
        label_visibility="collapsed"
    )

    if data_source == "Upload your own CSV":
        st.markdown("<div style='font-size: 0.82rem; color: #6B7280; margin-bottom: 0.5rem;'>Upload customers.csv</div>", unsafe_allow_html=True)
        customers_file = st.file_uploader("", type="csv", key="customers", label_visibility="collapsed")
        st.markdown("<div style='font-size: 0.82rem; color: #6B7280; margin-bottom: 0.5rem;'>Upload orders.csv</div>", unsafe_allow_html=True)
        orders_file = st.file_uploader("", type="csv", key="orders", label_visibility="collapsed")

        if customers_file and orders_file:
            raw_customers, raw_orders = load_uploaded_data(customers_file, orders_file)
        else:
            st.info("Upload both files to continue.")
            raw_customers, raw_orders = load_data()
    else:
        raw_customers, raw_orders = load_data()

    st.markdown("<div class='sidebar-section'>Navigation</div>", unsafe_allow_html=True)
    page = st.radio(
        "",
        ["Overview", "Segment Explorer", "Intervention Planner", "Campaign Brief Generator"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 0.75rem; color: #9CA3AF; line-height: 1.6;'>
        Built for FirstClub's Growth Team<br>
        Analyzes customer lifecycle in real time<br>
        Powered by Claude AI for briefs
    </div>
    """, unsafe_allow_html=True)


# ---- COMPUTE ----
customers_df, segment_summary = compute_metrics(raw_customers, raw_orders)
retention_curve = compute_retention_curve(raw_orders)
cat_penetration = compute_category_penetration(customers_df)
segment_counts = customers_df["segment"].value_counts().to_dict()
total_customers = len(customers_df)
total_revenue = customers_df["total_spend"].sum()
avg_aov = customers_df["avg_order_value"].mean()
repeat_rate = round((customers_df[customers_df["total_orders"] > 1].shape[0] / total_customers) * 100, 1)


# ==============================
# PAGE: OVERVIEW
# ==============================
if page == "Overview":
    st.markdown("""
    <div class='hero-title'>Customer Lifecycle Dashboard</div>
    <div class='hero-sub'>Real-time view of where every customer stands and what to do next.</div>
    """, unsafe_allow_html=True)

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-number'>{total_customers}</div>
            <div class='metric-label'>Total Customers</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-number'>{repeat_rate}%</div>
            <div class='metric-label'>Repeat Purchase Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-number'>Rs {int(avg_aov):,}</div>
            <div class='metric-label'>Avg Order Value</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        at_risk = segment_counts.get("Drifting", 0) + segment_counts.get("Churned", 0)
        at_risk_pct = round(at_risk / total_customers * 100, 1)
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-number' style='color: #EF4444;'>{at_risk}</div>
            <div class='metric-label'>At Risk ({at_risk_pct}% of base)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown("### Lifecycle Breakdown")

        for seg, config in SEGMENT_CONFIG.items():
            count = segment_counts.get(seg, 0)
            pct = round(count / total_customers * 100, 1)
            st.markdown(f"""
            <div class='segment-card' style='background: {config["bg"]}; border-color: {config["color"]}22;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span class='segment-icon'>{config["icon"]}</span>
                        <span class='segment-name' style='color: {config["color"]};'>{seg}</span>
                        <div style='font-size: 0.82rem; color: #6B7280; margin-top: 0.3rem; padding-left: 2rem;'>
                            {config["description"]}
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div class='segment-count'>{count}</div>
                        <div style='font-size: 0.75rem; color: #9CA3AF;'>{pct}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### Retention by Order Number")

        orders_list = list(retention_curve.keys())
        values = list(retention_curve.values())

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=orders_list,
            y=values,
            mode='lines+markers',
            line=dict(color='#1A1A1A', width=2.5),
            marker=dict(size=8, color='#1A1A1A', symbol='circle'),
            fill='tozeroy',
            fillcolor='rgba(26,26,26,0.06)',
            name='Retention'
        ))

        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(family='DM Sans', size=12, color='#6B7280')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#F3F4F6',
                title='% of Customers',
                ticksuffix='%',
                tickfont=dict(family='DM Sans', size=12, color='#6B7280'),
                range=[0, 105]
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # cliff annotation
        drop_order2 = retention_curve.get("Order 1", 100) - retention_curve.get("Order 2", 0)
        st.markdown(f"""
        <div class='insight-box'>
            <strong>{drop_order2:.1f}% of customers do not place a second order.</strong> This is the most critical intervention point. 
            Getting order 2 within 7 days of order 1 is the single highest-ROI action for the growth team right now.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Category Penetration")
        cats = list(cat_penetration.keys())[:6]
        vals = [cat_penetration[c] for c in cats]

        fig2 = go.Figure(go.Bar(
            x=vals,
            y=cats,
            orientation='h',
            marker=dict(
                color=vals,
                colorscale=[[0, '#E5E7EB'], [1, '#1A1A1A']],
                showscale=False
            ),
            text=[f"{v}%" for v in vals],
            textposition='outside',
            textfont=dict(family='DM Sans', size=11)
        ))

        fig2.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=40, t=10, b=10),
            height=220,
            xaxis=dict(showgrid=False, showticklabels=False, title=None),
            yaxis=dict(showgrid=False, title=None, tickfont=dict(family='DM Sans', size=12)),
        )
        st.plotly_chart(fig2, use_container_width=True)


# ==============================
# PAGE: SEGMENT EXPLORER
# ==============================
elif page == "Segment Explorer":
    st.markdown("""
    <div class='hero-title'>Segment Explorer</div>
    <div class='hero-sub'>Deep dive into each lifecycle segment. Understand who they are and what they need.</div>
    """, unsafe_allow_html=True)

    selected_seg = st.selectbox(
        "Select a segment",
        list(SEGMENT_CONFIG.keys()),
        format_func=lambda x: f"{SEGMENT_CONFIG[x]['icon']} {x}"
    )

    config = SEGMENT_CONFIG[selected_seg]
    seg_df = customers_df[customers_df["segment"] == selected_seg].copy()
    seg_count = len(seg_df)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Customers", str(seg_count), ""),
        ("Avg Orders", str(round(seg_df["total_orders"].mean(), 1)), "orders"),
        ("Avg Total Spend", f"Rs {int(seg_df['total_spend'].mean()):,}", ""),
        ("Avg Days Since Order", str(int(seg_df["days_since_last_order"].mean())), "days"),
    ]

    for col, (label, val, suffix) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class='metric-card' style='border-top: 3px solid {config["color"]};'>
                <div class='metric-number'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.markdown("### Customer List")
        display_cols = ["customer_id", "total_orders", "avg_order_value", "days_since_last_order", "preferred_categories"]
        display_df = seg_df[display_cols].copy()
        display_df.columns = ["Customer ID", "Orders", "Avg Order Value", "Days Since Last Order", "Top Categories"]
        display_df["Avg Order Value"] = display_df["Avg Order Value"].apply(lambda x: f"Rs {int(x):,}")
        st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)

    with col_r:
        st.markdown("### Segment Distribution by AOV")

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=seg_df["avg_order_value"],
            nbinsx=12,
            marker=dict(color=config["color"], opacity=0.8),
            name="AOV Distribution"
        ))

        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            height=220,
            xaxis=dict(
                title="Average Order Value (Rs)",
                showgrid=False,
                tickfont=dict(family='DM Sans', size=11)
            ),
            yaxis=dict(
                title="Customers",
                showgrid=True,
                gridcolor='#F3F4F6',
                tickfont=dict(family='DM Sans', size=11)
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Order Frequency Distribution")
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=seg_df["total_orders"],
            nbinsx=10,
            marker=dict(color='#1A1A1A', opacity=0.7),
        ))
        fig2.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            height=180,
            xaxis=dict(title="Total Orders", showgrid=False, tickfont=dict(family='DM Sans', size=11)),
            yaxis=dict(title="Customers", showgrid=True, gridcolor='#F3F4F6', tickfont=dict(family='DM Sans', size=11)),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)


# ==============================
# PAGE: INTERVENTION PLANNER
# ==============================
elif page == "Intervention Planner":
    st.markdown("""
    <div class='hero-title'>Intervention Planner</div>
    <div class='hero-sub'>For each segment, here is exactly what to run, when, why, and how to measure it.</div>
    """, unsafe_allow_html=True)

    for seg, config in SEGMENT_CONFIG.items():
        playbook = INTERVENTION_PLAYBOOK[seg]
        count = segment_counts.get(seg, 0)

        with st.expander(f"{config['icon']} {seg}   —   {count} customers", expanded=(seg == "Drifting")):
            st.markdown(f"""
            <div style='color: {config["color"]}; font-size: 0.82rem; font-weight: 600; 
                        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem;'>
                {config["description"]}
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class='intervention-card'>
                    <div class='intervention-label'>Goal</div>
                    <div class='intervention-value'>{playbook["goal"]}</div>
                </div>
                <div class='intervention-card'>
                    <div class='intervention-label'>Channel</div>
                    <div class='intervention-value'>{playbook["channel"]}</div>
                </div>
                <div class='intervention-card'>
                    <div class='intervention-label'>Timing</div>
                    <div class='intervention-value'>{playbook["timing"]}</div>
                </div>
                <div class='intervention-card'>
                    <div class='intervention-label'>Offer Type</div>
                    <div class='intervention-value'>{playbook["offer_type"]}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class='intervention-card' style='border-left: 3px solid {config["color"]};'>
                    <div class='intervention-label'>Hypothesis</div>
                    <div class='intervention-value'>{playbook["hypothesis"]}</div>
                </div>
                <div class='intervention-card'>
                    <div class='intervention-label'>Primary Metric</div>
                    <div class='intervention-value'>{playbook["metric"]}</div>
                </div>
                <div class='intervention-card' style='background: {config["bg"]};'>
                    <div class='intervention-label'>Target Lift</div>
                    <div class='intervention-value' style='font-weight: 600; color: {config["color"]};'>
                        {playbook["target_lift"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Revenue impact estimator
    st.markdown("---")
    st.markdown("### Revenue Impact Estimator")
    st.markdown("<div style='font-size: 0.9rem; color: #6B7280; margin-bottom: 1rem;'>Adjust the expected lift for each intervention to see the projected revenue impact.</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        forming_lift = st.slider("Forming: Order 4 conversion lift", 0, 50, 25, 5, format="%d%%")
    with col2:
        drifting_lift = st.slider("Drifting: Re-order rate lift", 0, 50, 30, 5, format="%d%%")
    with col3:
        churned_lift = st.slider("Churned: Win-back rate", 0, 30, 15, 5, format="%d%%")

    forming_count = segment_counts.get("Forming", 0)
    drifting_count = segment_counts.get("Drifting", 0)
    churned_count = segment_counts.get("Churned", 0)

    forming_rev = forming_count * (forming_lift / 100) * int(avg_aov)
    drifting_rev = drifting_count * (drifting_lift / 100) * int(avg_aov)
    churned_rev = churned_count * (churned_lift / 100) * int(avg_aov) * 2
    total_impact = forming_rev + drifting_rev + churned_rev

    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, val in zip(
        [col_a, col_b, col_c, col_d],
        ["Forming Impact", "Drifting Impact", "Churned Impact", "Total Projected Impact"],
        [forming_rev, drifting_rev, churned_rev, total_impact]
    ):
        with col:
            color = "#10B981" if label == "Total Projected Impact" else "#1A1A1A"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-number' style='color: {color};'>Rs {int(val):,}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)


# ==============================
# PAGE: CAMPAIGN BRIEF GENERATOR
# ==============================
elif page == "Campaign Brief Generator":
    st.markdown("""
    <div class='hero-title'>Campaign Brief Generator</div>
    <div class='hero-sub'>Select a customer and generate a personalised, AI-powered campaign brief in seconds.</div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.markdown("#### Select Customer")

        selected_seg_filter = st.selectbox(
            "Filter by segment",
            ["All"] + list(SEGMENT_CONFIG.keys()),
            format_func=lambda x: f"{SEGMENT_CONFIG[x]['icon']} {x}" if x != "All" else "All Segments"
        )

        if selected_seg_filter == "All":
            filtered_df = customers_df
        else:
            filtered_df = customers_df[customers_df["segment"] == selected_seg_filter]

        customer_options = filtered_df["customer_id"].tolist()
        selected_customer_id = st.selectbox("Select customer", customer_options)

        customer_row = customers_df[customers_df["customer_id"] == selected_customer_id].iloc[0]
        seg = customer_row["segment"]
        seg_config = SEGMENT_CONFIG[seg]
        playbook = INTERVENTION_PLAYBOOK[seg]

        st.markdown(f"""
        <div style='background: {seg_config["bg"]}; border-radius: 12px; padding: 1.2rem; 
                    border: 1px solid {seg_config["color"]}33; margin-top: 1rem;'>
            <div style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                        letter-spacing: 0.08em; color: {seg_config["color"]}; margin-bottom: 0.8rem;'>
                {seg_config["icon"]} {seg} Customer
            </div>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;'>
                <div>
                    <div style='font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;'>Total Orders</div>
                    <div style='font-size: 1.1rem; font-weight: 600;'>{int(customer_row["total_orders"])}</div>
                </div>
                <div>
                    <div style='font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;'>Avg Order Value</div>
                    <div style='font-size: 1.1rem; font-weight: 600;'>Rs {int(customer_row["avg_order_value"]):,}</div>
                </div>
                <div>
                    <div style='font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;'>Days Since Order</div>
                    <div style='font-size: 1.1rem; font-weight: 600;'>{int(customer_row["days_since_last_order"])}</div>
                </div>
                <div>
                    <div style='font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;'>Top Categories</div>
                    <div style='font-size: 0.82rem;'>{customer_row["preferred_categories"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("Generate Campaign Brief", use_container_width=True)

    with col_right:
        st.markdown("#### Intervention Prescription")

        st.markdown(f"""
        <div class='intervention-card' style='border-left: 3px solid {seg_config["color"]};'>
            <div class='intervention-label'>Goal</div>
            <div class='intervention-value'>{playbook["goal"]}</div>
        </div>
        <div class='intervention-card'>
            <div class='intervention-label'>Hypothesis</div>
            <div class='intervention-value'>{playbook["hypothesis"]}</div>
        </div>
        <div class='intervention-card'>
            <div class='intervention-label'>Success Metric</div>
            <div class='intervention-value'>{playbook["metric"]}</div>
        </div>
        """, unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("Generating brief..."):
                try:
                    customer_data = {
                        "preferred_categories": customer_row["preferred_categories"],
                        "total_orders": int(customer_row["total_orders"]),
                        "avg_order_value": int(customer_row["avg_order_value"]),
                        "days_since_last_order": int(customer_row["days_since_last_order"])
                    }

                    brief = generate_campaign_brief(seg, customer_data, playbook)

                    st.markdown("#### AI-Generated Campaign Brief")

                    st.markdown(f"""
                    <div class='brief-card'>
                        <div class='brief-label'>Subject Line</div>
                        <div class='brief-value' style='font-weight: 600; font-size: 1.05rem;'>{brief.get("subject_line", "")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='brief-card'>
                        <div class='brief-label'>WhatsApp Message</div>
                        <div class='brief-value'>{brief.get("whatsapp_message", "")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='brief-card'>
                        <div class='brief-label'>Push Notification</div>
                        <div class='brief-value'>{brief.get("push_notification", "")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='brief-card'>
                        <div class='brief-label'>Quality Hook</div>
                        <div class='brief-value'>{brief.get("quality_hook", "")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='intervention-card'>
                        <div class='intervention-label'>Campaign Rationale</div>
                        <div class='intervention-value'>{brief.get("campaign_rationale", "")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Brief generation failed: {str(e)}")
                    st.info("Make sure your ANTHROPIC_API_KEY is set in your environment.")
        else:
            st.markdown("""
            <div style='background: #F9FAFB; border-radius: 12px; padding: 2rem; text-align: center; 
                        border: 1px dashed #D1D5DB; color: #9CA3AF; font-size: 0.9rem; margin-top: 1rem;'>
                Select a customer and click Generate Campaign Brief to get an AI-powered, 
                personalised campaign tailored to their lifecycle stage and purchase behaviour.
            </div>
            """, unsafe_allow_html=True)
