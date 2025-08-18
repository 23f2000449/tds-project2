# main.py
from __future__ import annotations

import os
import tempfile
import pandas as pd
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# --- Handlers ---
try:
    from handlers.weather import analyze_weather
except Exception as e:
    analyze_weather = None
    WEATHER_ERROR = e
else:
    WEATHER_ERROR = None

try:
    from handlers.sales import analyze_sales
except Exception as e:
    analyze_sales = None
    SALES_ERROR = e
else:
    SALES_ERROR = None

try:
    from handlers.network import analyze_network_from_path
except Exception as e:
    analyze_network_from_path = None
    NETWORK_ERROR = e
else:
    NETWORK_ERROR = None

# -------------------- FastAPI App --------------------
app = FastAPI(title="TDS Project – Data Analyst Agent API")


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "note": "POST a CSV file to '/' and the system will auto-detect whether it's weather, sales, or network data."
    }


def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(upload.file.read())
        return tmp.name


# -------------------- Dispatcher --------------------
@app.post("/")
async def analyze_auto(file: UploadFile = File(...)) -> JSONResponse:
    """Universal evaluator endpoint: POST CSV to `/`.
    It auto-detects dataset type and calls the right handler.
    """
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file)
    try:
        df = pd.read_csv(path)

        # Weather dataset?
        if {"date", "temp_c", "precip_mm"}.issubset(df.columns):
            if analyze_weather is None:
                raise HTTPException(status_code=500, detail=f"Weather handler unavailable: {WEATHER_ERROR}")
            result = analyze_weather(path)

        # Sales dataset?
        elif {"date", "region", "sales"}.issubset(df.columns):
            if analyze_sales is None:
                raise HTTPException(status_code=500, detail=f"Sales handler unavailable: {SALES_ERROR}")
            # sales handler expects UploadFile, not path
            # wrap it with fake file
            result = await analyze_sales(file)

        # Network dataset?
        elif {"source", "target"}.issubset(df.columns):
            if analyze_network_from_path is None:
                raise HTTPException(status_code=500, detail=f"Network handler unavailable: {NETWORK_ERROR}")
            result = analyze_network_from_path(path)

        else:
            raise HTTPException(status_code=400, detail="CSV format not recognized as weather, sales, or network.")

        return JSONResponse(content=result)

    finally:
        try:
            os.remove(path)
        except Exception:
            pass


# -------------------- Explicit Endpoints --------------------
@app.post("/analyze-weather")
async def analyze_weather_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    path = _save_upload_to_temp(file)
    try:
        if analyze_weather is None:
            raise HTTPException(status_code=500, detail=f"Weather handler unavailable: {WEATHER_ERROR}")
        result = analyze_weather(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)


@app.post("/analyze-sales")
async def analyze_sales_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    if analyze_sales is None:
        raise HTTPException(status_code=500, detail=f"Sales handler unavailable: {SALES_ERROR}")
    result = await analyze_sales(file)
    return JSONResponse(content=result)


@app.post("/analyze-network")
async def analyze_network_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    path = _save_upload_to_temp(file)
    try:
        if analyze_network_from_path is None:
            raise HTTPException(status_code=500, detail=f"Network handler unavailable: {NETWORK_ERROR}")
        result = analyze_network_from_path(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)


# -------------------- Local Run --------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
