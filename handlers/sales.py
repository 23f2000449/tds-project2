# handlers/sales.py
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """Convert matplotlib figure to base64 PNG under max_kb."""
    for dpi in (120, 100, 90, 80, 70, 60):
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        data = buf.getvalue()
        if len(data) <= max_kb * 1024:
            plt.close(fig)
            return base64.b64encode(data).decode("utf-8")
    plt.close(fig)
    return base64.b64encode(data).decode("utf-8")

def analyze_sales(csv_path: str) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["date"])

    total_revenue = (df["units_sold"] * df["unit_price"]).sum()
    best_product = df.groupby("product")["units_sold"].sum().idxmax()
    avg_units_per_day = df.groupby("date")["units_sold"].sum().mean()
    daily_revenue = (df.groupby("date")
                       .apply(lambda g: (g["units_sold"] * g["unit_price"]).sum())
                       .mean())

    # --- Bar chart: Total units sold per product ---
    fig1, ax1 = plt.subplots()
    df.groupby("product")["units_sold"].sum().plot(kind="bar", ax=ax1, color="skyblue")
    ax1.set_xlabel("Product")
    ax1.set_ylabel("Units Sold")
    ax1.set_title("Units Sold per Product")
    product_bar_chart = _plot_to_base64(fig1)

    # --- Line chart: Daily revenue over time ---
    fig2, ax2 = plt.subplots()
    revenue_by_date = df.groupby("date").apply(lambda g: (g["units_sold"] * g["unit_price"]).sum())
    ax2.plot(revenue_by_date.index, revenue_by_date.values, color="green")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Revenue")
    ax2.set_title("Revenue Over Time")
    revenue_line_chart = _plot_to_base64(fig2)

    return {
        "total_revenue": round(float(total_revenue), 2),
        "best_selling_product": str(best_product),
        "average_daily_units_sold": round(float(avg_units_per_day), 2),
        "average_daily_revenue": round(float(daily_revenue), 2),
        "product_bar_chart": product_bar_chart,
        "revenue_line_chart": revenue_line_chart,
    }
