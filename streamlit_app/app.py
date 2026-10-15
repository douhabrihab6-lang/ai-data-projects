"""
Customer Segmentation Dashboard — RFM + K-Means
Author: Rihab Douhab
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Segmentation | RFM Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME / CUSTOM CSS ─────────────────────────────────────────
st.markdown("""
<style>
/* ---------- Global ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---------- Background ---------- */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1040 50%, #0f0c29 100%);
    color: #e8e0ff;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(108,99,255,0.3);
}

[data-testid="stSidebar"] .stRadio > label {
    font-size: 0.85rem;
    color: #b0a8d8;
}

/* ---------- KPI Cards ---------- */
.kpi-card {
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.35);
    border-radius: 16px;
    padding: 22px 18px;
    text-align: center;
    transition: transform .2s, box-shadow .2s;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(108,99,255,0.35);
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6C63FF, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.kpi-label {
    font-size: 0.82rem;
    color: #9d98c8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* ---------- Section headers ---------- */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #6C63FF 0%, #c4b5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}

/* ---------- Segment cards ---------- */
.seg-card {
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}

/* ---------- Divider ---------- */
.fancy-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #6C63FF, transparent);
    border: none;
    margin: 8px 0 24px 0;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "rfm_clustered.csv")
    df = pd.read_csv(data_path)
    return df

df = load_data()

PALETTE = {
    "🏆 Champions":        "#6C63FF",
    "💛 Loyal Customers":  "#F7931E",
    "⚠️  At Risk":         "#2EC4B6",
    "💤 Lost / Inactive":  "#E71D36",
}

# Normalise segment names (strip extra spaces)
df["Segment"] = df["Segment"].str.strip()

SEGMENTS = list(PALETTE.keys())
COLORS   = list(PALETTE.values())

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛍️ RFM Dashboard")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊 Overview", "🔍 RFM Explorer", "📈 Segment Profiles", "📣 Recommendations"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("### Filters")
    selected_segs = st.multiselect(
        "Segments",
        options=df["Segment"].unique().tolist(),
        default=df["Segment"].unique().tolist(),
    )
    recency_range = st.slider(
        "Recency (days)",
        int(df["Recency"].min()),
        int(df["Recency"].max()),
        (int(df["Recency"].min()), int(df["Recency"].max())),
    )
    monetary_range = st.slider(
        "Monetary (£)",
        float(df["Monetary"].min()),
        float(df["Monetary"].max()),
        (float(df["Monetary"].min()), float(df["Monetary"].max())),
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#6C63FF'>Built by **Rihab Douhab**</small>",
        unsafe_allow_html=True,
    )

# Apply filters
filtered = df[
    (df["Segment"].isin(selected_segs)) &
    (df["Recency"].between(*recency_range)) &
    (df["Monetary"].between(*monetary_range))
]


