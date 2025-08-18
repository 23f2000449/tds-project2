# main.py
from __future__ import annotations

import os
import tempfile
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# --- Import handlers ---
try:
    from handlers.weather import analyze_weather
except Exception as e:
    analyze_weather = None
    WEATHER_IMPORT_ERROR = e
else:
    WEATHER_IMPORT_ERROR = None

try:
    from handlers.sales import analyze_sales
except Exception as e:
    analyze_sales = None
    SALES_IMPORT_ERROR = e
else:
    SALES_IMPORT_ERROR = None

try:
    from handlers.network import analyze_network
except Exception as e:
    analyze_network = None
    NETWORK_IMPORT_ERROR = e
else:
    NETWORK_IMPORT_ERROR = None


# ------------------------ FastAPI app ------------------------
app = FastAPI(title="TDS Project – Data Analyst Agent API")


@app.get("/")
def root() -> Dict[str, Any]:
    """Health/info endpoint."""
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "endpoint": "POST / (upload CSV to auto-detect type)",
    }


# ------------- Helpers -------------
def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    """Save UploadFile to a temporary file and return its path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.file.read())
            return tmp.name
    finally:
        try:
            upload.file.close()
        except Exception:
            pass


def _detect_handler(csv_path: str):
    """Detect which handler to call based on CSV columns."""
    import pandas as pd
    try:
        df = pd.read_csv(csv_path, nrows=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    cols = set(df.columns.str.lower())

    if {"date", "temp_c", "precip_mm"}.issubset(cols):
        if analyze_weather is None:
            raise HTTPException(status_code=500, detail=f"Weather handler unavailable: {WEATHER_IMPORT_ERROR}")
        return analyze_weather

    if {"product", "sales"}.issubset(cols):
        if analyze_sales is None:
            raise HTTPException(status_code=500, detail=f"Sales handler unavailable: {SALES_IMPORT_ERROR}")
        return analyze_sales

    if {"source", "target"}.issubset(cols):
        if analyze_network is None:
            raise HTTPException(status_code=500, detail=f"Network handler unavailable: {NETWORK_IMPORT_ERROR}")
        return analyze_network

    raise HTTPException(status_code=400, detail="CSV format not recognized as weather, sales, or network.")


# ------------- Unified evaluator endpoint -------------
@app.post("/")
async def analyze_csv(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file, suffix=".csv")
    try:
        handler = _detect_handler(path)
        result = handler(path)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Handler must return a dict JSON object.")
        return JSONResponse(content=result)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


# ------------- Local run -------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
