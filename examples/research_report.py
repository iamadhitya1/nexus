"""
Example: Generate a research report on any topic.
Run: python examples/research_report.py
"""
from nexus import Orchestrator

orchestrator = Orchestrator(output_format="report")
result = orchestrator.run("What are the latest breakthroughs in quantum computing in 2025?")

with open("quantum_computing_report.md", "w") as f:
    f.write(result)

print("\nReport saved to quantum_computing_report.md")
