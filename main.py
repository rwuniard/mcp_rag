#!/usr/bin/env python3
"""
Convenience script to run RAG services from the project root.

This script provides a simple router for the different services.
For production use, install the package and use specific CLI commands.
"""

import sys

from pathlib import Path

# Add src to path for development usage
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    print("🤖 MCP RAG - Microservices Architecture")
    print("=" * 50)

    if len(sys.argv) > 1:
        service = sys.argv[1]

        if service == "store":
            from rag_store.cli import main as store_main

            store_main()
        elif service == "search":
            from rag_fetch.cli import main as fetch_main

            fetch_main()
        elif service == "server":
            from rag_fetch.mcp_server import main as server_main

            server_main()
        else:
            print(f"Unknown service: {service}")
            show_usage()
    else:
        show_usage()


def show_usage():
    print("Usage:")
    print("  python main.py store    # Run document ingestion service")
    print("  python main.py search   # Run search CLI")
    print("  python main.py server   # Start MCP server")
    print()
    print("Individual services:")
    print("  python src/rag_store/cli.py store")
    print("  python src/rag_fetch/cli.py <query>")
    print("  python src/rag_fetch/mcp_server.py")


if __name__ == "__main__":
    main()
