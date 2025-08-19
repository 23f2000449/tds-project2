import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """Convert matplotlib figure to base64 PNG string under max_kb."""
    try:
        for dpi in (150, 120, 100, 90, 80, 70, 60):
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
            data = buf.getvalue()
            if len(data) <= max_kb * 1024:
                plt.close(fig)
                return base64.b64encode(data).decode("utf-8")
        return base64.b64encode(data).decode("utf-8")
    finally:
        plt.close(fig)

def analyze_sales(csv_path: str) -> dict:
    df = pd.read_csv(csv_path)

    # Required calculations
    total_sales = df["sales"].sum()
    median_sales = df["sales"].median()

    # Assume df has a "region" column for top_region calculation
    top_region = df.groupby("region")["sales"].sum().idxmax()

    # Calculate correlation between day of month and sales
    # Extract day from "date" column, assuming format compatible
    df["day"] = pd.to_datetime(df["date"]).dt.day
    day_sales_correlation = df["day"].corr(df["sales"])

    # Calculate total sales tax (10% of total sales)
    total_sales_tax = total_sales * 0.10

    # Bar chart: total sales by region (blue bars)
    fig1, ax1 = plt.subplots()
    sales_by_region = df.groupby("region")["sales"].sum()
    ax1.bar(sales_by_region.index, sales_by_region, color="blue")
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Total Sales")
    ax1.set_title("Total Sales by Region")
    bar_chart = _plot_to_base64(fig1)

    # Cumulative sales over time line chart (red line)
    fig2, ax2 = plt.subplots()
    df_sorted = df.sort_values("date")
    df_sorted["cumulative_sales"] = df_sorted["sales"].cumsum()
    ax2.plot(df_sorted["date"], df_sorted["cumulative_sales"], color="red")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Cumulative Sales")
    ax2.set_title("Cumulative Sales Over Time")
    cumulative_sales_chart = _plot_to_base64(fig2)

    return {
        "total_sales": round(float(total_sales), 2),
        "top_region": str(top_region),
        "day_sales_correlation": round(float(day_sales_correlation), 5),
        "bar_chart": bar_chart,
        "median_sales": round(float(median_sales), 2),
        "total_sales_tax": round(float(total_sales_tax), 2),
        "cumulative_sales_chart": cumulative_sales_chart,
    }
