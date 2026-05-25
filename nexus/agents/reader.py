from nexus.agent import BaseAgent, AgentResult
from nexus.tools.browser import read_url


class ReaderAgent(BaseAgent):
    """
    Visits URLs and extracts the most relevant information for a given goal.
    Acts as the research gatherer of the system.
    """

    def __init__(self, model: str = "llama3"):
        super().__init__(
            name="ReaderAgent",
            role="You are a research analyst. Read content and extract the most important facts, insights, and details relevant to a research goal.",
            model=model
        )

    def run(self, input: dict) -> AgentResult:
        goal = input.get("goal", "")
        urls = input.get("urls", [])

        self.log(f"Reading {len(urls)} sources...")
        all_knowledge = []

        for url in urls[:4]:
            self.log(f"Reading: {url}")
            content = read_url(url)
            if not content or "Could not read" in content:
                continue

            extract_prompt = f"""Research goal: "{goal}"

Page content:
{content}

Extract the most relevant facts, data, and insights from this page that help answer the research goal.
Be concise but thorough. Use bullet points."""

            extracted = self.think(extract_prompt, system=self.role)
            all_knowledge.append(f"Source: {url}\n{extracted}")

        combined = "\n\n---\n\n".join(all_knowledge)
        self.log(f"Extracted knowledge from {len(all_knowledge)} sources")

        return AgentResult(
            agent=self.name,
            output=combined,
            success=bool(all_knowledge),
            metadata={"sources_read": len(all_knowledge)}
        )
