#!/usr/bin/env python3
"""
RAG Store CLI - Document Ingestion Service

Command-line interface for the document ingestion service.
Processes and stores documents with embeddings.
"""

import sys
from pathlib import Path

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .store_embeddings import main as store_main
except ImportError:
    # Fallback for direct execution
    from store_embeddings import main as store_main


def main():
    """Entry point for the RAG Store CLI."""
    print("🗄️  RAG Store - Document Ingestion Service")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "store":
        # Run the document storage process
        store_main()
    else:
        print("Usage:")
        print("  rag-store-cli store              # Store documents to ChromaDB")
        print("  python -m rag_store.cli store   # Store documents (development)")
        print()
        print("Make sure you have:")
        print("1. GOOGLE_API_KEY in your .env file")
        print("2. PDF and text files in the data_source directory")


if __name__ == "__main__":
    main()