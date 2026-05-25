from nexus.agent import BaseAgent, AgentResult


class WriterAgent(BaseAgent):
    """
    Takes gathered research and writes a polished, structured output.
    Adapts tone and format based on the task type.
    """

    def __init__(self, model: str = "llama3"):
        super().__init__(
            name="WriterAgent",
            role="You are an expert writer. You craft clear, engaging, well-structured content from raw research. You adapt your style to the requested output format.",
            model=model
        )

    def run(self, input: dict) -> AgentResult:
        goal = input.get("goal", "")
        research = input.get("research", "")
        output_format = input.get("format", "report")

        self.log(f"Writing {output_format}...")

        format_instructions = {
            "report": "Write a detailed research report with sections: Executive Summary, Key Findings, Analysis, and Conclusion.",
            "blog": "Write an engaging blog post with a hook, subheadings, and a clear conclusion.",
            "summary": "Write a concise executive summary in bullet points followed by 2-3 paragraphs.",
            "essay": "Write a structured essay with introduction, body paragraphs, and conclusion."
        }

        instruction = format_instructions.get(output_format, format_instructions["report"])

        prompt = f"""Goal: "{goal}"

Research gathered:
{research}

{instruction}

Write the full {output_format} now. Make it thorough and well-structured."""

        output = self.think(prompt, system=self.role)
        self.log("Draft complete")

        return AgentResult(
            agent=self.name,
            output=output,
            success=True,
            metadata={"format": output_format, "word_count": len(output.split())}
        )
