from utils.wikipedia_loader import load_data

def handler(request: dict) -> dict:
    # 1️⃣ Extract query param
    query = request["params"].get("q", "")
    if not isinstance(query, str) or not query.strip():
        return {"error": "Missing query parameter ?q="}
    query = query.strip().lower()

    # 2️⃣ Load dataset
    data = load_data()

    # 3️⃣ Search titles for the query
    matches = []
    for article in data:
        title = article.get("title", "")
        summary = article.get("summary", "")
        if not isinstance(title, str) or not isinstance(summary, str):
            continue
        if query in title.lower():
            preview = summary[:150].rsplit(" ", 1)[0] + "..." if summary else ""
            matches.append({
                "title": title,
                "summary": preview
            })

    # 4️⃣ Sort results so exact matches appear first
    matches.sort(key=lambda m: (m["title"].lower() != query, m["title"]))

    return {
        "query": query,
        "count": len(matches),
        "results": matches
    }
