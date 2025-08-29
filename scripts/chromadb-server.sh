#!/bin/bash
# ChromaDB Server Management Script - Wrapper

# This script redirects to the actual ChromaDB server script in setup_chromadb/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_SCRIPT="$SCRIPT_DIR/../setup_chromadb/chromadb-server.sh"

if [ -f "$SETUP_SCRIPT" ]; then
    exec "$SETUP_SCRIPT" "$@"
else
    echo "❌ ChromaDB server script not found at: $SETUP_SCRIPT"
    echo "💡 Please ensure setup_chromadb/chromadb-server.sh exists"
    exit 1
fi