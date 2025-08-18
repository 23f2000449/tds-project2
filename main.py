# main.py
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import matplotlib
matplotlib.use("Agg")  # headless backend for image generation

# Import your handlers directly
from handlers.weather import analyze_weather
from handlers.sales import analyze_sales
from handlers.network import analyze_network_from_path

app = FastAPI(title="TDS Project – Data Analyst Agent API")

@app.get("/")
def root():
    return {
        "service": "TDS Project – Data Analyst Agent API",
        "status": "ok",
        "endpoints": [
            "POST /analyze-weather",
            "POST /analyze-sales",
            "POST /analyze-network",
        ],
    }


def _save_upload_to_temp(upload: UploadFile, suffix: str = ".csv") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(upload.file.read())
        return tmp.name


@app.post("/analyze-weather")
async def analyze_weather_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    path = _save_upload_to_temp(file)
    try:
        result = analyze_weather(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)


@app.post("/analyze-sales")
async def analyze_sales_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    # Here we just pass the UploadFile directly since your sales handler consumes file.file
    result = await analyze_sales(file)
    return JSONResponse(content=result)


@app.post("/analyze-network")
async def analyze_network_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    path = _save_upload_to_temp(file)
    try:
        result = analyze_network_from_path(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
