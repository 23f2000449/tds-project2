# main.py
from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")  # headless backend for image generation

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
    """Health/info endpoint for GET /"""
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "hint": "POST a CSV file to / with filename containing 'weather', 'sales', or 'network'."
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


def _call_handler_or_500(handler_name: str, func: Optional[callable], csv_path: str) -> Dict[str, Any]:
    """Call handler safely; raise HTTP 500 if unavailable or failing."""
    if func is None:
        extra = None
        if handler_name == "analyze_weather":
            extra = WEATHER_IMPORT_ERROR
        elif handler_name == "analyze_sales":
            extra = SALES_IMPORT_ERROR
        elif handler_name == "analyze_network":
            extra = NETWORK_IMPORT
