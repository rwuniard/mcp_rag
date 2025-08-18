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
    from .search_similarity import similarity_search_mcp_tool, ModelVendor
except ImportError:
    # Fallback for direct execution
    from search_similarity import similarity_search_mcp_tool, ModelVendor


def main():
    print("🤖 MCP RAG - Retrieval Augmented Generation with MCP")
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
            print("2. Documents stored in ChromaDB (run: cd rag_store && python store_embeddings.py)")
    else:
        print("Usage:")
        print("  python main.py <search query>     # Search documents")
        print("  python mcp_server.py              # Start MCP server")
        print()
        print("Example:")
        print("  python main.py 'interesting facts about English'")


if __name__ == "__main__":
    main()
