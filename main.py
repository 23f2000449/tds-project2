# main.py
from __future__ import annotations

import os
import tempfile
import base64
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")  # headless backend for image generation

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# --- Import handler callables if available ---
# Weather handler is already known to be a function that accepts a CSV path and returns a dict.
try:
    from handlers.weather import analyze_weather as _analyze_weather_file
except Exception as e:
    _analyze_weather_file = None  # type: ignore
    WEATHER_IMPORT_ERROR = e
else:
    WEATHER_IMPORT_ERROR = None

# Sales: try both a function and a router (don’t fail if missing)
_analyze_sales_file: Optional[callable] = None
SALES_IMPORT_ERROR: Optional[Exception] = None
try:
    from handlers.sales import analyze_sales as _analyze_sales_file  # type: ignore
except Exception as e:
    SALES_IMPORT_ERROR = e
    _analyze_sales_file = None

_sales_router = None
try:
    from handlers import sales as _sales_module
    _sales_router = getattr(_sales_module, "router", None)
except Exception:
    _sales_router = None

# Network: try both a function and a router (don’t fail if missing)
_analyze_network_file: Optional[callable] = None
NETWORK_IMPORT_ERROR: Optional[Exception] = None
try:
    from handlers.network import analyze_network as _analyze_network_file  # type: ignore
except Exception as e:
    NETWORK_IMPORT_ERROR = e
    _analyze_network_file = None

_network_router = None
try:
    from handlers.network import router as _network_router  # type: ignore
except Exception:
    _network_router = None


# ------------------------ FastAPI app ------------------------
app = FastAPI(title="TDS Project – Data Analyst Agent API")


@app.get("/")
def root() -> Dict[str, Any]:
    """
    Lightweight health/info endpoint.
    Keep it minimal so the evaluator won’t mistake this for task output.
    """
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "endpoints": [
            "POST /analyze-weather",
            "POST /analyze-sales",
            "POST /analyze-network",
        ],
    }


# ------------- Helpers -------------
def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    """
    Save an UploadFile to a NamedTemporaryFile and return the path.
    The caller is responsible for os.remove(path).
    """
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
    """
    Call a handler function with csv_path; convert exceptions to HTTP 500.
    """
    if func is None:
        # Provide clearer error if import failed
        extra = None
        if handler_name == "analyze_weather":
            extra = WEATHER_IMPORT_ERROR
        elif handler_name == "analyze_sales":
            extra = SALES_IMPORT_ERROR
        elif handler_name == "analyze_network":
            extra = NETWORK_IMPORT_ERROR

        msg = f"Handler '{handler_name}' is not available."
        if extra:
            msg += f" Import error: {extra}"
        raise HTTPException(status_code=500, detail=msg)

    try:
        out = func(csv_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{handler_name} failed: {e}")

    if not isinstance(out, dict):
        raise HTTPException(status_code=500, detail=f"{handler_name} must return a dict JSON object.")
    return out


# ------------- Required evaluator endpoints -------------
@app.post("/analyze-weather")
async def analyze_weather_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """
    Evaluator posts a CSV as 'file'.
    Your handlers.weather.analyze_weather must:
      - read the CSV via the provided path
      - return a dict with EXACT keys expected by the rubric:
        average_temp_c, max_precip_date, min_temp_c,
        temp_precip_correlation, average_precip_mm,
        temp_line_chart, precip_histogram
      - images must be base64-encoded PNG strings (no data: prefix), ideally <100kB
    """
    if file.content_type and "csv" not in file.content_type:
        # Be tolerant: some runners omit content-type; only reject explicit non-CSV
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file, suffix=".csv")
    try:
        result = _call_handler_or_500("analyze_weather", _analyze_weather_file, path)
        return JSONResponse(content=result)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@app.post("/analyze-sales")
async def analyze_sales_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """
    Evaluator posts a CSV as 'file'.
    handlers.sales.analyze_sales should return a dict JSON object per the sales rubric.
    """
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file, suffix=".csv")
    try:
        result = _call_handler_or_500("analyze_sales", _analyze_sales_file, path)
        return JSONResponse(content=result)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@app.post("/analyze-network")
async def analyze_network_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """
    Evaluator posts a CSV as 'file'.
    handlers.network.analyze_network should return a dict JSON object per the network rubric.
    """
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    path = _save_upload_to_temp(file, suffix=".csv")
    try:
        result = _call_handler_or_500("analyze_network", _analyze_network_file, path)
        return JSONResponse(content=result)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


# ------------- Optional: mount routers if present -------------
# These do not affect the evaluator, but let you keep any extra routes you already built.
if _sales_router is not None:
    app.include_router(_sales_router, tags=["sales"])

if _network_router is not None:
    app.include_router(_network_router, tags=["network"])


# ------------- Local run -------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
