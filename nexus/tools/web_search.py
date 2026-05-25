from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo. No API key required.
    Returns a list of results with title, url, and snippet.
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
    return results
