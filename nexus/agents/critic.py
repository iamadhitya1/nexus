from nexus.agent import BaseAgent, AgentResult


class CriticAgent(BaseAgent):
    """
    Reviews the writer's output, identifies weaknesses, and produces
    an improved final version. The last line of defence for quality.
    """

    def __init__(self, model: str = "llama3"):
        super().__init__(
            name="CriticAgent",
            role="You are a sharp editor and critic. You review content for accuracy, clarity, completeness, and quality. You rewrite and improve it to the highest standard.",
            model=model
        )

    def run(self, input: dict) -> AgentResult:
        goal = input.get("goal", "")
        draft = input.get("draft", "")

        self.log("Reviewing and improving draft...")

        critique_prompt = f"""Original goal: "{goal}"

Draft to review:
{draft}

First, identify 3-5 specific weaknesses or gaps in this draft.
Then, rewrite the FULL improved version that fixes all issues.

Format your response as:
CRITIQUE:
[your critique points]

IMPROVED VERSION:
[full rewritten content]"""

        response = self.think(critique_prompt, system=self.role)

        # Case-insensitive search for the improved version delimiter
        lower = response.lower()
        marker = "improved version:"
        idx = lower.rfind(marker)
        if idx != -1:
            final = response[idx + len(marker):].strip()
        else:
            # Fallback: strip everything before the last double-newline block
            # (usually the critique section) and return the rest
            parts = response.strip().split("\n\n")
            final = "\n\n".join(parts[1:]).strip() if len(parts) > 1 else response.strip()

        self.log("Final version ready")
        return AgentResult(
            agent=self.name,
            output=final,
            success=True,
            metadata={"word_count": len(final.split())}
        )
