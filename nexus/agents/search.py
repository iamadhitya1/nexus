from nexus.agent import BaseAgent, AgentResult
from nexus.tools.web_search import search_web


class SearchAgent(BaseAgent):
    """
    Searches the web for relevant information given a query.
    Returns a list of URLs and snippets for the Reader agent to process.
    """

    def __init__(self, model: str = "llama3"):
        super().__init__(
            name="SearchAgent",
            role="You are a search specialist. Given a research goal, generate the best search queries and find the most relevant sources.",
            model=model
        )

    def run(self, goal: str) -> AgentResult:
        self.log(f"Finding sources for: '{goal}'")

        query_prompt = f"""Given this research goal: "{goal}"
Generate 2 specific, targeted search queries to find the best information.
Return ONLY the queries, one per line, nothing else."""

        queries_raw = self.think(query_prompt, system=self.role)
        # Strip numbering, bullets, and extra text the LLM might add
        lines = [q.strip() for q in queries_raw.strip().split("\n") if q.strip()]
        queries = []
        for line in lines:
            # Remove common prefixes like "1.", "2.", "-", "*"
            clean = line.lstrip("0123456789.-* ").strip()
            # Skip lines that are clearly meta-text, not queries
            if clean and len(clean) > 5 and not clean.lower().startswith("here are"):
                queries.append(clean)
        queries = queries[:2]

        all_results = []
        for query in queries:
            self.log(f"Searching: {query}")
            results = search_web(query, max_results=4)
            all_results.extend(results)

        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)

        output = "\n\n".join([
            f"[{r['title']}]\nURL: {r['url']}\n{r['snippet']}"
            for r in unique_results[:6]
        ])

        self.log(f"Found {len(unique_results)} sources")
        return AgentResult(
            agent=self.name,
            output=output,
            success=True,
            metadata={"urls": [r["url"] for r in unique_results[:6]]}
        )
