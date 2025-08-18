# handlers/sales.py
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io
import os

import base64
from io import BytesIO
import matplotlib.pyplot as plt

def _plot_to_base64(fig, max_kb: int = 100) -> str:
    """
    Convert a matplotlib figure to a base64-encoded PNG string under max_kb.
    Returns the base64 string (without data: prefix).
    """
    try:
        for dpi in (150, 120, 100, 90, 80, 70, 60):
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
            data = buf.getvalue()
            if len(data) <= max_kb * 1024:  # check size
                plt.close(fig)
                return base64.b64encode(data).decode("utf-8")
        # fallback: return even if it's bigger
        return base64.b64encode(data).decode("utf-8")
    finally:
        plt.close(fig)

def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def analyze_sales(csv_path: str):
    df = pd.read_csv(csv_path)

    # Ensure required columns
    if not {"date", "region", "sales"}.issubset(df.columns):
        raise ValueError("Sales CSV must contain columns: date, region, sales")

    df["date"] = pd.to_datetime(df["date"])
    total_sales = float(df["sales"].sum())
    avg_sales = float(df["sales"].mean())
    best_region = df.groupby("region")["sales"].sum().idxmax()

    # Sales trend line chart
    fig, ax = plt.subplots()
    df.groupby("date")["sales"].sum().plot(ax=ax, marker="o", color="blue")
    ax.set_title("Sales Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Sales")
    sales_trend_chart = _fig_to_base64(fig)

    # Regional sales bar chart
    fig, ax = plt.subplots()
    df.groupby("region")["sales"].sum().plot(kind="bar", ax=ax, color="green")
    ax.set_title("Regional Sales")
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    regional_sales_chart = _fig_to_base64(fig)

    return {
        "total_sales": total_sales,
        "average_sales": avg_sales,
        "best_region": best_region,
        "sales_trend_chart": sales_trend_chart,
        "regional_sales_chart": regional_sales_chart,
    }
