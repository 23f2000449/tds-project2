# main.py
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Import explicit handler functions
from handlers.weather import analyze_weather
from handlers.sales import analyze_sales
from handlers.network import analyze_network

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

def _save_upload(upload: UploadFile, suffix: str = ".csv") -> str:
    """Save uploaded file to a temporary file and return its path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.file.read())
            return tmp.name
    finally:
        try:
            upload.file.close()
        except Exception:
            pass

@app.post("/analyze-weather")
async def analyze_weather_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Upload must be a CSV file")
    path = _save_upload(file, suffix=".csv")
    try:
        result = analyze_weather(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)

@app.post("/analyze-sales")
async def analyze_sales_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Upload must be a CSV file")
    path = _save_upload(file, suffix=".csv")
    try:
        result = analyze_sales(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)

@app.post("/analyze-network")
async def analyze_network_endpoint(file: UploadFile = File(...)):
    if file.content_type and "csv" not in file.content_type:
        raise HTTPException(status_code=400, detail="Upload must be a CSV file")
    path = _save_upload(file, suffix=".csv")
    try:
        result = analyze_network(path)
        return JSONResponse(content=result)
    finally:
        os.remove(path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
