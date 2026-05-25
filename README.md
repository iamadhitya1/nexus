# Nexus 🔮
### Multi-Agent Research System — by [Rewrite Labs](https://github.com/iamadhitya1)

> Give Nexus a goal. It searches the web, reads sources, writes a draft, critiques it, and delivers a polished output — fully autonomously.

---

## How it works

```
You → Give a goal
         ↓
   Orchestrator
         ↓
  ┌──────────────────────────────────────┐
  ▼              ▼          ▼            ▼
Search       Reader      Writer      Critic
Agent        Agent       Agent       Agent
(finds URLs) (reads &    (writes     (reviews &
             extracts)   draft)      improves)
  └──────────────────────────────────────┘
         ↓
   Final Output
```

**No LangChain. No CrewAI. Built from scratch.**

Each agent is an independent LLM-powered unit with its own memory, role, and tool access. The Orchestrator coordinates them in a sequential pipeline, passing knowledge between agents via shared memory.

---

## Features

- 🔍 **SearchAgent** — Generates smart queries and finds the best sources via DuckDuckGo
- 📖 **ReaderAgent** — Visits URLs, extracts and summarises relevant content
- ✍️ **WriterAgent** — Writes structured output (report, blog, summary, essay)
- 🧠 **CriticAgent** — Reviews the draft, identifies gaps, produces the final version
- 💾 **SharedMemory** — Agents share knowledge across the pipeline
- 🎨 **Rich terminal UI** — Beautiful output with progress indicators
- 🔒 **Fully local** — Runs on Ollama, no API keys, no internet dependency for AI

---

## Setup

**Prerequisites:** Python 3.11+, [Ollama](https://ollama.ai) installed

```bash
git clone https://github.com/iamadhitya1/nexus.git
cd nexus
pip install -r requirements.txt
playwright install chromium
ollama pull llama3
```

---

## Usage

**CLI:**
```bash
# Research report (default)
python main.py "What is the future of renewable energy?"

# Blog post
python main.py "How do AI agents work?" --format blog

# Summary
python main.py "Latest AI research in 2025" --format summary

# Save to file
python main.py "Quantum computing breakthroughs" --output report.md
```

**Python API:**
```python
from nexus import Orchestrator

orchestrator = Orchestrator(output_format="blog")
result = orchestrator.run("Why are multi-agent systems the future of AI?")
print(result)
```

---

## Architecture

```
nexus/
├── nexus/
│   ├── agent.py          # BaseAgent — all agents inherit from this
│   ├── orchestrator.py   # Pipeline coordinator
│   ├── memory.py         # SharedMemory across agents
│   ├── agents/
│   │   ├── search.py     # Web search + query generation
│   │   ├── reader.py     # URL reading + knowledge extraction
│   │   ├── writer.py     # Structured content generation
│   │   └── critic.py     # Review + improvement
│   └── tools/
│       ├── web_search.py # DuckDuckGo wrapper
│       └── browser.py    # Playwright-based URL reader
├── examples/
│   ├── research_report.py
│   └── blog_post.py
└── main.py               # CLI entry point
```

---

## Extending Nexus

Add your own agent in 3 steps:

```python
from nexus.agent import BaseAgent, AgentResult

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent", role="You are a specialist in X.")

    def run(self, input) -> AgentResult:
        result = self.think(f"Do something with: {input}")
        return AgentResult(agent=self.name, output=result, success=True)
```

---

## Built with

- [Ollama](https://ollama.ai) — Local LLM inference
- [Playwright](https://playwright.dev) — Browser automation
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) — No-key web search
- [Rich](https://github.com/Textualize/rich) — Terminal UI

---

## License

MIT © [iamadhitya1](https://github.com/iamadhitya1) — Rewrite Labs
