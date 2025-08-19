from __future__ import annotations
import os
import tempfile
from typing import Any, Dict, Optional
import logging
import traceback
import sys

import matplotlib
matplotlib.use("Agg")  # headless backend for image generation

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

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

# Setup FastAPI app and logging
app = FastAPI(title="TDS Project – Data Analyst API")

logging.basicConfig(
    level=logging.DEBUG,  # DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Exception handler to catch request validation errors (e.g., missing file field)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Request validation error at {request.url}:\n{exc.errors()}")
    return await request_validation_exception_handler(request, exc)

# Global catch-all exception handler to log unexpected errors with stack trace
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception processing request {request.url}:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error occurred"},
    )

@app.get("/")
def root() -> Dict[str, Any]:
    logging.debug("Health check endpoint accessed")
    return {
        "service": "TDS Project – Data Analyst API",
        "status": "ok",
        "hint": "POST a CSV file to / with filename containing 'weather', 'sales', or 'network'."
    }

def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
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
    if func is None:
        extra = None
        if handler_name == "analyze_weather":
            extra = WEATHER_IMPORT_ERROR
        elif handler_name == "analyze_sales":
            extra = SALES_IMPORT_ERROR
        elif handler_name == "analyze_network":
            extra = NETWORK_IMPORT_ERROR
        logging.error(f"Handler {handler_name} unavailable: {extra}")
        raise HTTPException(status_code=500, detail=f"Handler {handler_name} unavailable: {extra}")

    try:
        result = func(csv_path)
        logging.debug(f"Handler {handler_name} returned keys: {list(result.keys())}")
        for k, v in result.items():
            if isinstance(v, str) and len(v) > 100:
                logging.debug(f"Key '{k}' is a large string with length {len(v)}")
            else:
                logging.debug(f"Key '{k}': {v} ({type(v)})")
        return result
    except Exception as exc:
        logging.error(f"Exception in handler {handler_name}: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Handler {handler_name} failed: {exc}")

@app.post("/")
async def analyze_csv(file: Optional[UploadFile] = File(None), request: Request = None) -> Dict[str, Any]:
    # Log all form fields to diagnose missing 'file' field issues
    if request is not None:
        form = await request.form()
        logging.debug(f"Received form fields: {list(form.keys())}")

    if file is None:
        logging.error("Missing file field in request")
        return JSONResponse(
            status_code=400,
            content={"detail": "Missing file field in request"},
        )

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
        logging.error(f"Filename '{filename}' does not contain required keywords")
        raise HTTPException(status_code=400, detail="Filename must contain 'weather', 'sales', or 'network'")

    csv_path = _save_upload_to_temp(file)

    try:
        result = _call_handler_or_500(handler_name, handler, csv_path)
    finally:
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
                logging.debug(f"Deleted temporary file {csv_path}")
            except Exception as e:
                logging.warning(f"Could not delete temp file {csv_path}: {e}")

    return JSONResponse(content=result)
