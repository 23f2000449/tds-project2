from utils.wikipedia_loader import load_data
from collections import Counter

def handler(request: dict) -> dict:
    """
    Returns the top N most frequent categories across the dataset.
    Optional query param: limit=<number> (defaults to 10)
    """
    # 1️⃣ Get limit from query (default 10 if not provided or invalid)
    limit_param = request["params"].get("limit", "").strip()
    try:
        limit = int(limit_param) if limit_param else 10
        if limit <= 0:
            return {"error": "Limit must be a positive integer"}
    except ValueError:
        limit = 10

    # 2️⃣ Load dataset
    data = load_data()
    if not data:
        return {"error": "Dataset is empty"}

    # 3️⃣ Collect all categories safely
    all_categories = []
    for article in data:
        cats = article.get("categories", [])
        if isinstance(cats, list):
            all_categories.extend(cats)

    if not all_categories:
        return {"error": "No categories found in dataset"}

    # 4️⃣ Count frequencies & get top N
    category_counts = Counter(all_categories)
    top_n = category_counts.most_common(limit)

    # 5️⃣ Format results
    return {
        "limit": limit,
        "total_unique_categories": len(category_counts),
        "top_categories": [
            {"category": cat, "count": count} for cat, count in top_n
        ]
    }
