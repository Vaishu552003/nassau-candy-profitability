"""
Nassau Candy Distributor — data loading, cleaning, and profitability analytics.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

DATA_FILENAME = "Nassau Candy Distributor (1).csv"

FACTORY_COORDS = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.11914, -96.18115),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.1175, -89.971107),
}

# Division + Product Name -> manufacturing site (from project brief)
PRODUCT_FACTORY: list[tuple[str, str, str]] = [
    ("Chocolate", "Wonka Bar - Nutty Crunch Surprise", "Lot's O' Nuts"),
    ("Chocolate", "Wonka Bar - Fudge Mallows", "Lot's O' Nuts"),
    ("Chocolate", "Wonka Bar -Scrumdiddlyumptious", "Lot's O' Nuts"),
    ("Chocolate", "Wonka Bar - Milk Chocolate", "Wicked Choccy's"),
    ("Chocolate", "Wonka Bar - Triple Dazzle Caramel", "Wicked Choccy's"),
    ("Sugar", "Laffy Taffy", "Sugar Shack"),
    ("Sugar", "SweeTARTS", "Sugar Shack"),
    ("Sugar", "Nerds", "Sugar Shack"),
    ("Sugar", "Fun Dip", "Sugar Shack"),
    ("Sugar", "Fizzy Lifting Drinks", "Sugar Shack"),
    ("Sugar", "Everlasting Gobstopper", "Secret Factory"),
    ("Sugar", "Hair Toffee", "The Other Factory"),
    ("Other", "Lickable Wallpaper", "Secret Factory"),
    ("Other", "Wonka Gum", "Secret Factory"),
    ("Other", "Kazookles", "The Other Factory"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parent


def default_csv_path() -> Path:
    return project_root() / DATA_FILENAME


def _factory_lookup_df() -> pd.DataFrame:
    rows = [
        {"Division": d, "Product Name": p, "Factory": f} for d, p, f in PRODUCT_FACTORY
    ]
    return pd.DataFrame(rows)


def load_raw(csv_path: Path | str | None = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else default_csv_path()
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame, profit_tol: float = 0.05) -> tuple[pd.DataFrame, dict]:
    """
    Validate cost/sales, drop invalid rows, standardize labels, attach factory.
    Returns cleaned frame and a report dict (counts removed, flags).
    """
    report: dict = {"initial_rows": len(df)}
    d = df.copy()

    str_cols = [
        "Ship Mode",
        "Country/Region",
        "City",
        "State/Province",
        "Division",
        "Region",
        "Product ID",
        "Product Name",
    ]
    for c in str_cols:
        if c in d.columns:
            d[c] = d[c].astype(str).str.strip()
            if c in ("Division", "Product Name"):
                d[c] = d[c].str.replace(r"\s+", " ", regex=True)

    d["Order Date"] = pd.to_datetime(d["Order Date"], dayfirst=True, errors="coerce")
    d["Ship Date"] = pd.to_datetime(d["Ship Date"], dayfirst=True, errors="coerce")

    for col in ("Sales", "Units", "Gross Profit", "Cost"):
        d[col] = pd.to_numeric(d[col], errors="coerce")

    before = len(d)
    d = d.dropna(subset=["Sales", "Gross Profit", "Cost", "Units", "Order Date"])
    report["dropped_missing_core"] = before - len(d)

    before = len(d)
    d = d[(d["Sales"] > 0) & (d["Units"] > 0)]
    report["dropped_nonpositive_sales_or_units"] = before - len(d)

    implied = d["Sales"] - d["Cost"]
    delta = (d["Gross Profit"] - implied).abs()
    bad = delta > profit_tol
    report["rows_profit_mismatch_gt_tol"] = int(bad.sum())
    d.loc[bad, "Gross Profit"] = implied.loc[bad]

    lookup = _factory_lookup_df()
    d = d.merge(lookup, on=["Division", "Product Name"], how="left")

    report["final_rows"] = len(d)
    return d, report


def add_row_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Gross Margin %"] = np.where(
        out["Sales"] > 0, (out["Gross Profit"] / out["Sales"]) * 100.0, np.nan
    )
    out["Profit per Unit"] = out["Gross Profit"] / out["Units"]
    out["Cost Ratio %"] = np.where(
        out["Sales"] > 0, (out["Cost"] / out["Sales"]) * 100.0, np.nan
    )
    out["Order Month"] = out["Order Date"].dt.to_period("M").dt.to_timestamp()
    return out


def aggregate_by_product(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby(["Division", "Product ID", "Product Name", "Factory"], dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            Units=("Units", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    g["Gross Margin %"] = np.where(
        g["Sales"] > 0, (g["Gross_Profit"] / g["Sales"]) * 100.0, np.nan
    )
    g["Profit per Unit"] = g["Gross_Profit"] / g["Units"]
    g["Cost Ratio %"] = np.where(
        g["Sales"] > 0, (g["Cost"] / g["Sales"]) * 100.0, np.nan
    )
    total_sales = g["Sales"].sum()
    total_profit = g["Gross_Profit"].sum()
    g["Revenue Contribution %"] = np.where(
        total_sales > 0, (g["Sales"] / total_sales) * 100.0, 0.0
    )
    g["Profit Contribution %"] = np.where(
        total_profit != 0, (g["Gross_Profit"] / total_profit) * 100.0, 0.0
    )
    return g


def aggregate_by_division(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("Division", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    g["Gross Margin %"] = np.where(
        g["Sales"] > 0, (g["Gross_Profit"] / g["Sales"]) * 100.0, np.nan
    )
    g["Profit per Unit"] = g["Gross_Profit"] / g["Units"]
    return g


def margin_volatility_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """Std dev of row-level gross margin % by product over time (monthly means)."""
    x = df.copy()
    x["Order Month"] = x["Order Date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        x.groupby(
            ["Division", "Product ID", "Product Name", "Order Month"], dropna=False
        )
        .agg(Sales=("Sales", "sum"), Gross_Profit=("Gross Profit", "sum"))
        .reset_index()
    )
    monthly["Gross Margin %"] = np.where(
        monthly["Sales"] > 0,
        (monthly["Gross_Profit"] / monthly["Sales"]) * 100.0,
        np.nan,
    )
    vol = (
        monthly.groupby(["Division", "Product ID", "Product Name"], dropna=False)[
            "Gross Margin %"
        ]
        .std()
        .reset_index(name="Margin Volatility (σ pp)")
    )
    return vol


def pareto_analysis(
    product_agg: pd.DataFrame, value_col: str, label: str
) -> pd.DataFrame:
    """Sorted products with cumulative share of value_col."""
    p = product_agg.sort_values(value_col, ascending=False).copy()
    total = p[value_col].sum()
    p["share_pct"] = np.where(total > 0, (p[value_col] / total) * 100.0, 0.0)
    p["cum_share_pct"] = p["share_pct"].cumsum()
    p["rank"] = range(1, len(p) + 1)
    p["pareto_metric"] = label
    return p


def pareto_threshold_rows(pareto_df: pd.DataFrame, threshold: float = 80.0) -> dict:
    """First rank where cumulative share >= threshold."""
    hit = pareto_df[pareto_df["cum_share_pct"] >= threshold].head(1)
    if hit.empty:
        return {"rank": None, "cum_share_pct": None, "product": None}
    row = hit.iloc[0]
    return {
        "rank": int(row["rank"]),
        "cum_share_pct": float(row["cum_share_pct"]),
        "product": row["Product Name"],
    }


def region_state_concentration(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sales and profit share by Region and State for congestion / dependency view."""
    total_s = df["Sales"].sum()
    total_p = df["Gross Profit"].sum()

    def _geo(key: str) -> pd.DataFrame:
        g = (
            df.groupby(key, dropna=False)
            .agg(Sales=("Sales", "sum"), Gross_Profit=("Gross Profit", "sum"))
            .reset_index()
        )
        g["Sales Share %"] = (g["Sales"] / total_s) * 100.0 if total_s else 0.0
        g["Profit Share %"] = (g["Gross_Profit"] / total_p) * 100.0 if total_p else 0.0
        return g.sort_values("Sales", ascending=False)

    return _geo("Region"), _geo("State/Province")


