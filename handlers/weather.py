import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend
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
                return base64.b64encode(data).decode("utf-8")
        return base64.b64encode(data).decode("utf-8")
    finally:
        plt.close(fig)

def analyze_weather(csv_path: str) -> dict:
    df = pd.read_csv(csv_path)

    # Check for temperature column: accept either 'temp_c' or 'temperature_c'
    if "temp_c" in df.columns:
        temp_col = "temp_c"
    elif "temperature_c" in df.columns:
        temp_col = "temperature_c"
    else:
        raise ValueError("CSV missing temperature column 'temp_c' or 'temperature_c'")

    # Required columns check (always must have 'precip_mm' and 'date')
    required_columns = {"precip_mm", "date"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    avg_temp = df[temp_col].mean()
    min_temp = df[temp_col].min()

    max_precip_idx = df["precip_mm"].idxmax()
    max_precip_date = df.loc[max_precip_idx, "date"] if pd.notna(max_precip_idx) else ""

    avg_precip = df["precip_mm"].mean()
    correlation = df[temp_col].corr(df["precip_mm"])

    # Temperature line chart
    fig1, ax1 = plt.subplots()
    ax1.plot(df["date"], df[temp_col], color="red")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("Temperature Over Time")
    temp_line_chart = _plot_to_base64(fig1)

    # Precipitation histogram
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
        "temp_precip_correlation": round(float(correlation), 2),
        "average_precip_mm": round(float(avg_precip), 2),
        "temp_line_chart": temp_line_chart,
        "precip_histogram": precip_histogram,
    }
