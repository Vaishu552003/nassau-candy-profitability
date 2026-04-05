# Research paper — exploratory analysis of product line profitability (Nassau Candy Distributor)

## 1. Introduction

Distributors must balance **revenue growth** with **margin quality**. This study analyzes transactional order data for Nassau Candy Distributor to expose which product lines and divisions contribute disproportionately to gross profit, which SKUs combine high sales with weak margins, and how concentrated profit is across the portfolio (Pareto structure).

## 2. Data and fields

The dataset includes line-level orders with: identifiers (`Row ID`, `Order ID`, `Product ID`), dates (`Order Date`, `Ship Date`), customer geography (`Country/Region`, `City`, `State/Province`, `Region`), **Division**, **Product Name**, **Sales**, **Units**, **Gross Profit**, and **Cost**.

Manufacturing sites are mapped from the project brief (division + product name) for reference; factory coordinates are visualized in the dashboard for geographic context.

## 3. Data cleaning and validation

1. **Standardization:** Trim whitespace; normalize internal spaces in division and product name to support consistent joins (e.g., factory mapping).  
2. **Parsing:** `Order Date` and `Ship Date` parsed with **day-first** interpretation to match the source format.  
3. **Core completeness:** Rows with missing sales, cost, gross profit, units, or order date are removed.  
4. **Business validity:** Rows with non-positive **sales** or **units** are removed (undefined or misleading margin and profit-per-unit).  
5. **Profit consistency:** Where recorded gross profit deviates from **sales − cost** beyond a small tolerance, gross profit is **recomputed** from sales and cost to preserve internal consistency for margin analytics.

Cleaning statistics are surfaced in the Streamlit sidebar for transparency.

## 4. Methodology

### 4.1 Row-level metrics

- Gross margin (%) = (gross profit ÷ sales) × 100  
- Profit per unit = gross profit ÷ units  
- Cost ratio (%) = (cost ÷ sales) × 100  

### 4.2 Product-level aggregation

Products are aggregated by `Division`, `Product ID`, and `Product Name` (and factory where matched). Totals for sales, units, gross profit, and cost support:

- **Revenue contribution** and **profit contribution** (percent of filtered portfolio).  
- **Strategic quadrants:** median split on sales and gross margin % classifies SKUs into high/low sales and high/low margin segments.  

### 4.3 Division-level aggregation

Divisions are compared on total sales, gross profit, implied gross margin %, and distribution of line-item margins (box plots).

### 4.4 Margin volatility

For each product, monthly gross margin % is computed from summed sales and profit; the **standard deviation** of those monthly margins is reported as a simple volatility indicator (interpret with caution for sparse months).

### 4.5 Pareto (concentration) analysis

Products are ranked by total sales and by total gross profit; cumulative share curves identify how many SKUs account for **80%** of revenue and **80%** of profit — a standard lens for dependency risk.

### 4.6 Geographic concentration

**Region** and **state/province** tables show share of filtered sales and gross profit to highlight markets that drive results or create geographic dependency.

### 4.7 Cost–margin diagnostics

Scatter plots of cost vs. sales (color = margin %) and rule-based **risk flags** (margin below a user threshold; cost ratio above 85%) support identification of candidates for repricing, cost renegotiation, or discontinuation review.

## 5. Exploratory findings (framework)

*After running the dashboard on the full CSV, replace this section with concrete numbers and charts.*

- **Division comparison:** Expect differences in average margin and in the spread of line-item margins; divisions with high revenue but lagging profit merit pricing and mix review.  
- **High sales / low margin:** Quadrant and scatter views isolate SKUs that dilute portfolio margin despite volume.  
- **Pareto:** Typically a minority of SKUs drives a large share of profit; mismatches between revenue-Pareto and profit-Pareto ranks signal margin structure issues.  
- **Geography:** A small set of states or regions may dominate sales and profit — relevant for capacity, service levels, and risk planning.  
- **Outliers:** Products such as those with very high cost ratios relative to peers in the same division should be prioritized for sourcing or pricing workstreams.

## 6. Recommendations

1. **Institutionalize KPIs:** Adopt gross margin %, profit per unit, and contribution percentages as standard product-review metrics.  
2. **Quarterly portfolio review:** Use Pareto and quadrant views to set promotion, delisting, and cost targets.  
3. **Division scorecards:** Compare revenue, profit, and margin distribution; investigate structural cost or price gaps.  
4. **Playbooks for flagged SKUs:** Define steps for repricing, supplier negotiation, pack-size changes, and exit criteria.  
5. **Data governance:** Keep division and product naming conventions stable; log cleaning exclusions for audit trails.

## 7. Limitations

- Gross margin does not allocate **operating** or **logistics** overhead by SKU in this build.  
- Margin volatility is sensitive to low-frequency products.  
- Factory mapping applies only to listed division–product pairs; unmatched rows retain null factory.

## 8. Conclusion

Linking **volume**, **cost**, and **gross profit** at order line level enables Nassau Candy Distributor to see which products truly drive profit, how divisions compare, and where concentration creates risk. The Streamlit application operationalizes this methodology for ongoing, filterable decision support.

## References

- Implementation: `analytics.py`, `app.py`  
- Dataset: `Nassau Candy Distributor (1).csv`  
- Executive summary: `docs/Executive_Summary.md`
