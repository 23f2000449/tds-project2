from utils.wikipedia_loader import find_article
from utils.wikipedia_parser import get_summary

def handler(request: dict) -> dict:
    """
    Returns the summary for a given article title.
    Query param: title=<exact article title>
    """
    # 1️⃣ Get the 'title' parameter from query
    title_param = request["params"].get("title", "")
    if not isinstance(title_param, str) or not title_param.strip():
        return {"error": "Missing 'title' query parameter"}
    title_param = title_param.strip()

    # 2️⃣ Find the matching article from the dataset
    article = find_article(title_param)
    if not article:
        return {"error": f"Article '{title_param}' not found"}

    # 3️⃣ Get the summary for that article
    summary = get_summary(article)
    if not summary:
        summary = "No summary available for this article."

    # 4️⃣ Return result (with actual dataset title)
    return {"title": article.get("title", title_param), "summary": summary}
