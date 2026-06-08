from ddgs import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo. No API key required.
    Returns a list of results with title, url, and snippet.
    Raises RuntimeError if the search fails.
    """
    results = []
    try:
        ddgs = DDGS()
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
    except Exception as e:
        raise RuntimeError(f"Web search failed for query '{query}': {e}") from e
    return results
