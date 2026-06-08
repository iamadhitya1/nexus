from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import os
from groq import Groq
from rich.console import Console

console = Console()
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@dataclass
class Message:
    role: str
    content: str


@dataclass
class AgentResult:
    agent: str
    output: str
    success: bool
    metadata: dict = field(default_factory=dict)
    error: str = ""


class BaseAgent(ABC):
    """
    Base class for all Nexus agents.
    Every agent has a name, a role description, and a model to think with.
    """

    def __init__(self, name: str, role: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.role = role
        self.model = model
        self.memory: list[Message] = []

    def _build_messages(self, prompt: str, system: str = None) -> list:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        for msg in self.memory:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": prompt})
        return messages

    def think(self, prompt: str, system: str = None) -> str:
        """Send a prompt to the LLM and get a full response."""
        messages = self._build_messages(prompt, system)
        response = _groq_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096,
        )
        reply = response.choices[0].message.content.strip()
        self.memory.append(Message("user", prompt))
        self.memory.append(Message("assistant", reply))
        return reply

    def stream_think(self, prompt: str, system: str = None):
        """Stream tokens from the LLM. Yields string chunks, stores full reply in memory."""
        messages = self._build_messages(prompt, system)
        stream = _groq_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=4096,
            stream=True,
        )
        full_reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_reply += delta
                yield delta
        self.memory.append(Message("user", prompt))
        self.memory.append(Message("assistant", full_reply))

    def remember(self, content: str):
        """Add context to the agent's memory."""
        self.memory.append(Message("system", content))

    def clear_memory(self):
        self.memory = []

    def log(self, msg: str):
        console.print(f"[bold cyan][{self.name}][/bold cyan] {msg}")

    @abstractmethod
    def run(self, input: Any) -> AgentResult:
        pass