# ═══════════════════════════════════════════════════════════
#  PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════
if page == "📊 Overview":

    st.markdown('<div class="section-header">📊 Customer Segmentation Overview</div>', unsafe_allow_html=True)
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # KPI Row
    total_customers = len(filtered)
    avg_recency     = filtered["Recency"].mean()
    avg_frequency   = filtered["Frequency"].mean()
    avg_monetary    = filtered["Monetary"].mean()
    total_revenue   = filtered["Monetary"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, val, label in [
        (k1, f"{total_customers:,}",  "Total Customers"),
        (k2, f"{avg_recency:.0f} d",  "Avg Recency"),
        (k3, f"{avg_frequency:.1f}",  "Avg Frequency"),
        (k4, f"£{avg_monetary:,.0f}", "Avg Monetary"),
        (k5, f"£{total_revenue:,.0f}","Total Revenue"),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{val}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Row: Pie + Bar
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🧩 Segment Distribution")
        counts = filtered["Segment"].value_counts().reset_index()
        counts.columns = ["Segment", "Count"]
        seg_colors = [PALETTE.get(s, "#888") for s in counts["Segment"]]
        fig_pie = px.pie(
            counts, names="Segment", values="Count",
            color="Segment",
            color_discrete_map=PALETTE,
            hole=0.45,
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#0f0c29", width=2)),
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=340,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("#### 💰 Revenue by Segment")
        rev = filtered.groupby("Segment")["Monetary"].sum().reset_index()
        rev = rev.sort_values("Monetary", ascending=True)
        fig_bar = px.bar(
            rev, x="Monetary", y="Segment", orientation="h",
            color="Segment", color_discrete_map=PALETTE,
            text=rev["Monetary"].apply(lambda x: f"£{x:,.0f}"),
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)", title=""),
            yaxis=dict(showgrid=False, title=""),
            margin=dict(t=10, b=10, l=10, r=80),
            height=340,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Per-segment summary table
    st.markdown("#### 📋 Segment Summary Table")
    summary = (
        filtered.groupby("Segment")[["Recency", "Frequency", "Monetary"]]
        .agg(["mean", "median", "count"])
        .round(1)
    )
    summary.columns = [" ".join(c) for c in summary.columns]
    summary = summary.reset_index()
    st.dataframe(
        summary.style.background_gradient(cmap="Purples", subset=[c for c in summary.columns if "mean" in c]),
        use_container_width=True,
        hide_index=True,
    )


# ═══════════════════════════════════════════════════════════
#  PAGE 2 — RFM EXPLORER
# ═══════════════════════════════════════════════════════════
elif page == "🔍 RFM Explorer":

    st.markdown('<div class="section-header">🔍 RFM Explorer</div>', unsafe_allow_html=True)
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # 3-D scatter: Recency × Frequency × Monetary
    st.markdown("#### 🌐 3D RFM Scatter")
    fig_3d = px.scatter_3d(
        filtered,
        x="Recency", y="Frequency", z="Monetary",
        color="Segment",
        color_discrete_map=PALETTE,
        opacity=0.7,
        size_max=6,
        hover_data={"Customer ID": True},
    )
    fig_3d.update_traces(marker=dict(size=3))
    fig_3d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8e0ff",
        scene=dict(
            xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.1)"),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=520,
        margin=dict(t=0, b=0),
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 📦 Recency Distribution")
        fig_r = px.histogram(
            filtered, x="Recency", color="Segment",
            color_discrete_map=PALETTE,
            nbins=40, barmode="overlay", opacity=0.7,
        )
        fig_r.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=300, margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_r, use_container_width=True)

    with c2:
        st.markdown("#### 💸 Monetary Distribution (log scale)")
        fig_m = px.histogram(
            filtered, x="Monetary", color="Segment",
            color_discrete_map=PALETTE,
            nbins=40, barmode="overlay", opacity=0.7,
            log_x=True,
        )
        fig_m.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=300, margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_m, use_container_width=True)

    # Correlation heatmap
    st.markdown("#### 🔥 RFM Correlation Heatmap")
    corr = filtered[["Recency", "Frequency", "Monetary"]].corr()
    fig_corr = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig_corr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8e0ff",
        height=320, margin=dict(t=10, b=10),
        coloraxis_colorbar=dict(tickfont=dict(color="#e8e0ff")),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Raw data table
    with st.expander("📄 View Raw Data"):
        st.dataframe(
            filtered[["Customer ID", "Recency", "Frequency", "Monetary", "Segment"]]
            .sort_values("Monetary", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# ═══════════════════════════════════════════════════════════
#  PAGE 3 — SEGMENT PROFILES
# ═══════════════════════════════════════════════════════════
elif page == "📈 Segment Profiles":

    st.markdown('<div class="section-header">📈 Segment Profiles</div>', unsafe_allow_html=True)
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # Snake plot
    st.markdown("#### 🐍 Snake Plot — Normalised RFM per Segment")

    rfm_norm = filtered.copy()
    for col in ["Recency", "Frequency", "Monetary"]:
        _min, _max = df[col].min(), df[col].max()   # use global range for consistency
        rfm_norm[col] = (rfm_norm[col] - _min) / (_max - _min)

    snake = rfm_norm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean().reset_index()

    fig_snake = go.Figure()
    for _, row in snake.iterrows():
        seg = row["Segment"]
        fig_snake.add_trace(go.Scatter(
            x=["Recency", "Frequency", "Monetary"],
            y=[row["Recency"], row["Frequency"], row["Monetary"]],
            mode="lines+markers",
            name=seg,
            line=dict(color=PALETTE.get(seg, "#888"), width=3),
            marker=dict(size=10, symbol="circle"),
        ))
    fig_snake.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8e0ff",
        yaxis=dict(title="Normalised Value (0–1)", showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(showgrid=False),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=380, margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig_snake, use_container_width=True)

    # Heatmap + Box plots side by side
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🗺️ RFM Heatmap")
        hm_data = snake.set_index("Segment")[["Recency", "Frequency", "Monetary"]]
        fig_hm = px.imshow(
            hm_data, text_auto=".2f",
            color_continuous_scale="Viridis",
            aspect="auto",
        )
        fig_hm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            height=300, margin=dict(t=10, b=10),
            coloraxis_colorbar=dict(tickfont=dict(color="#e8e0ff")),
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    with c2:
        st.markdown("#### 📦 Frequency Box Plot")
        fig_box = px.box(
            filtered, x="Segment", y="Frequency",
            color="Segment", color_discrete_map=PALETTE,
            notched=True,
        )
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
            height=300, margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # PCA scatter
    st.markdown("#### 🔵 PCA 2D Cluster Visualisation")
    if "PC1" in filtered.columns and "PC2" in filtered.columns:
        fig_pca = px.scatter(
            filtered, x="PC1", y="PC2",
            color="Segment", color_discrete_map=PALETTE,
            opacity=0.55,
            hover_data={"Customer ID": True, "Recency": True, "Monetary": True},
        )
        fig_pca.update_traces(marker=dict(size=5))
        fig_pca.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e0ff",
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_pca, use_container_width=True)
    else:
        st.info("PCA columns (PC1/PC2) not found in data. Run the full notebook to generate them.")

    # Violin plot
    st.markdown("#### 🎻 Monetary Violin Plot")
    fig_vio = px.violin(
        filtered, x="Segment", y="Monetary",
        color="Segment", color_discrete_map=PALETTE,
        box=True, points="outliers",
    )
    fig_vio.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8e0ff",
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(showgrid=False),
        height=380, margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig_vio, use_container_width=True)


# ═══════════════════════════════════════════════════════════
#  PAGE 4 — MARKETING RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════
elif page == "📣 Recommendations":

    st.markdown('<div class="section-header">📣 Marketing Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    recommendations = {
        "🏆 Champions": {
            "color": "#6C63FF",
            "bg": "rgba(108,99,255,0.12)",
            "border": "rgba(108,99,255,0.5)",
            "tagline": "Your best customers — reward them!",
            "profile": "Low Recency · High Frequency · High Monetary",
            "actions": [
                "🎁 Enrol in a VIP loyalty programme with exclusive perks",
                "⭐ Ask for reviews and referrals — they trust your brand",
                "🚀 Give early access to new products / limited editions",
                "📩 Send personalised 'thank you' emails with surprise rewards",
            ],
        },
        "💛 Loyal Customers": {
            "color": "#F7931E",
            "bg": "rgba(247,147,30,0.10)",
            "border": "rgba(247,147,30,0.45)",
            "tagline": "Consistent buyers — grow their basket",
            "profile": "Medium Recency · Medium Frequency · Medium Monetary",
            "actions": [
                "📦 Upsell premium versions of products they already buy",
                "🔁 Cross-sell complementary categories",
                "💌 Send personalised product recommendations via email",
                "🎟️ Offer membership / subscription deals to increase stickiness",
            ],
        },
        "⚠️  At Risk": {
            "color": "#2EC4B6",
            "bg": "rgba(46,196,182,0.10)",
            "border": "rgba(46,196,182,0.45)",
            "tagline": "Were good customers — win them back!",
            "profile": "High Recency · Low-Medium Frequency · Medium Monetary",
            "actions": [
                "💸 Send a win-back campaign: 'We miss you!' with a discount code",
                "📲 Trigger SMS / email re-engagement sequence over 2–3 weeks",
                "🎯 Personalised product recommendations based on past purchases",
                "🔔 Remind them of items left in the cart or wishlisted products",
            ],
        },
        "💤 Lost / Inactive": {
            "color": "#E71D36",
            "bg": "rgba(231,29,54,0.10)",
            "border": "rgba(231,29,54,0.45)",
            "tagline": "Dormant customers — last chance!",
            "profile": "Very High Recency · Very Low Frequency · Low Monetary",
            "actions": [
                "🔥 Last-chance reactivation offer (biggest discount tier)",
                "📋 Send a short churn survey: 'What stopped you shopping with us?'",
                "🚫 If no response in 6 months, remove from active mailing list",
                "💡 Consider re-targeting via paid social ads / display campaigns",
            ],
        },
    }

    # Segment selector at top
    active_segs = [s for s in recommendations if s.strip() in filtered["Segment"].unique()]
    tab_labels  = list(recommendations.keys())
    tabs = st.tabs(tab_labels)

    for tab, (seg, info) in zip(tabs, recommendations.items()):
        with tab:
            stripped = seg.strip()
            count = len(filtered[filtered["Segment"] == stripped])
            pct   = count / len(df) * 100 if len(df) > 0 else 0

            st.markdown(f"""
            <div style="
                background: {info['bg']};
                border: 1px solid {info['border']};
                border-radius: 16px;
                padding: 24px 28px;
                margin-bottom: 20px;
            ">
                <h2 style="color:{info['color']};margin:0 0 6px 0;">{seg}</h2>
                <p style="color:#c4b5fd;font-size:0.95rem;margin:0 0 10px 0;font-style:italic;">
                    {info['tagline']}
                </p>
                <p style="color:#9d98c8;font-size:0.82rem;margin:0;">
                    📊 <strong style="color:{info['color']}">{count:,}</strong> customers
                    &nbsp;|&nbsp; <strong style="color:{info['color']}">{pct:.1f}%</strong> of base
                    &nbsp;|&nbsp; Profile: <em>{info['profile']}</em>
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 🎯 Recommended Actions")
            for action in info["actions"]:
                st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.04);
                    border-left: 3px solid {info['color']};
                    border-radius: 0 8px 8px 0;
                    padding: 12px 16px;
                    margin-bottom: 10px;
                    font-size: 0.95rem;
                    color: #e8e0ff;
                ">{action}</div>
                """, unsafe_allow_html=True)

            # Mini metrics for this segment
            seg_data = filtered[filtered["Segment"] == stripped]
            if len(seg_data) > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📐 Segment Metrics")
                ma, mb, mc, md = st.columns(4)
                for col, val, label in [
                    (ma, f"{seg_data['Recency'].mean():.0f} d",   "Avg Recency"),
                    (mb, f"{seg_data['Frequency'].mean():.1f}",   "Avg Frequency"),
                    (mc, f"£{seg_data['Monetary'].mean():,.0f}",  "Avg Monetary"),
                    (md, f"£{seg_data['Monetary'].sum():,.0f}",   "Total Revenue"),
                ]:
                    col.metric(label, val)
