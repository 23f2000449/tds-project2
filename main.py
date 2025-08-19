from __future__ import annotations
import os
import tempfile
from typing import Any, Dict, Optional
import logging
import matplotlib
matplotlib.use("Agg")  # headless backend for image generation
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# --- Import handlers with error handling ---
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

# Setup FastAPI app and detailed logging
app = FastAPI(title="TDS Project – Data Analyst Agent API")
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

@app.get("/")
def root() -> Dict[str, Any]:
    """Health/info endpoint for GET /"""
    logging.debug("Health check endpoint accessed")
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "hint": "POST a CSV file to / with filename containing 'weather', 'sales', or 'network'."
    }

def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    """Save UploadFile to a temporary file and return its path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            data = upload.file.read()
            tmp.write(data)
            logging.debug(f"Saved upload to temp file {tmp.name} ({len(data)} bytes)")
            return tmp.name
    finally:
        try:
            upload.file.close()
        except Exception as e:
            logging.warning(f"Failed to close upload file: {e}")

def _call_handler_or_500(handler_name: str, func: Optional[callable], csv_path: str) -> Dict[str, Any]:
    """Call handler safely; raise HTTP 500 if handler unavailable or raises exception."""
    if func is None:
        extra = None
        if handler_name == "analyze_weather":
            extra = WEATHER_IMPORT_ERROR
        elif handler_name == "analyze_sales":
            extra = SALES_IMPORT_ERROR
        elif handler_name == "analyze_network":
            extra = NETWORK_IMPORT_ERROR
        logging.error(f"Handler unavailable: {handler_name}, error: {extra}")
        raise HTTPException(status_code=500, detail=f"Handler unavailable: {handler_name}, error: {extra}")
    try:
        result = func(csv_path)
        logging.debug(f"Handler {handler_name} returned result with keys: {list(result.keys())}")
        # Additional debug: log length and type of each value
        for k, v in result.items():
            if isinstance(v, str) and len(v) > 100:
                logging.debug(f"Result key '{k}' value is a str of length {len(v)}")
            else:
                logging.debug(f"Result key '{k}' value type: {type(v)}, value: {v}")
        return result
    except Exception as exc:
        logging.exception(f"Handler {handler_name} failed with exception")
        raise HTTPException(status_code=500, detail=f"Handler {handler_name} failed with error: {exc}")

@app.post("/")
async def analyze_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    filename = file.filename.lower()
    content_type = file.content_type
    logging.info(f"Received file: filename={filename}, content_type={content_type}")

    if "weather" in filename:
        handler = analyze_weather
        handler_name = "analyze_weather"
    elif "sales" in filename:
        handler = analyze_sales
        handler_name = "analyze_sales"
    elif "network" in filename:
        handler = analyze_network
        handler_name = "analyze_network"
    else:
        logging.error("File name does not contain required keywords")
        raise HTTPException(status_code=400, detail="Filename must contain 'weather', 'sales', or 'network'")

    csv_path = _save_upload_to_temp(file)

    try:
        result = _call_handler_or_500(handler_name, handler, csv_path)
    finally:
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
                logging.debug(f"Temporary file {csv_path} deleted")
            except Exception as e:
                logging.warning(f"Failed to delete temp file {csv_path}: {e}")

    return JSONResponse(content=result)
