from utils.wikipedia_loader import find_article
from utils.wikipedia_parser import get_links

def handler(request: dict) -> dict:
    """
    Returns the internal Wikipedia links for a given article title.
    Query param: title=<exact article title>
    """
    # 1️⃣ Get the 'title' parameter safely
    title_param = request["params"].get("title", "")
    if not isinstance(title_param, str) or not title_param.strip():
        return {"error": "Missing 'title' query parameter"}
    title_param = title_param.strip()

    # 2️⃣ Find the article
    article = find_article(title_param)
    if not article:
        return {"error": f"Article '{title_param}' not found"}

    # 3️⃣ Get article links
    links = get_links(article)
    if not links:
        return {
            "title": article.get("title", title_param),
            "links": [],
            "note": "No internal links available for this article."
        }

    # 4️⃣ Return result (with real dataset title)
    return {"title": article.get("title", title_param), "links": links}
