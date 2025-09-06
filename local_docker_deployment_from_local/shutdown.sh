#!/bin/bash

# Local Docker Shutdown Script (Local Build Version)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_status "Stopping local Docker deployment (local build)..."

# Stop MCP RAG Server
print_status "Stopping MCP RAG Server..."
docker-compose -f docker-compose.mcp-server.yml down || print_warning "MCP RAG Server was not running"

# Stop ChromaDB
print_status "Stopping ChromaDB..."
docker-compose -f docker-compose.yml down || print_warning "ChromaDB was not running"

print_success "All services stopped!"
print_status "Data is preserved in ./data/chroma_data"
print_status "To restart, run: ./deploy.sh"