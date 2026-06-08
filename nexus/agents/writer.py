from nexus.agent import BaseAgent, AgentResult


FORMAT_INSTRUCTIONS = {
    "report":      "Write a detailed research report with: Executive Summary, Key Findings, In-Depth Analysis, and Conclusion.",
    "blog":        "Write an engaging blog post with a compelling hook, 4-6 subheadings, and a memorable conclusion. Conversational but expert tone.",
    "summary":     "Write a concise executive summary: 5-7 bullet-point highlights first, then 2-3 tight paragraphs.",
    "essay":       "Write a structured essay with a clear thesis introduction, 3-4 substantive body paragraphs, and a strong conclusion.",
    "tweet-thread": "Write a tweet thread of 8-12 tweets. Hook tweet first, number each tweet (1/N), back each claim with a fact, end with a CTA. Max 280 chars each.",
    "linkedin":    "Write a LinkedIn post: bold hook as first line (no hashtag), 4-6 short paragraphs with line breaks, 3-5 relevant hashtags at the very end.",
    "newsletter":  "Write a newsletter edition: subject line on line 1, short greeting, 3-4 story sections with headers, a key takeaway box (use '>'), and a CTA.",
    "slides":      "Write slide-by-slide content. Format each slide as '## Slide N: Title' followed by 3-5 bullet points. 8-12 slides total.",
}


class WriterAgent(BaseAgent):
    """
    Writes polished, format-specific content from research.
    Supports revision via feedback from the ScorerAgent (ReAct loop).
    Supports streaming via stream_run().
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        super().__init__(
            name="WriterAgent",
            role="You are an expert writer. You craft clear, engaging, well-structured content from raw research. You adapt your style and format precisely to the requested output type.",
            model=model
        )

    def _build_prompt(self, goal: str, research: str, output_format: str,
                      feedback: str = None, previous_attempt: str = None) -> str:
        instruction = FORMAT_INSTRUCTIONS.get(output_format, FORMAT_INSTRUCTIONS["report"])

        revision_block = ""
        if feedback and previous_attempt:
            revision_block = (
                f"\nA previous draft received this feedback: \"{feedback}\"\n"
                "Fix that specific weakness. Make it measurably better — don't just rewrite.\n"
            )

        return (
            f"Goal: \"{goal}\"\n\n"
            f"Research:\n{research}\n"
            f"{revision_block}\n"
            f"{instruction}\n\n"
            f"Write the full {output_format} now. Make it thorough and polished."
        )

    def run(self, input: dict) -> AgentResult:
        goal             = input.get("goal", "")
        research         = input.get("research", "")
        output_format    = input.get("format", "report")
        feedback         = input.get("feedback")
        previous_attempt = input.get("previous_attempt")

        self.log(f"Writing {output_format}...")
        prompt = self._build_prompt(goal, research, output_format, feedback, previous_attempt)
        output = self.think(prompt, system=self.role)
        self.log("Draft complete")

        return AgentResult(
            agent=self.name,
            output=output,
            success=bool(output.strip()),
            metadata={"format": output_format, "word_count": len(output.split())}
        )

    def stream_run(self, input: dict):
        """Generator — yields string tokens as they arrive from the LLM."""
        goal             = input.get("goal", "")
        research         = input.get("research", "")
        output_format    = input.get("format", "report")
        feedback         = input.get("feedback")
        previous_attempt = input.get("previous_attempt")

        self.log(f"Writing {output_format} (streaming)...")
        prompt = self._build_prompt(goal, research, output_format, feedback, previous_attempt)
        yield from self.stream_think(prompt, system=self.role)
        self.log("Draft complete")
