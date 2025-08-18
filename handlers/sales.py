import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_base64

@router.post("/analyze-sales")
async def analyze_sales(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    # Required columns — assume CSV is valid for portal
    df["date"] = pd.to_datetime(df["date"])

    total_sales = df["sales"].sum()
    region_sales = df.groupby("region")["sales"].sum()
    top_region = region_sales.idxmax()
    df["day"] = df["date"].dt.day
    day_sales_correlation = df["day"].corr(df["sales"])
    median_sales = df["sales"].median()
    total_sales_tax = total_sales * 0.10

    # Bar chart: total sales by region
    fig1, ax1 = plt.subplots()
    region_sales.plot(kind="bar", color="blue", ax=ax1)
    ax1.set_title("Total Sales by Region")
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Sales")
    bar_chart = fig_to_base64(fig1)

    # Line chart: cumulative sales over time
    df_sorted = df.sort_values("date")
    df_sorted["cumulative_sales"] = df_sorted["sales"].cumsum()
    fig2, ax2 = plt.subplots()
    ax2.plot(df_sorted["date"], df_sorted["cumulative_sales"], color="red")
    ax2.set_title("Cumulative Sales Over Time")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Cumulative Sales")
    cumulative_sales_chart = fig_to_base64(fig2)

    return {
        "total_sales": float(total_sales),
        "top_region": str(top_region),
        "day_sales_correlation": float(day_sales_correlation),
        "median_sales": float(median_sales),
        "total_sales_tax": float(total_sales_tax),
        "bar_chart": "data:image/png;base64," + bar_chart,
        "cumulative_sales_chart": "data:image/png;base64," + cumulative_sales_chart,
    }
