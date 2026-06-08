from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from nexus.agent import AgentResult
from nexus.memory import SharedMemory
from nexus.agents.search import SearchAgent
from nexus.agents.reader import ReaderAgent
from nexus.agents.writer import WriterAgent
from nexus.agents.critic import CriticAgent
from nexus.agents.scorer import ScorerAgent

console = Console()

MAX_RETRIES     = 2      # max writer revision attempts
SCORE_THRESHOLD = 7.0    # minimum quality score before skipping revision


class Orchestrator:
    """
    Coordinates the Nexus multi-agent pipeline:
        Goal → Search → Read → Write (ReAct loop) → Critique → Output

    Supports two modes:
      - CLI mode  (on_event=None):  Rich console output + live token streaming to stdout.
      - API mode  (on_event=fn):    Silent — emits structured events via callback for SSE.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile", output_format: str = "report"):
        self.model         = model
        self.output_format = output_format
        self.memory        = SharedMemory()
        self.agents        = {
            "search":  SearchAgent(model=model),
            "reader":  ReaderAgent(model=model),
            "writer":  WriterAgent(model=model),
            "critic":  CriticAgent(model=model),
            "scorer":  ScorerAgent(model=model),
        }

    def run(self, goal: str, on_event=None) -> str:
        is_api = on_event is not None

        # ── Reset state ───────────────────────────────────────────────────────
        for agent in self.agents.values():
            agent.clear_memory()
        self.memory.clear()

        def emit(event: dict):
            if is_api:
                on_event(event)

        def rule(title: str):
            if not is_api:
                console.rule(title)

        # ── Header ────────────────────────────────────────────────────────────
        if not is_api:
            console.print(Panel.fit(
                f"[bold white]{goal}[/bold white]",
                title="[bold magenta]NEXUS[/bold magenta]",
                subtitle="[dim]Multi-Agent System · Rewrite Labs[/dim]",
                border_style="magenta"
            ))

        # ── Step 1: Search ────────────────────────────────────────────────────
        rule("[cyan]Step 1 — Search[/cyan]")
        emit({"type": "step", "step": "search", "status": "running"})

        search_result = self.agents["search"].run(goal)
        if not search_result.success:
            emit({"type": "step", "step": "search", "status": "error", "error": search_result.error})
            if not is_api:
                console.print(f"[bold red]SearchAgent failed:[/bold red] {search_result.error}")
            return ""

        self.memory.write("SearchAgent", search_result.output)
        urls = search_result.metadata.get("urls", [])
        emit({"type": "step", "step": "search", "status": "done",
              "info": f"{len(urls)} sources found", "urls": urls})

        # ── Step 2: Read ──────────────────────────────────────────────────────
        rule("[cyan]Step 2 — Read & Extract[/cyan]")
        emit({"type": "step", "step": "read", "status": "running"})

        reader_result = self.agents["reader"].run({
            "goal":       goal,
            "raw_search": search_result.output,
        })
        if not reader_result.success:
            emit({"type": "step", "step": "read", "status": "error", "error": reader_result.error})
            if not is_api:
                console.print(f"[bold red]ReaderAgent failed:[/bold red] {reader_result.error}")
            return ""

        self.memory.write("ReaderAgent", reader_result.output)
        emit({"type": "step", "step": "read", "status": "done",
              "info": f"{reader_result.metadata.get('sources_read', 0)} sources synthesised"})

        # ── Step 3: Write  +  ReAct quality loop ─────────────────────────────
        rule("[cyan]Step 3 — Write[/cyan]")

        write_input   = {"goal": goal, "research": reader_result.output, "format": self.output_format}
        writer_result = None
        final_score   = None

        for attempt in range(MAX_RETRIES + 1):
            emit({"type": "step", "step": "write", "status": "running", "attempt": attempt + 1})

            if not is_api and attempt > 0:
                console.rule(f"[cyan]Step 3 — Write (revision {attempt})[/cyan]")

            # Stream writer output
            full_writer_output = ""
            emit({"type": "streaming_start", "agent": "writer"})

            for token in self.agents["writer"].stream_run(write_input):
                full_writer_output += token
                emit({"type": "token", "content": token})
                if not is_api:
                    print(token, end="", flush=True)

            if not is_api:
                print()  # newline after stream
            emit({"type": "streaming_end"})

            writer_result = AgentResult(
                agent="WriterAgent",
                output=full_writer_output,
                success=bool(full_writer_output.strip()),
                metadata={"format": self.output_format, "word_count": len(full_writer_output.split())}
            )

            if not writer_result.success:
                emit({"type": "step", "step": "write", "status": "error",
                      "error": "Writer produced empty output"})
                return ""

            # Score — skip on last attempt to avoid a wasted LLM call
            if attempt < MAX_RETRIES:
                score, feedback = self.agents["scorer"].run({
                    "goal":   goal,
                    "output": full_writer_output,
                })
                final_score = score
                emit({"type": "quality", "score": score, "attempt": attempt + 1, "feedback": feedback})

                if not is_api:
                    colour = "green" if score >= SCORE_THRESHOLD else "yellow"
                    console.print(f"\n[{colour}]Quality: {score}/10 — {feedback}[/{colour}]")

                if score >= SCORE_THRESHOLD:
                    emit({"type": "step", "step": "write", "status": "done",
                          "info": f"Quality {score}/10 ✓"})
                    break

                # Prepare next revision
                write_input["feedback"]         = feedback
                write_input["previous_attempt"] = full_writer_output
                self.agents["writer"].clear_memory()
            else:
                emit({"type": "step", "step": "write", "status": "done"})

        self.memory.write("WriterAgent", writer_result.output)

        # ── Step 4: Critique & Improve ────────────────────────────────────────
        rule("[cyan]Step 4 — Critique & Improve[/cyan]")
        emit({"type": "step", "step": "critique", "status": "running"})

        critic_result = self.agents["critic"].run({
            "goal":  goal,
            "draft": writer_result.output,
        })

        if not critic_result.success:
            emit({"type": "step", "step": "critique", "status": "error",
                  "error": critic_result.error})
            final = writer_result.output
        else:
            self.memory.write("CriticAgent", critic_result.output)
            final = critic_result.output
            emit({"type": "step", "step": "critique", "status": "done",
                  "info": f"{critic_result.metadata.get('word_count', 0)} words"})

        # ── Done ──────────────────────────────────────────────────────────────
        emit({"type": "done", "stats": {
            "sources": len(urls),
            "words":   len(final.split()),
            "score":   final_score,
        }})

        if not is_api:
            console.rule("[bold green]Final Output[/bold green]")
            console.print(Markdown(final))

        return final
