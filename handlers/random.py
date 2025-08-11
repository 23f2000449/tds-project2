import random
from utils.wikipedia_loader import load_data

def handler(request: dict) -> dict:
    """
    Returns a random Wikipedia article from the dataset.
    No parameters required.
    """
    data = load_data()
    if not data:
        return {"error": "Dataset is empty"}

    article = random.choice(data)

    title = article.get("title", "Untitled Article")
    if not isinstance(title, str):
        title = str(title)

    summary = article.get("summary", "")
    if not isinstance(summary, str):
        summary = ""

    categories = article.get("categories", [])
    if not isinstance(categories, list):
        categories = []

    links = article.get("links", [])
    if not isinstance(links, list):
        links = []

    images = article.get("images", [])
    if not isinstance(images, list):
        images = []

    return {
        "title": title.strip(),
        "summary": summary.strip(),
        "categories": categories,
        "links": links,
        "images": images
    }
