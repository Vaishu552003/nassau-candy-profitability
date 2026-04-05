# Executive summary — product line profitability (Nassau Candy Distributor)

**Audience:** Government and regulatory stakeholders, executive leadership  
**Purpose:** Summarize how order-level sales and cost data are turned into transparent measures of gross margin, profit concentration, and division-level performance to support evidence-based commercial policy and oversight.

## Problem

Sales volume alone is an unreliable indicator of economic contribution. High-turnover SKUs may carry low gross margins or high cost-to-sales ratios, weakening overall portfolio profitability. Without consistent metrics and interactive analytics, pricing, promotions, and assortment decisions tend to be reactive.

## Approach

The analysis uses validated order lines with **sales**, **cost**, **units**, and **gross profit**, standardized **division** and **product** labels, and calculated KPIs:

- **Gross margin (%)** = gross profit ÷ sales  
- **Profit per unit** = gross profit ÷ units  
- **Revenue and profit contribution** = share of totals at product level  
- **Margin volatility** = variability of margin over time (monthly aggregation)  
- **Pareto concentration** = cumulative share of revenue and profit across ranked products  

Geographic views (**region** and **state/province**) highlight revenue and profit concentration that may indicate dependency or congestion in specific markets.

## Deliverables

1. **Streamlit dashboard** (`app.py`) — filters by date range, division, margin threshold, and product search; modules for product profitability, division performance, cost–margin diagnostics, and Pareto analysis.  
2. **Research paper** (`docs/Research_Paper.md`) — methodology, exploratory findings framework, and recommendations.  
3. **Reproducible analytics layer** (`analytics.py`) — documented cleaning rules and metric definitions.

## Governance and transparency

- **Data quality:** Invalid or non-positive sales and units are excluded; gross profit is reconciled to sales minus cost within a defined tolerance.  
- **Auditability:** Metric definitions are implemented in code and mirrored in documentation.  
- **Risk flags:** Products below a user-set margin threshold and/or with very high cost-to-sales ratios are highlighted for review (repricing, sourcing, or discontinuation), not for automated enforcement.

## Strategic use

The dashboard supports **portfolio rationalization**, **division benchmarking**, **dependency risk awareness** (Pareto and geography), and **targeted follow-up** on cost-heavy, low-margin items — aligning operational and policy conversations with a single, consistent view of profitability.

---

*Note: Run `streamlit run app.py` from the project folder after installing dependencies from `requirements.txt`.*
