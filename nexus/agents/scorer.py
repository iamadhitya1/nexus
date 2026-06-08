from nexus.agent import BaseAgent


class ScorerAgent(BaseAgent):
    """
    Scores the WriterAgent's output 1-10 and returns one line of actionable feedback.
    Used by the Orchestrator's ReAct quality loop.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        super().__init__(
            name="ScorerAgent",
            role="You are a content quality evaluator. You score content objectively and give a single, specific, actionable improvement note.",
            model=model
        )

    def run(self, input: dict) -> tuple[float, str]:
        """Returns (score: float, feedback: str)."""
        goal   = input.get("goal", "")
        output = input.get("output", "")

        prompt = (
            f"Rate this content for the goal: \"{goal}\"\n\n"
            f"Content (first 1500 chars):\n{output[:1500]}\n\n"
            "Score 1-10 on: accuracy, depth, clarity, completeness.\n"
            "Reply in EXACTLY this two-line format:\n"
            "SCORE: <number>\n"
            "FEEDBACK: <one sentence on the single biggest weakness>"
        )

        response = self.think(prompt, system=self.role)

        score    = 7.0
        feedback = "No specific feedback."
        for line in response.strip().splitlines():
            upper = line.upper()
            if upper.startswith("SCORE:"):
                try:
                    score = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif upper.startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()

        self.log(f"Score: {score}/10 — {feedback}")
        return score, feedback
