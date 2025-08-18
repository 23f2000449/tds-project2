# handlers/sales.py
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io
import os

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
