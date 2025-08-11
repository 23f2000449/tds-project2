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

> **Note:** All data is served from `data/wikipedia.json` (no live Wikipedia calls).

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

Minimal `requirements.txt`:
```
fastapi==0.111.0
uvicorn==0.30.1
requests==2.32.3
```

---

## 🚀 Running the Server
From the project root:
```bash
python -m uvicorn main:myapp --reload
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

### Summary
```bash
GET /summary?title=Python%20(programming%20language)
```
Example Response:
```json
{
  "title": "Python (programming language)",
  "summary": "Python is an interpreted, high-level, general-purpose programming language..."
}
```

---

### Related
```bash
GET /related?title=Python%20(programming%20language)
```

---

### Top Categories
```bash
GET /top_categories?limit=5
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
│   ├── random.py
│   ├── related.py
│   ├── root.py
│   ├── search.py
│   ├── stats.py
│   ├── summary.py
│   ├── top_categories.py
│   └── __init__.py
│
├── utils/
│   ├── wikipedia_loader.py
│   ├── wikipedia_parser.py
│   └── __init__.py
```

---

## 📊 Dataset
- Small, rich subset of Wikipedia articles.
- Interconnected via `links` for `/related` functionality.
- Local only — **no internet required**.

---

## 📌 Extra Notes
- API designed for **no-internet grading environment**.
- Error handling ensures **valid JSON** for all responses.
- Modular **handler-based design** allows easy extension.

---

## 📝 Submission Instructions
For **grading**:
1. Push this project to a **public GitHub repository**.
2. Deploy the API to your preferred hosting (if required by grader).
3. Submit both:
   - **GitHub Repository Link**
   - **Deployed API Endpoint URL**
   
Submission Portal:  
[https://exam.sanand.workers.dev/tds-data-analyst-agent](https://exam.sanand.workers.dev/tds-data-analyst-agent)
