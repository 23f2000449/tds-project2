from utils.wikipedia_loader import load_data
from collections import Counter

def handler(request: dict) -> dict:
    """
    Returns dataset-wide statistics.
    No parameters required.
    """
    # 1️⃣ Load the whole dataset
    data = load_data()
    if not data:
        return {"error": "Dataset is empty"}

    # 2️⃣ Basic counts
    total_articles = len(data)

    # 3️⃣ Category, link, and image counts
    all_categories = []
    total_links = 0
    total_images = 0

    for article in data:
        cats = article.get("categories", [])
        if isinstance(cats, list):
            all_categories.extend(cats)
        links = article.get("links", [])
        if isinstance(links, list):
            total_links += len(links)
        images = article.get("images", [])
        if isinstance(images, list):
            total_images += len(images)

    category_counts = Counter(all_categories)
    if category_counts:
        most_common_category, freq = category_counts.most_common(1)[0]
    else:
        most_common_category, freq = None, 0

    # 4️⃣ Return stats
    return {
        "total_articles": total_articles,
        "unique_categories": len(category_counts),
        "most_common_category": most_common_category,
        "most_common_category_count": freq,
        "avg_links_per_article": round(total_links / total_articles, 2),
        "avg_images_per_article": round(total_images / total_articles, 2)
    }
