# handlers/weather.py
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Headless backend
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

def analyze_weather(csv_path: str) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["date"])

    avg_temp = df["temp_c"].mean()
    max_precip_date = df.loc[df["precip_mm"].idxmax(), "date"].strftime("%Y-%m-%d")
    min_temp = df["temp_c"].min()
    correlation = df["temp_c"].corr(df["precip_mm"])
    avg_precip = df["precip_mm"].mean()

    # --- Line chart: Temperature over time ---
    fig1, ax1 = plt.subplots()
    ax1.plot(df["date"], df["temp_c"], color="red")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("Temperature Over Time")
    temp_line_chart = _plot_to_base64(fig1)

    # --- Histogram: Precipitation ---
    fig2, ax2 = plt.subplots()
    ax2.hist(df["precip_mm"], bins=10, color="orange", edgecolor="black")
    ax2.set_xlabel("Precipitation (mm)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Precipitation Histogram")
    precip_histogram = _plot_to_base64(fig2)

    return {
        "average_temp_c": round(float(avg_temp), 2),
        "max_precip_date": str(max_precip_date),
        "min_temp_c": round(float(min_temp), 2),
        "temp_precip_correlation": round(float(correlation), 10),
        "average_precip_mm": round(float(avg_precip), 2),
        "temp_line_chart": temp_line_chart,
        "precip_histogram": precip_histogram,
    }
