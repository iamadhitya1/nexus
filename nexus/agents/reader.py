from nexus.agent import BaseAgent, AgentResult


class ReaderAgent(BaseAgent):
    """
    Synthesises search snippets into structured knowledge for a given goal.
    Fast mode: uses snippets directly instead of slow browser visits.
    """

    def __init__(self, model: str = "llama3"):
        super().__init__(
            name="ReaderAgent",
            role="You are a research analyst. Extract and synthesise the most important facts, insights, and details relevant to a research goal.",
            model=model
        )

    def run(self, input: dict) -> AgentResult:
        goal = input.get("goal", "")
        raw_search = input.get("raw_search", "")

        self.log("Synthesising search results...")

        extract_prompt = f"""Research goal: "{goal}"

Search results:
{raw_search}

Extract and organise the most relevant facts, frameworks, tools, and insights.
Use bullet points grouped by theme. Be thorough."""

        extracted = self.think(extract_prompt, system=self.role)
        self.log("Knowledge extracted")

        return AgentResult(
            agent=self.name,
            output=extracted,
            success=bool(extracted),
            metadata={"sources_read": raw_search.count("URL:")}
        )
