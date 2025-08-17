# handlers/sales.py

import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 PNG under 100kB."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_base64

@router.post("/analyze-sales")
async def analyze_sales(file: UploadFile = File(...)):
    # Load dataset from uploaded file
    df = pd.read_csv(file.file)

    # Ensure expected columns exist
    if not {"date", "region", "sales"}.issubset(df.columns):
        return {"error": "CSV must contain 'date', 'region', and 'sales' columns."}

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])

    # 1. Total sales
    total_sales = df["sales"].sum()

    # 2. Region with highest sales
    region_sales = df.groupby("region")["sales"].sum()
    top_region = region_sales.idxmax()

    # 3. Correlation between day of month and sales
    df["day"] = df["date"].dt.day
    day_sales_correlation = df["day"].corr(df["sales"])

    # 4. Median sales
    median_sales = df["sales"].median()

    # 5. Total sales tax (10%)
    total_sales_tax = total_sales * 0.10

    # 6. Bar chart: total sales by region
    fig1, ax1 = plt.subplots()
    region_sales.plot(kind="bar", color="blue", ax=ax1)
    ax1.set_title("Total Sales by Region")
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Sales")
    bar_chart = fig_to_base64(fig1)

    # 7. Line chart: cumulative sales over time
    df_sorted = df.sort_values("date")
    df_sorted["cumulative_sales"] = df_sorted["sales"].cumsum()
    fig2, ax2 = plt.subplots()
    ax2.plot(df_sorted["date"], df_sorted["cumulative_sales"], color="red")
    ax2.set_title("Cumulative Sales Over Time")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Cumulative Sales")
    cumulative_sales_chart = fig_to_base64(fig2)

    # Build response JSON
    return {
        "total_sales": float(total_sales),
        "top_region": str(top_region),
        "day_sales_correlation": float(day_sales_correlation),
        "bar_chart": bar_chart,
        "median_sales": float(median_sales),
        "total_sales_tax": float(total_sales_tax),
        "cumulative_sales_chart": cumulative_sales_chart,
    }
