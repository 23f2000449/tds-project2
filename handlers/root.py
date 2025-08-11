def handler(request: dict) -> dict:
    """
    Root endpoint handler.
    Returns a welcome message and available endpoints.
    """
    try:
        return {
            "message": "Welcome to the Wikipedia API Project",
            "version": "1.0",
            "available_endpoints": [
                "/search?q=<keyword>",
                "/summary?title=<article_title>",
                "/links?title=<article_title>",
                "/images?title=<article_title>",
                "/categories?title=<article_title>",
                "/stats",
                "/random",          # optional
                "/related?title=<article_title>",  # optional
                "/top_categories"   # optional
            ],
            "note": "All endpoints are relative to the base API URL."
        }
    except Exception as e:
        return {"error": f"Unexpected error in root handler: {str(e)}"}
