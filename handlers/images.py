from utils.wikipedia_loader import find_article
from utils.wikipedia_parser import get_images

def handler(request: dict) -> dict:
    """
    Returns the image URLs for a given article title.
    Query param: title=<exact article title>
    """
    # 1️⃣ Get 'title' parameter safely
    title_param = request["params"].get("title", "")
    if not isinstance(title_param, str) or not title_param.strip():
        return {"error": "Missing 'title' query parameter"}
    title_param = title_param.strip()

    # 2️⃣ Find the article in dataset
    article = find_article(title_param)
    if not article:
        return {"error": f"Article '{title_param}' not found"}

    # 3️⃣ Extract images
    images = get_images(article)
    if not images:
        return {
            "title": article.get("title", title_param),
            "images": [],
            "note": "No images available for this article."
        }

    # 4️⃣ Return response (with real dataset title)
    return {"title": article.get("title", title_param), "images": images}
