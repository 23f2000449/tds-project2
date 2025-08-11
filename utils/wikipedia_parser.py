def get_summary(article):
    """Return the summary as a clean string."""
    summary = article.get("summary", "")
    if not isinstance(summary, str):
        return ""
    return summary.strip()

def get_links(article):
    """Return a list of internal links."""
    links = article.get("links", [])
    return links if isinstance(links, list) else []

def get_images(article):
    """Return a list of image URLs."""
    images = article.get("images", [])
    return images if isinstance(images, list) else []

def get_categories(article):
    """Return a list of categories."""
    categories = article.get("categories", [])
    return categories if isinstance(categories, list) else []
