# warmup.py
import requests

BASE_URL = "https://tds-project2-wikipedia-api.up.railway.app"

ENDPOINTS = [
    "/", 
    "/search?q=Python", 
    "/summary?title=Python%20(programming%20language)",
    "/links?title=Python%20(programming%20language)",
    "/images?title=Python%20(programming%20language)",
    "/categories?title=Python%20(programming%20language)",
    "/stats",
    "/random",
    "/related?title=Python%20(programming%20language)",
    "/top_categories?limit=5"
]

for ep in ENDPOINTS:
    try:
        r = requests.get(BASE_URL + ep, timeout=10)
        print(f"[{r.status_code}] {ep} -> {r.elapsed.total_seconds():.2f}s")
    except Exception as e:
        print(f"[ERROR] {ep} -> {e}")
