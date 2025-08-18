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

    total_sales = df["sales"].sum()
    average_sales = df["sales"].mean()
    max_sales_product = df.loc[df["sales"].idxmax(), "product"]
    min_sales_product = df.loc[df["sales"].idxmin(), "product"]

    # --- Sales bar chart ---
    fig1, ax1 = plt.subplots()
    ax1.bar(df["product"], df["sales"], color="blue")
    ax1.set_xlabel("Product")
    ax1.set_ylabel("Sales")
    ax1.set_title("Sales by Product")
    sales_bar_chart = _plot_to_base64(fig1)

    # --- Sales pie chart ---
    fig2, ax2 = plt.subplots()
    df_grouped = df.groupby("product")["sales"].sum()
    ax2.pie(df_grouped, labels=df_grouped.index, autopct="%1.1f%%")
    ax2.set_title("Sales Distribution")
    sales_pie_chart = _plot_to_base64(fig2)

    return {
        "total_sales": round(float(total_sales), 2),
        "average_sales": round(float(average_sales), 2),
        "max_sales_product": str(max_sales_product),
        "min_sales_product": str(min_sales_product),
        "sales_bar_chart": sales_bar_chart,
        "sales_pie_chart": sales_pie_chart,
    }
