# main.py
from __future__ import annotations
import os
import tempfile
from typing import Any, Dict, Optional
import logging
import traceback
import sys
import csv

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

app = FastAPI(title="TDS Project – Data Analyst API")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Request validation error at {request.url}:\n{exc.errors()}")
    return await request_validation_exception_handler(request, exc)

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

def _validate_csv_headers(csv_path: str, required_columns: set[str]) -> Optional[str]:
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            headers_set = set(h.lower() for h in headers)
            if not required_columns.issubset(headers_set):
                return f"CSV missing required columns: {required_columns - headers_set}"
    except Exception as e:
        return f"Failed to read CSV headers: {e}"
    return None

@app.post("/")
async def analyze_csv(request: Request):
    form = await request.form()
    logging.info(f"Received form fields: {list(form.keys())}")

    upload_file = None
    upload_key = None

    # Find CSV file with expected keywords including "edges" mapped to network
    for key, value in form.items():
        if hasattr(value, "filename") and value.filename and value.filename.lower().endswith(".csv"):
            fname = value.filename.lower()
            if any(keyword in fname for keyword in ["network", "edges", "sales", "weather"]):
                upload_file = value
                upload_key = key
                break

    if not upload_file:
        logging.error("No CSV file found with 'network', 'edges', 'sales', or 'weather' in filename")
        return JSONResponse(
            status_code=400,
            content={"detail": "No CSV file found with 'network', 'edges', 'sales', or 'weather' in filename."},
        )

    logging.info(f"Using uploaded file from field '{upload_key}': {upload_file.filename}")
    filename = upload_file.filename.lower()

    if any(keyword in filename for keyword in ["network", "edges"]):
        handler = analyze_network
        handler_name = "analyze_network"
        required_cols = {"source", "target"}  # adjust if your network handler requires specific columns
    elif "sales" in filename:
        handler = analyze_sales
        handler_name = "analyze_sales"
        required_cols = {"sales", "region", "date"}
    elif "weather" in filename:
        handler = analyze_weather
        handler_name = "analyze_weather"
        required_cols = {"precip_mm", "temp_c", "date"}
    else:
        logging.error(f"Filename '{filename}' does not contain required keywords after selection")
        return JSONResponse(status_code=400, content={"detail": "Filename must contain 'network', 'edges', 'sales', or 'weather'."})

    csv_path = _save_upload_to_temp(upload_file)
    with open(csv_path, 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
    logging.debug(f"CSV header line in '{upload_file.filename}': {header_line}")


    val_error = _validate_csv_headers(csv_path, required_cols)
    if val_error:
        logging.error(val_error)
        try:
            os.remove(csv_path)
        except Exception:
            pass
        return JSONResponse(status_code=400, content={"detail": val_error})

    try:
        result = _call_handler_or_500(handler_name, handler, csv_path)
    finally:
        try:
            os.remove(csv_path)
            logging.debug(f"Deleted temporary file {csv_path}")
        except Exception as e:
            logging.warning(f"Could not delete temp file {csv_path}: {e}")

    return JSONResponse(content=result)
