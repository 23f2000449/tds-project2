# Wikipedia API – Project 2 (TDS)

## 📌 Overview
This project is a **local Wikipedia API** built with **FastAPI**.  
It serves information from a pre-loaded `wikipedia.json` dataset without requiring internet access.  

---

## 📚 Core Endpoints
- `/` – Project welcome/info
- `/search?q=keyword` – Search article titles (case-insensitive)
- `/summary?title=...` – Return summary of a specific article
- `/links?title=...` – List internal links from the article
- `/images?title=...` – List article image URLs
- `/categories?title=...` – List article categories
- `/stats` – Dataset-wide statistics

### 🌟 Bonus Endpoints
- `/random` – Return a random article
- `/related?title=...` – Articles linked from the given one
- `/top_categories?limit=N` – Most frequent categories

### 📊 Analysis Endpoints (New)
- `/analyze-weather` – Upload a weather CSV and analyze temperature/precipitation trends.
- `/analyze-network` – Analyze a social network graph from `edges.csv`.
- `/analyze-sales` – Analyze sales data from `sample-sales.csv`.

> **Note:** All data is served from local files (`data/wikipedia.json`, `sample-weather.csv`, `edges.csv`, `sample-sales.csv`) — no live API calls.

---

## 🛠 Installation

### 1. Clone or Extract Project
Extract this project folder locally, or clone from GitHub if applicable.

### 2. Python Version
Use **Python 3.8+**.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Server
From the project root:
```bash
uvicorn main:app --reload
```
Server will start at:  
```
http://127.0.0.1:8000/
```

---

## 🔍 Example Requests

### Root
```bash
GET /
```
Example:  
`http://127.0.0.1:8000/`

---

### Search
```bash
GET /search?q=python
```
Example Response:
```json
{
  "query": "python",
  "count": 1,
  "results": [
    {
      "title": "Python (programming language)",
      "summary": "Python is an interpreted high-level programming language for general-purpose programming..."
    }
  ]
}
```

---

### Analyze Weather
```bash
POST /analyze-weather
```
Upload `sample-weather.csv`.  
Example Response:
```json
{
  "average_temp_c": 21.5,
  "max_precip_date": "2025-01-04",
  "min_temp_c": 19.9,
  "temp_precip_correlation": -0.69,
  "average_precip_mm": 1.54,
  "temp_line_chart": "<base64 string>"
}
```

---

### Analyze Sales
```bash
POST /analyze-sales
```
Upload `sample-sales.csv`.  
Example Response:
```json
{
  "total_sales": 1690.0,
  "top_region": "West",
  "day_sales_correlation": -0.37,
  "bar_chart": "<base64 string>",
  "median_sales": 90.0,
  "total_sales_tax": 169.0,
  "cumulative_sales_chart": "<base64 string>"
}
```

---

### Analyze Network
```bash
POST /analyze-network
```
Uses `edges.csv`.  
Example Response:
```json
{
  "edge_count": 7,
  "highest_degree_node": "Bob",
  "average_degree": 2.8,
  "density": 0.7,
  "shortest_path_alice_eve": 2,
  "network_graph": "<base64 string>"
}
```

---

## 📂 Project Structure
```
project2/
├── config.py
├── main.py
├── requirements.txt
├── README.md
│
├── data/
│   └── wikipedia.json
│
├── handlers/
│   ├── categories.py
│   ├── images.py
│   ├── links.py
│   ├── network.py
│   ├── random.py
│   ├── related.py
│   ├── root.py
│   ├── sales.py
│   ├── search.py
│   ├── stats.py
│   ├── summary.py
│   ├── top_categories.py
│   ├── weather.py
│   └── __init__.py
│
├── utils/
│   ├── wikipedia_loader.py
│   ├── wikipedia_parser.py
│   └── __init__.py
│
├── sample-weather.csv
├── sample-sales.csv
├── edges.csv
```

---

## 📊 Dataset
- `data/wikipedia.json`: Wikipedia subset dataset
- `sample-weather.csv`: Example weather data
- `sample-sales.csv`: Example sales data
- `edges.csv`: Example social network

---

## 📌 Extra Notes
- API designed for **no-internet grading environment**.
- Error handling ensures **valid JSON** for all responses.
- Modular **handler-based design** allows easy extension.

---


