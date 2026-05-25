import argparse
from nexus import Orchestrator

def main():
    parser = argparse.ArgumentParser(
        description="Nexus — Multi-Agent Research System by Rewrite Labs"
    )
    parser.add_argument("goal", type=str, help="The research goal or question")
    parser.add_argument(
        "--format",
        choices=["report", "blog", "summary", "essay"],
        default="report",
        help="Output format (default: report)"
    )
    parser.add_argument(
        "--model",
        default="llama3",
        help="Ollama model to use (default: llama3)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save output to a file"
    )
    args = parser.parse_args()

    orchestrator = Orchestrator(model=args.model, output_format=args.format)
    result = orchestrator.run(args.goal)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nSaved to {args.output}")

if __name__ == "__main__":
    main()
