#!/usr/bin/env python3
"""
MCP RAG - Main entry point

This script provides a simple interface to the RAG functionality.
For MCP server, use: python mcp_server.py
"""

import sys

from pathlib import Path

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .search_similarity import ModelVendor, similarity_search_mcp_tool
    from ._version import __version__, get_version_info
except ImportError:
    # Fallback for direct execution
    from search_similarity import ModelVendor, similarity_search_mcp_tool
    from _version import __version__, get_version_info


def main():
    # Handle version flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--version", "-v"]:
        version_info = get_version_info()
        print(f"rag-fetch version {version_info['version']}")
        if version_info['git_sha']:
            print(f"Git SHA: {version_info['git_sha']}")
            if version_info['git_branch']:
                print(f"Git Branch: {version_info['git_branch']}")
            if version_info['git_dirty']:
                print("Status: dirty (uncommitted changes)")
        return

    print("🤖 MCP RAG - Retrieval Augmented Generation with MCP")
    print(f"Version: {__version__}")
    print("=" * 50)

    if len(sys.argv) > 1:
        # Simple CLI interface
        query = " ".join(sys.argv[1:])
        print(f"Searching for: '{query}'")
        print()

        try:
            result = similarity_search_mcp_tool(query, ModelVendor.GOOGLE, limit=3)
            print("Results:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
            print("\nMake sure you have:")
            print("1. GOOGLE_API_KEY in your .env file")
            print(
                "2. Documents stored in ChromaDB (run: cd rag_store && python store_embeddings.py)"
            )
    else:
        print("Usage:")
        print("  rag-fetch-cli --version           # Show version info")
        print("  rag-fetch-cli <search query>     # Search documents")
        print("  rag-mcp-server                   # Start MCP server")
        print()
        print("Example:")
        print("  rag-fetch-cli 'interesting facts about English'")


if __name__ == "__main__":
    main()