def classify_product_quadrants(
    product_agg: pd.DataFrame, sales_median: float | None = None
) -> pd.DataFrame:
    """High/low sales vs margin quadrants (median split on log-sales and margin)."""
    p = product_agg.copy()
    med_s = sales_median if sales_median is not None else p["Sales"].median()
    med_m = p["Gross Margin %"].median()

    def quad(row: pd.Series) -> str:
        hs = row["Sales"] >= med_s
        hm = row["Gross Margin %"] >= med_m
        if hs and hm:
            return "High sales / High margin"
        if hs and not hm:
            return "High sales / Low margin"
        if not hs and not hm:
            return "Low sales / Low margin"
        return "Low sales / High margin"

    p["Strategic Quadrant"] = p.apply(quad, axis=1)
    return p


def margin_risk_flags(
    product_agg: pd.DataFrame,
    margin_threshold_pct: float,
    cost_ratio_threshold_pct: float = 85.0,
) -> pd.DataFrame:
    """Flag cost-heavy or below-threshold margin products."""
    p = product_agg.copy()
    p["Risk: Below margin threshold"] = p["Gross Margin %"] < margin_threshold_pct
    p["Risk: High cost ratio"] = p["Cost Ratio %"] > cost_ratio_threshold_pct
    p["Risk: Margin + cost stress"] = p["Risk: Below margin threshold"] & p[
        "Risk: High cost ratio"
    ]
    return p


def apply_filters(
    df: pd.DataFrame,
    date_min=None,
    date_max=None,
    divisions: list[str] | None = None,
    product_query: str = "",
) -> pd.DataFrame:
    out = df.copy()
    if date_min is not None:
        out = out[out["Order Date"].dt.date >= date_min]
    if date_max is not None:
        out = out[out["Order Date"].dt.date <= date_max]
    if divisions:
        out = out[out["Division"].isin(divisions)]
    q = (product_query or "").strip().lower()
    if q:
        out = out[out["Product Name"].str.lower().str.contains(q, na=False)]
    return out
