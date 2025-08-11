from utils.wikipedia_loader import find_article, load_data

def handler(request: dict) -> dict:
    """
    Given an article, return other articles from the dataset that are linked from it.
    Query param: title=<exact article title>
    """
    # 1️⃣ Get the title param safely
    title_param = request["params"].get("title", "")
    if not isinstance(title_param, str) or not title_param.strip():
        return {"error": "Missing 'title' query parameter"}
    title_param = title_param.strip()

    # 2️⃣ Find the requested article
    article = find_article(title_param)
    if not article:
        return {"error": f"Article '{title_param}' not found"}

    # 3️⃣ Get that article's internal links
    link_titles = article.get("links", [])
    if not isinstance(link_titles, list) or not link_titles:
        return {
            "title": article.get("title", title_param),
            "related_count": 0,
            "related_articles": [],
            "note": "No related articles found for this article."
        }

    # 4️⃣ Build a lookup dictionary for quick matching
    data = load_data()
    article_lookup = {a.get("title", "").lower(): a for a in data if isinstance(a.get("title"), str)}

    related = []
    for linked_title in link_titles:
        candidate = article_lookup.get(linked_title.lower())
        if candidate:
            summary = candidate.get("summary", "")
            if isinstance(summary, str):
                preview = summary[:150].rsplit(" ", 1)[0] + "..." if summary else ""
            else:
                preview = ""
            related.append({
                "title": candidate.get("title", linked_title),
                "summary": preview
            })

    # 5️⃣ Return results
    return {
        "title": article.get("title", title_param),
        "related_count": len(related),
        "related_articles": related
    }
