import json
from config import DATA_PATH

# Simple in-memory cache
_cached_data = None

def load_data():
    global _cached_data
    if _cached_data is not None:
        return _cached_data
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _cached_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at {DATA_PATH}")
        _cached_data = []
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON format in {DATA_PATH}")
        _cached_data = []
    return _cached_data

def find_article(title):
    """Finds an article by title (case-insensitive, trims spaces)."""
    if not title:
        return None
    data = load_data()
    title = title.strip().lower()
    for article in data:
        if article.get("title", "").strip().lower() == title:
            return article
    return None
