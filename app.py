"""
Nassau Candy Distributor — Streamlit profitability & margin dashboard.
Run: streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import analytics as an

st.set_page_config(
    page_title="Nassau Candy — Profitability",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_prepared():
    raw = an.load_raw()
    clean, report = an.clean_data(raw)
    return an.add_row_metrics(clean), report


def _feedback_video_url() -> str:
    """Optional Streamlit Cloud secret FEEDBACK_VIDEO_URL (e.g. YouTube/Loom https link)."""
    try:
        return str(st.secrets.get("FEEDBACK_VIDEO_URL", "") or "").strip()
    except Exception:
        return ""


def main():
    st.title("Product line profitability & margin performance")
    st.caption(
        "Nassau Candy Distributor — order-level analytics, division comparison, "
        "cost diagnostics, and profit concentration (Pareto)."
    )

    try:
        base_df, clean_report = load_prepared()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    with st.sidebar:
        st.header("Filters")
        dmin = base_df["Order Date"].min().date()
        dmax = base_df["Order Date"].max().date()
        dr = st.date_input(
            "Order date range",
            value=(dmin, dmax),
            min_value=dmin,
            max_value=dmax,
        )
        if isinstance(dr, tuple) and len(dr) == 2:
            date_min, date_max = dr[0], dr[1]
        else:
            date_min, date_max = dmin, dmax

        divs = sorted(base_df["Division"].dropna().unique().tolist())
        div_pick = st.multiselect("Divisions", options=divs, default=divs)

        margin_thr = st.slider(
            "Margin threshold (%) for risk flags",
            min_value=0.0,
            max_value=100.0,
            value=35.0,
            step=1.0,
        )
        product_q = st.text_input("Product search (contains)", value="")

        st.divider()
        st.subheader("Data quality (cleaning)")
        st.caption(
            f"Rows: {clean_report['initial_rows']:,} → {clean_report['final_rows']:,} "
            f"| Dropped (missing core): {clean_report['dropped_missing_core']:,} "
            f"| Dropped (≤0 sales/units): {clean_report['dropped_nonpositive_sales_or_units']:,}"
        )
        st.caption(
            f"Profit vs (Sales−Cost) corrections (>tol): {clean_report['rows_profit_mismatch_gt_tol']:,}"
        )

    df = an.apply_filters(
        base_df,
        date_min=date_min,
        date_max=date_max,
        divisions=div_pick if div_pick else None,
        product_query=product_q,
    )
    if df.empty:
        st.warning("No rows match the current filters.")
        st.stop()

    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()
    overall_margin = (total_profit / total_sales * 100.0) if total_sales else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Filtered revenue", f"${total_sales:,.0f}")
    k2.metric("Gross profit", f"${total_profit:,.0f}")
    k3.metric("Portfolio gross margin", f"{overall_margin:.1f}%")
    k4.metric("Line items (rows)", f"{len(df):,}")

    prod = an.aggregate_by_product(df)
    div_agg = an.aggregate_by_division(df)
    vol = an.margin_volatility_by_product(df)
    prod = prod.merge(
        vol,
        on=["Division", "Product ID", "Product Name"],
        how="left",
    )
    prod["Margin Volatility (σ pp)"] = prod["Margin Volatility (σ pp)"].fillna(0.0)
    prod_risk = an.margin_risk_flags(prod, margin_threshold_pct=margin_thr)
    quad = an.classify_product_quadrants(prod)
    pareto_rev = an.pareto_analysis(prod, "Sales", "Revenue")
    pareto_prof = an.pareto_analysis(prod, "Gross_Profit", "Gross profit")
    reg_df, state_df = an.region_state_concentration(df)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Product profitability",
            "Division performance",
            "Cost vs margin diagnostics",
            "Profit concentration (Pareto)",
        ]
    )

    with tab1:
        st.subheader("Margin leaderboard & profit contribution")
        c1, c2 = st.columns(2)
        top_n = st.slider("Top N products to show in bar charts", 5, 40, 15)

        lead = prod_risk.sort_values("Gross Margin %", ascending=False).head(top_n)
        fig_m = px.bar(
            lead,
            x="Gross Margin %",
            y="Product Name",
            orientation="h",
            color="Division",
            hover_data=["Sales", "Gross_Profit", "Cost Ratio %"],
            title=f"Top {top_n} by gross margin %",
        )
        fig_m.update_layout(yaxis={"categoryorder": "total ascending"}, height=480)
        c1.plotly_chart(fig_m, use_container_width=True)

        lead_p = prod.sort_values("Gross_Profit", ascending=False).head(top_n)
        fig_p = px.bar(
            lead_p,
            x="Gross_Profit",
            y="Product Name",
            orientation="h",
            color="Division",
            hover_data=["Gross Margin %", "Sales", "Profit Contribution %"],
            title=f"Top {top_n} by total gross profit",
        )
        fig_p.update_layout(yaxis={"categoryorder": "total ascending"}, height=480)
        c2.plotly_chart(fig_p, use_container_width=True)

        st.subheader("Strategic quadrants (median split)")
        fig_sc = px.scatter(
            quad,
            x="Sales",
            y="Gross Margin %",
            color="Strategic Quadrant",
            size="Gross_Profit",
            hover_name="Product Name",
            hover_data=["Division", "Cost Ratio %", "Profit Contribution %"],
            title="Sales vs gross margin % (bubble size = gross profit)",
        )
        st.plotly_chart(fig_sc, use_container_width=True)

        st.subheader("Full product table")
        show_cols = [
            "Division",
            "Product Name",
            "Factory",
            "Sales",
            "Units",
            "Gross_Profit",
            "Gross Margin %",
            "Profit per Unit",
            "Cost Ratio %",
            "Revenue Contribution %",
            "Profit Contribution %",
            "Margin Volatility (σ pp)",
            "Risk: Below margin threshold",
            "Risk: High cost ratio",
        ]
        st.dataframe(
            prod_risk[show_cols].sort_values("Gross_Profit", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.subheader("Revenue vs profit by division")
        fig_div = go.Figure()
        fig_div.add_trace(
            go.Bar(name="Sales", x=div_agg["Division"], y=div_agg["Sales"], yaxis="y")
        )
        fig_div.add_trace(
            go.Bar(
                name="Gross profit",
                x=div_agg["Division"],
                y=div_agg["Gross_Profit"],
                yaxis="y2",
            )
        )
        fig_div.update_layout(
            barmode="group",
            yaxis=dict(title="Sales ($)"),
            yaxis2=dict(title="Gross profit ($)", overlaying="y", side="right"),
            legend=dict(orientation="h"),
            height=420,
        )
        st.plotly_chart(fig_div, use_container_width=True)

        c1, c2 = st.columns(2)
        fig_box = px.box(
            df,
            x="Division",
            y="Gross Margin %",
            color="Division",
            points="outliers",
            title="Distribution of line-item gross margin % by division",
        )
        fig_box.update_layout(showlegend=False, height=400)
        c1.plotly_chart(fig_box, use_container_width=True)

        fig_dm = px.bar(
            div_agg.sort_values("Gross Margin %", ascending=False),
            x="Division",
            y="Gross Margin %",
            color="Division",
            title="Weighted gross margin % by division",
        )
        fig_dm.update_layout(showlegend=False, height=400)
        c2.plotly_chart(fig_dm, use_container_width=True)

        st.subheader("Division summary")
        st.dataframe(
            div_agg.sort_values("Sales", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Geographic concentration (dependency indicators)")
        c3, c4 = st.columns(2)
        top_states = state_df.head(15)
        fig_s = px.bar(
            top_states,
            x="State/Province",
            y="Sales Share %",
            title="Top 15 states — share of filtered sales",
        )
        fig_s.update_layout(height=380)
        c3.plotly_chart(fig_s, use_container_width=True)

        top_reg = reg_df.head(10)
        fig_r = px.bar(
            top_reg,
            x="Region",
            y=["Sales Share %", "Profit Share %"],
            barmode="group",
            title="Region — sales vs profit share %",
        )
        fig_r.update_layout(height=380)
        c4.plotly_chart(fig_r, use_container_width=True)

    with tab3:
        st.subheader("Cost vs sales (margin risk)")
        fig_cs = px.scatter(
            prod_risk,
            x="Sales",
            y="Cost",
            color="Gross Margin %",
            size="Units",
            hover_name="Product Name",
            hover_data=["Division", "Cost Ratio %", "Gross_Profit"],
            title="Cost vs sales (color = gross margin %)",
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig_cs, use_container_width=True)

        st.subheader("Products flagged at current threshold")
        flagged = prod_risk[
            prod_risk["Risk: Below margin threshold"]
            | prod_risk["Risk: High cost ratio"]
        ].sort_values("Gross_Profit", ascending=False)
        st.dataframe(
            flagged[
                [
                    "Division",
                    "Product Name",
                    "Sales",
                    "Gross_Profit",
                    "Gross Margin %",
                    "Cost Ratio %",
                    "Risk: Below margin threshold",
                    "Risk: High cost ratio",
                    "Risk: Margin + cost stress",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "High cost ratio default: cost/sales > 85%. Adjust margin threshold in the sidebar; "
            "cost-ratio rule is fixed in analytics for structural cost-heavy SKUs."
        )

    with tab4:
        st.subheader("Pareto — revenue and profit concentration")

        def pareto_fig(pdf: pd.DataFrame, title: str):
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(
                    x=pdf["rank"],
                    y=pdf["share_pct"],
                    name="Product share %",
                    marker_color="#636EFA",
                ),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=pdf["rank"],
                    y=pdf["cum_share_pct"],
                    name="Cumulative %",
                    mode="lines",
                    line=dict(color="firebrick", width=2),
                ),
                secondary_y=True,
            )
            fig.add_hline(y=80, line_dash="dash", secondary_y=True, annotation_text="80%")
            fig.update_layout(
                title=title,
                xaxis_title="Product rank",
                height=460,
                legend=dict(orientation="h"),
            )
            fig.update_yaxes(title_text="Share of total (%)", secondary_y=False)
            fig.update_yaxes(title_text="Cumulative (%)", secondary_y=True, range=[0, 105])
            return fig

        t80r = an.pareto_threshold_rows(pareto_rev, 80)
        t80p = an.pareto_threshold_rows(pareto_prof, 80)
        st.markdown(
            f"**80% of revenue** is reached by the top **{t80r['rank']}** products "
            f"(cumulative {t80r['cum_share_pct']:.1f}%). "
            f"**80% of gross profit** is reached by the top **{t80p['rank']}** products "
            f"(cumulative {t80p['cum_share_pct']:.1f}%)."
        )

        c1, c2 = st.columns(2)
        c1.plotly_chart(
            pareto_fig(pareto_rev, "Revenue concentration by product rank"),
            use_container_width=True,
        )
        c2.plotly_chart(
            pareto_fig(pareto_prof, "Gross profit concentration by product rank"),
            use_container_width=True,
        )

        st.subheader("Manufacturing footprint (reference)")
        fac_rows = []
        for name, (lat, lon) in an.FACTORY_COORDS.items():
            fac_rows.append({"Factory": name, "lat": lat, "lon": lon})
        fac_df = pd.DataFrame(fac_rows)
        fig_map = px.scatter_geo(
            fac_df,
            lat="lat",
            lon="lon",
            text="Factory",
            projection="albers usa",
            title="Factory locations (US) — from project brief",
        )
        fig_map.update_traces(marker=dict(size=12))
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()
    with st.expander("Project feedback video — link for your submission", expanded=False):
        vurl = _feedback_video_url()
        if vurl:
            st.video(vurl)
            st.markdown("**Use this same URL** in your portal’s *Project feedback video* field:")
            st.code(vurl, language=None)
        else:
            st.markdown(
                """
Streamlit **cannot generate** a video link by itself. The form needs a normal **`https://`** URL from a
video host (YouTube, Loom, Google Drive with link sharing, etc.).

**What to do**
1. Record a short screen demo (this dashboard + what you learned) — e.g. **Win+G** (Xbox Game Bar) or your phone.
2. Upload to **YouTube** (**Unlisted**) or **loom.com**.
3. Copy the **`https://…`** link they give you — **paste that** in the *Project feedback video* field.

**Optional — show the video inside this app too:**  
Streamlit Cloud → **Manage app** → **Secrets** → add:

`FEEDBACK_VIDEO_URL = "https://www.youtube.com/watch?v=YOUR_ID"`

Save; the app will reboot and display your video and the copy-paste link below.
"""
            )


if __name__ == "__main__":
    main()
