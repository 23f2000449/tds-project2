from utils.wikipedia_loader import find_article
from utils.wikipedia_parser import get_categories

def handler(request: dict) -> dict:
    """
    Returns the categories for a given article title.
    Query param: title=<exact article title>
    """
    # 1️⃣ Extract query param safely
    title_param = request["params"].get("title", "")
    if not isinstance(title_param, str) or not title_param.strip():
        return {"error": "Missing 'title' query parameter"}
    title_param = title_param.strip()

    # 2️⃣ Look up article in dataset
    article = find_article(title_param)
    if not article:
        return {"error": f"Article '{title_param}' not found"}

    # 3️⃣ Fetch categories from the article
    categories = get_categories(article)
    if not categories:
        return {
            "title": article.get("title", title_param),
            "categories": [],
            "note": "No categories available for this article."
        }

    # 4️⃣ Return JSON response (with real dataset title)
    return {"title": article.get("title", title_param), "categories": categories}
