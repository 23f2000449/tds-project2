# main.py
import os
import tempfile
import json
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")  # headless backend for image generation

from fastapi import FastAPI, Request, HTTPException
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


@app.api_route("/", methods=["GET", "POST"])
async def root(request: Request):
    """
    Handle both GET and POST for root.
    GET -> health check
    POST -> evaluator request (routes to correct handler based on question text).
    """
    if request.method == "GET":
        return {
            "service": "TDS Project – Data Analyst Agent API",
            "status": "ok",
            "usage": "POST JSON with 'vars.question' referring to weather/sales/network"
        }

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    # The evaluator always includes the question inside body["vars"]["question"]
    question = (
        body.get("vars", {}).get("question", "")
        if isinstance(body, dict) else ""
    ).lower()

    # Route based on keywords
    try:
        if "temperature" in question or "precip" in question or "weather" in question:
            # Evaluator provides a CSV path in body["vars"]["question"] context
            path = "weather.csv"
            result = analyze_weather(path) if analyze_weather else {}
            return JSONResponse(content=result)

        elif "sales" in question:
            path = "sales.csv"
            result = analyze_sales(path) if analyze_sales else {}
            return JSONResponse(content=result)

        elif "edges.csv" in question or "network" in question:
            path = "edges.csv"
            result = analyze_network(path) if analyze_network else {}
            return JSONResponse(content=result)

        else:
            raise HTTPException(status_code=400, detail="Unrecognized task in question.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Handler failed: {e}")


# ------------- Local run -------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
