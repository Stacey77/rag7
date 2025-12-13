"""Main entry point for the LangGraph multi-agent system."""

import argparse
import sys
from typing import Optional

from langgraph.config import get_settings
from langgraph.graphs import (
    create_sequential_graph,
    create_parallel_graph,
    create_loop_graph,
    create_router_graph,
    create_aggregator_graph,
    create_hierarchical_graph,
    create_network_graph,
)
from langgraph.graphs.sequential_graph import run_sequential_pipeline
from langgraph.graphs.parallel_graph import run_parallel_pipeline
from langgraph.graphs.loop_graph import run_loop_pipeline
from langgraph.graphs.router_graph import run_router_pipeline
from langgraph.graphs.aggregator_graph import run_aggregator_pipeline
from langgraph.graphs.hierarchical_graph import run_hierarchical_pipeline
from langgraph.graphs.network_graph import run_network_pipeline


PATTERNS = {
    "sequential": {
        "description": "Agents working in chain order (Researcher → Writer → Reviewer)",
        "runner": run_sequential_pipeline,
    },
    "parallel": {
        "description": "Multiple agents processing simultaneously",
        "runner": run_parallel_pipeline,
    },
    "loop": {
        "description": "Iterative improvement until quality threshold",
        "runner": run_loop_pipeline,
    },
    "router": {
        "description": "Direct inputs to specialized handlers",
        "runner": run_router_pipeline,
    },
    "aggregator": {
        "description": "Consolidate multiple agent outputs",
        "runner": run_aggregator_pipeline,
    },
    "hierarchical": {
        "description": "Manager-worker structure with delegation",
        "runner": run_hierarchical_pipeline,
    },
    "network": {
        "description": "Interconnected agents with bidirectional communication",
        "runner": run_network_pipeline,
    },
}


def list_patterns() -> None:
    """Print available patterns and their descriptions."""
    print("\nAvailable Agent Patterns:")
    print("-" * 60)
    for name, info in PATTERNS.items():
        print(f"  {name:15} - {info['description']}")
    print()


def run_pattern(pattern: str, task: str, **kwargs) -> dict:
    """Run a specific pattern with the given task.

    Args:
        pattern: Name of the pattern to run.
        task: The task to process.
        **kwargs: Additional arguments for specific patterns.

    Returns:
        Final state after pattern execution.

    Raises:
        ValueError: If pattern is not recognized.
    """
    if pattern not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern}. Use --list to see available patterns.")

    runner = PATTERNS[pattern]["runner"]
    return runner(task, **kwargs)


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="LangGraph Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m langgraph.main --pattern sequential --task "Write about AI"
  python -m langgraph.main --pattern loop --task "Create a blog post" --quality 0.9
  python -m langgraph.main --list
        """,
    )

    parser.add_argument(
        "--pattern", "-p",
        type=str,
        choices=list(PATTERNS.keys()),
        help="Agent pattern to use",
    )

    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Task or query to process",
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available patterns",
    )

    parser.add_argument(
        "--quality",
        type=float,
        default=0.8,
        help="Quality threshold for loop pattern (default: 0.8)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum iterations for loop/hierarchical patterns (default: 5)",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.list:
        list_patterns()
        return 0

    if not args.pattern or not args.task:
        parser.print_help()
        print("\nError: --pattern and --task are required unless --list is specified")
        return 1

    # Check for API key
    settings = get_settings()
    if not settings.openai_api_key:
        print("Warning: OPENAI_API_KEY not set. LLM calls will fail.")

    try:
        print(f"\nRunning {args.pattern} pattern...")
        print(f"Task: {args.task}\n")

        # Prepare kwargs for specific patterns
        kwargs = {}
        if args.pattern == "loop":
            kwargs["quality_threshold"] = args.quality
            kwargs["max_iterations"] = args.max_iterations
        elif args.pattern == "hierarchical":
            kwargs["max_iterations"] = args.max_iterations

        result = run_pattern(args.pattern, args.task, **kwargs)

        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)

        if args.verbose:
            print(f"\nFull State:")
            for key, value in result.items():
                if key != "messages":
                    print(f"  {key}: {value}")

        print(f"\nFinal Output:\n{result.get('final_output', 'No output generated')}")
        print(f"\nQuality Score: {result.get('quality_score', 'N/A')}")
        print(f"Iterations: {result.get('iteration_count', 'N/A')}")

        return 0

    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
