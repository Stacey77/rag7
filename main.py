"""Main entry point for the RAG7 multi-LLM orchestration service."""
import sys
import argparse
import uvicorn
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag7.config import config_manager


def main():
    """Main entry point for running the API server."""
    parser = argparse.ArgumentParser(
        description="RAG7 Multi-LLM Orchestration Service"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("RAG7 Multi-LLM Orchestration Service")
    print("=" * 70)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Config: {args.config}")
    print(f"Reload: {args.reload}")
    print("=" * 70)
    
    # Run the server
    uvicorn.run(
        "rag7.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
