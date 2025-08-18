# main.py
from __future__ import annotations

import os
import tempfile
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")  # headless backend

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Import handlers
from handlers.weather import analyze_weather
from handlers.sales import analyze_sales
from handlers.network import analyze_network


# ------------------------ FastAPI app ------------------------
app = FastAPI(title="TDS Project – Unified API")


@app.get("/")
def root() -> Dict[str, Any]:
    """Health/info endpoint (GET only)."""
    return {
        "service": "TDS Project – Unified API",
        "status": "ok",
        "usage": "POST a CSV file to `/` and it will auto-analyze (weather, sales, or network).",
    }


# ------------- Helpers -------------
def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    """Save an UploadFile to a temporary file and return path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.file.read())
            return tmp.name
    finally:
        try:
            upload.file.close()
        except Exception:
            pass


def _detect_dataset_type(path: str) -> str:
    """Peek CSV header to decide which handler to use."""
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip().lower()

    if "temperature" in header and "precipitation" in header:
        return "weather"
    elif "sales" in header or "revenue" in header or "profit" in header:
        return "sales"
    elif "source" in header and "target" in header:
        return "network"
    else:
        raise HTTPException(status_code=400, detail=f"Unrecognized CSV schema: {header}")


# ------------- Unified evaluator endpoint -------------
@app.post("/")
async def analyze_unified(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file, suffix=".csv")
    try:
        dataset_type = _detect_dataset_type(path)

        if dataset_type == "weather":
            result = analyze_weather(path)
        elif dataset_type == "sales":
            result = analyze_sales(path)
        elif dataset_type == "network":
            result = analyze_network(path)
        else:
            raise HTTPException(status_code=400, detail="Could not determine dataset type.")

        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Handler must return a JSON dict.")

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
