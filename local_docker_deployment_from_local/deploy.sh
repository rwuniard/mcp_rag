#!/bin/bash

# Local Docker Deployment Script (Build from Local Source)
# This script builds the Docker image locally and deploys it with ChromaDB

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Starting local Docker deployment (building from local source)..."

# Set build metadata
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
export GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
export VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

print_status "Build metadata:"
print_status "  Build Date: $BUILD_DATE"
print_status "  Git Commit: $GIT_COMMIT"
print_status "  Git Branch: $GIT_BRANCH"
print_status "  Version: $VERSION"

# Create network if it doesn't exist
print_status "Creating Docker network 'mcp-network' if it doesn't exist..."
docker network create mcp-network 2>/dev/null || print_warning "Network 'mcp-network' already exists"

# Create data directory
print_status "Creating data directory..."
mkdir -p ./data/chroma_data

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
docker-compose -f docker-compose.mcp-server.yml down 2>/dev/null || true

# Start ChromaDB first
print_status "Starting ChromaDB..."
docker-compose -f docker-compose.yml up -d chromadb

# Wait for ChromaDB to be healthy
print_status "Waiting for ChromaDB to be ready..."
timeout=60
counter=0
while ! docker exec chromadb curl -f http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "ChromaDB failed to start within $timeout seconds"
        docker-compose -f docker-compose.yml logs chromadb
        exit 1
    fi
    echo -n "."
    sleep 1
    counter=$((counter + 1))
done
echo ""
print_success "ChromaDB is ready!"

# Build and start MCP RAG Server
print_status "Building and starting MCP RAG Server (this may take a few minutes)..."
docker-compose -f docker-compose.mcp-server.yml up -d --build

# Wait for MCP RAG Server to be healthy
print_status "Waiting for MCP RAG Server to be ready..."
timeout=120
counter=0
while ! docker exec mcp-rag-server-local curl -f http://localhost:8080/health > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "MCP RAG Server failed to start within $timeout seconds"
        docker-compose -f docker-compose.mcp-server.yml logs mcp-rag-server
        exit 1
    fi
    echo -n "."
    sleep 1
    counter=$((counter + 1))
done
echo ""

print_success "All services are running!"
print_status "Services available at:"
print_status "  ChromaDB: http://localhost:8000"
print_status "  MCP RAG Server: http://localhost:8080"
print_status "  Health Check: http://localhost:8080/health"

print_status "To view logs, run:"
print_status "  docker-compose -f docker-compose.yml logs -f chromadb"
print_status "  docker-compose -f docker-compose.mcp-server.yml logs -f mcp-rag-server"

print_status "To stop services, run:"
print_status "  ./shutdown.sh"