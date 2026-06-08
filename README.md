# Nexus 🔮
### Multi-Agent Research System — by [Rewrite Labs](https://rewritelabs.vercel.app)

[![MIT License](https://img.shields.io/badge/License-MIT-39FF14?style=flat-square)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-0a0a0a?style=flat-square&logo=python)](https://python.org)
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-f55036?style=flat-square)](https://groq.com)
[![Rewrite Labs](https://img.shields.io/badge/Rewrite-Labs-39FF14?style=flat-square)](https://rewritelabs.vercel.app)

> Give Nexus a goal. Five agents search the web, extract knowledge, write a draft, score its quality, revise it, and deliver a polished output — fully autonomously.

**No LangChain. No CrewAI. No wrappers. Built from scratch.**

---

## How it works

```
You → Give a goal
              ↓
        Orchestrator
              ↓
  ┌──────────────────────────────────────────────────┐
  ▼          ▼           ▼            ▼          ▼
Search    Reader      Writer      Scorer      Critic
Agent     Agent       Agent       Agent       Agent
(finds    (extracts   (writes     (scores     (reviews &
sources)  knowledge)  draft)      quality)    improves)
  └──────────────────────────────────────────────────┘
              ↓
         Final Output
   (streamed live to terminal or browser)
```

**ReAct quality loop:** After each draft, the ScorerAgent rates it 1-10. If below 7, the WriterAgent revises with specific feedback — up to 2 times — before passing to the CriticAgent.

---

## Features

- 🔍 **SearchAgent** — Generates targeted queries, finds the best sources via DuckDuckGo (no API key)
- 📖 **ReaderAgent** — Synthesises search snippets into structured, thematic knowledge
- ✍️ **WriterAgent** — Writes in 8 formats with support for revision via feedback
- ⬡ **ScorerAgent** — Rates draft quality 1-10, gives one-line actionable feedback
- 🧠 **CriticAgent** — Reviews, identifies gaps, and produces the final polished version
- ⚡ **Live streaming** — Tokens stream in real time — in the terminal and in the Web UI
- 🌐 **Web UI** — Clean dark terminal interface (React + Vite) with step indicators and markdown rendering
- 🔁 **ReAct loop** — Automatic quality-gated revision before the critic ever sees the draft
- 💾 **SharedMemory** — Agents share knowledge across the pipeline

---

## Output Formats

| Format | Description |
|---|---|
| `report` | Executive Summary, Key Findings, Analysis, Conclusion |
| `blog` | Hook, 4-6 subheadings, conclusion — conversational expert tone |
| `summary` | Bullet-point highlights + 2-3 tight paragraphs |
| `essay` | Thesis introduction, body paragraphs, conclusion |
| `tweet-thread` | 8-12 numbered tweets, max 280 chars each, ends with CTA |
| `linkedin` | Hook, short paragraphs, hashtags — LinkedIn-native format |
| `newsletter` | Subject line, sections, key takeaway box, CTA |
| `slides` | Slide-by-slide content — `## Slide N: Title` + bullets |

---

## Quickstart

### Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com) (takes 30 seconds)

### 1. Clone & install

```bash
git clone https://github.com/iamadhitya1/nexus.git
cd nexus
pip install -r requirements.txt
```

### 2. Set your Groq key

**Windows:**
```cmd
set GROQ_API_KEY=your_key_here
```

**macOS / Linux:**
```bash
export GROQ_API_KEY=your_key_here
```

### 3. Run

```bash
python main.py "What is retrieval-augmented generation?" --format report
```

---

## Running the Web UI

The Web UI gives you a full browser interface with live streaming, step indicators, quality scores, and source links.

**Terminal 1 — Start the API server:**
```bash
# From the nexus/ root
set GROQ_API_KEY=your_key_here   # Windows
export GROQ_API_KEY=your_key_here  # macOS/Linux

uvicorn api.server:app --reload --port 8000
```

**Terminal 2 — Start the frontend:**
```bash
cd ui
npm install
npm run dev
```

Then open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## CLI Usage

```bash
# Research report (default)
python main.py "What is the future of renewable energy?"

# Blog post
python main.py "How do multi-agent systems work?" --format blog

# Tweet thread
python main.py "Why Rust is taking over systems programming" --format tweet-thread

# LinkedIn post
python main.py "Lessons from building a startup solo" --format linkedin

# Slides
python main.py "Introduction to transformer architecture" --format slides

# Save output to a file
python main.py "Quantum computing in 2025" --format report --output report.md

# Use a different Groq model
python main.py "AI safety overview" --model llama-3.1-8b-instant
```

---

## Python API

```python
from nexus import Orchestrator

# Basic usage
orch = Orchestrator(output_format="blog")
result = orch.run("Why are multi-agent systems the future of AI?")
print(result)

# With event streaming (for custom UIs)
def handle_event(event):
    if event["type"] == "token":
        print(event["content"], end="", flush=True)
    elif event["type"] == "step":
        print(f"\n[{event['step']}] {event['status']}")

orch = Orchestrator(output_format="report")
orch.run("Explain transformer attention mechanisms", on_event=handle_event)
```

---

## Adding a Custom Agent

```python
from nexus.agent import BaseAgent, AgentResult

class TranslatorAgent(BaseAgent):
    def __init__(self, model="llama-3.3-70b-versatile"):
        super().__init__(
            name="TranslatorAgent",
            role="You are an expert translator. Translate content accurately while preserving tone.",
            model=model
        )

    def run(self, input: dict) -> AgentResult:
        content  = input.get("content", "")
        language = input.get("language", "Spanish")

        result = self.think(f"Translate this to {language}:\n\n{content}")
        return AgentResult(agent=self.name, output=result, success=bool(result))
```

Plug it into the Orchestrator by adding it to `self.agents` and calling it in `run()`.

---

## Project Structure

```
nexus/
├── nexus/
│   ├── agent.py              # BaseAgent — think(), stream_think(), memory
│   ├── orchestrator.py       # Pipeline coordinator — ReAct loop + SSE events
│   ├── memory.py             # SharedMemory across agents
│   └── agents/
│       ├── search.py         # Web search + LLM query generation
│       ├── reader.py         # Knowledge extraction from search snippets
│       ├── writer.py         # Content generation in 8 formats + stream_run()
│       ├── scorer.py         # Quality scoring 1-10 with feedback
│       └── critic.py         # Review + final polish
├── tools/
│   └── web_search.py         # DuckDuckGo wrapper (no API key needed)
├── api/
│   └── server.py             # FastAPI SSE server (uvicorn)
├── ui/
│   ├── src/
│   │   ├── App.jsx           # Main UI — pipeline steps, streaming output
│   │   └── index.css         # Dark terminal theme
│   └── package.json
├── examples/
│   ├── research_report.py
│   └── blog_post.py
├── main.py                   # CLI entry point
└── requirements.txt
```

---

## Stack

| Layer | Tech |
|---|---|
| LLM | [Groq API](https://groq.com) — `llama-3.3-70b-versatile` |
| Web search | [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) — no API key |
| Terminal UI | [Rich](https://github.com/Textualize/rich) |
| API server | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) |
| Web UI | React 18 + Vite + react-markdown |

---

## Built by Rewrite Labs

Nexus is part of the **[Rewrite Labs](https://rewritelabs.vercel.app)** open-source suite — AI tools built for engineers and builders.

Other libraries:
- [`react-premium-gate`](https://github.com/iamadhitya1/react-premium-gate) — Razorpay paywall components
- [`groq-chain`](https://github.com/iamadhitya1/groq-chain) — Python Groq LLM chaining
- [`react-toast-native`](https://github.com/iamadhitya1/react-toast-native) — Lightweight toast notifications
- [`llm-router`](https://github.com/iamadhitya1/llm-router) — Route prompts to the right LLM by cost and complexity

---

## License

MIT © 2026 [M Adhitya](https://github.com/iamadhitya1) · Rewrite Labs

See [LICENSE](LICENSE) for full text.
