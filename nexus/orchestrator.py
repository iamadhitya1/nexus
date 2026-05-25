from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from nexus.memory import SharedMemory
from nexus.agents.search import SearchAgent
from nexus.agents.reader import ReaderAgent
from nexus.agents.writer import WriterAgent
from nexus.agents.critic import CriticAgent

console = Console()


class Orchestrator:
    """
    The brain of Nexus. Takes a high-level goal and coordinates
    specialized agents to complete it autonomously.

    Pipeline:
        Goal → SearchAgent → ReaderAgent → WriterAgent → CriticAgent → Output
    """

    def __init__(self, model: str = "llama3", output_format: str = "report"):
        self.model = model
        self.output_format = output_format
        self.memory = SharedMemory()

        self.agents = {
            "search": SearchAgent(model=model),
            "reader": ReaderAgent(model=model),
            "writer": WriterAgent(model=model),
            "critic": CriticAgent(model=model),
        }

    def run(self, goal: str) -> str:
        console.print(Panel.fit(
            f"[bold white]{goal}[/bold white]",
            title="[bold magenta]NEXUS[/bold magenta]",
            subtitle="[dim]Multi-Agent System by Rewrite Labs[/dim]",
            border_style="magenta"
        ))

        # Step 1: Search
        console.rule("[cyan]Step 1 — Search[/cyan]")
        search_result = self.agents["search"].run(goal)
        self.memory.write("SearchAgent", search_result.output)
        urls = search_result.metadata.get("urls", [])

        # Step 2: Read
        console.rule("[cyan]Step 2 — Read & Extract[/cyan]")
        reader_result = self.agents["reader"].run({
            "goal": goal,
            "raw_search": search_result.output
        })
        self.memory.write("ReaderAgent", reader_result.output)

        # Step 3: Write
        console.rule("[cyan]Step 3 — Write[/cyan]")
        writer_result = self.agents["writer"].run({
            "goal": goal,
            "research": reader_result.output,
            "format": self.output_format
        })
        self.memory.write("WriterAgent", writer_result.output)

        # Step 4: Critique & Improve
        console.rule("[cyan]Step 4 — Critique & Improve[/cyan]")
        critic_result = self.agents["critic"].run({
            "goal": goal,
            "draft": writer_result.output
        })
        self.memory.write("CriticAgent", critic_result.output)

        final = critic_result.output
        console.rule("[bold green]Final Output[/bold green]")
        console.print(Markdown(final))

        return final
