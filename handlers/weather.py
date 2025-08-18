import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def plot_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return encoded

def analyze_weather(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["date"])
    
    avg_temp = df["temp_c"].mean()
    max_precip_date = df.loc[df["precip_mm"].idxmax(), "date"].strftime("%Y-%m-%d")
    min_temp = df["temp_c"].min()
    correlation = df["temp_c"].corr(df["precip_mm"])
    avg_precip = df["precip_mm"].mean()

    # Line chart: Temperature over time
    fig1, ax1 = plt.subplots()
    ax1.plot(df["date"], df["temp_c"], color="red")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("Temperature Over Time")
    temp_line_chart = plot_to_base64(fig1)

    # Histogram: Precipitation
    fig2, ax2 = plt.subplots()
    ax2.hist(df["precip_mm"], bins=10, color="orange", edgecolor="black")
    ax2.set_xlabel("Precipitation (mm)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Precipitation Histogram")
    precip_histogram = plot_to_base64(fig2)

    return {
        "average_temp_c": float(round(avg_temp, 2)),
        "max_precip_date": str(max_precip_date),
        "min_temp_c": float(round(min_temp, 2)),
        "temp_precip_correlation": float(round(correlation, 10)),
        "average_precip_mm": float(round(avg_precip, 2)),
        "temp_line_chart": "data:image/png;base64," + temp_line_chart,
        "precip_histogram": "data:image/png;base64," + precip_histogram
    }
