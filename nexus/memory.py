from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntry:
    agent: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SharedMemory:
    """
    Shared memory store across all agents in a pipeline.
    Allows agents to read each other's outputs and build on them.
    """

    def __init__(self):
        self._store: list[MemoryEntry] = []

    def write(self, agent: str, content: str):
        self._store.append(MemoryEntry(agent=agent, content=content))

    def read_all(self) -> str:
        return "\n\n".join([
            f"[{e.agent} @ {e.timestamp}]\n{e.content}"
            for e in self._store
        ])

    def read_last(self, n: int = 1) -> list[MemoryEntry]:
        return self._store[-n:]

    def read_by_agent(self, agent_name: str) -> list[MemoryEntry]:
        return [e for e in self._store if e.agent == agent_name]

    def clear(self):
        self._store = []

    def __len__(self):
        return len(self._store)
