from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import ollama
from rich.console import Console

console = Console()


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


class BaseAgent(ABC):
    """
    Base class for all Nexus agents.
    Every agent has a name, a role description, and a model to think with.
    """

    def __init__(self, name: str, role: str, model: str = "llama3"):
        self.name = name
        self.role = role
        self.model = model
        self.memory: list[Message] = []

    def think(self, prompt: str, system: str = None) -> str:
        """Send a prompt to the LLM and get a response."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        for msg in self.memory:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": prompt})

        response = ollama.chat(model=self.model, messages=messages)
        reply = response["message"]["content"].strip()

        self.memory.append(Message("user", prompt))
        self.memory.append(Message("assistant", reply))
        return reply

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
