#!/bin/bash

# MCP RAG Server Deployment Script
# Deploys the production Docker image from GitHub Container Registry

set -e

# Configuration
MCP_CONTAINER="mcp-rag-server"
GITHUB_IMAGE="ghcr.io/rwuniard/mcp_rag:latest"
NETWORK_NAME="mcp-network"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MCP RAG Server Deployment${NC}"
echo "=========================================="

# Function to check if container is running
is_container_running() {
    docker ps -q -f name="$1" | grep -q .
}

# Function to check if network exists
network_exists() {
    docker network ls -q -f name="$1" | grep -q .
}

# Step 1: Check network exists
echo -e "\n${YELLOW}📡 Checking Docker network...${NC}"
if ! network_exists "$NETWORK_NAME"; then
    echo -e "${RED}❌ Network '$NETWORK_NAME' does not exist${NC}"
    echo -e "${YELLOW}💡 Please run ChromaDB setup first:${NC}"
    echo "   ./setup_chroma_db/chromadb-server.sh start"
    exit 1
fi
echo -e "${GREEN}✅ Network '$NETWORK_NAME' exists${NC}"

# Step 2: Check ChromaDB is running
echo -e "\n${YELLOW}🗄️  Checking ChromaDB...${NC}"
if ! is_container_running "chromadb"; then
    echo -e "${RED}❌ ChromaDB is not running${NC}"
    echo -e "${YELLOW}💡 Please start ChromaDB first:${NC}"
    echo "   ./setup_chroma_db/chromadb-server.sh start"
    exit 1
fi
echo -e "${GREEN}✅ ChromaDB is running${NC}"

# Step 3: Stop existing MCP container if running
echo -e "\n${YELLOW}🔄 Checking existing MCP RAG server...${NC}"
if is_container_running "$MCP_CONTAINER"; then
    echo -e "${YELLOW}🛑 Stopping existing MCP RAG server...${NC}"
    docker stop "$MCP_CONTAINER"
    docker rm "$MCP_CONTAINER"
    echo -e "${GREEN}✅ Previous container stopped and removed${NC}"
fi

# Step 4: Pull latest production image
echo -e "\n${YELLOW}📦 Pulling latest production Docker image...${NC}"
echo -e "${BLUE}Image: $GITHUB_IMAGE${NC}"
docker pull "$GITHUB_IMAGE"
echo -e "${GREEN}✅ Latest production image pulled${NC}"

# Step 5: Run MCP RAG server
echo -e "\n${YELLOW}🚀 Starting MCP RAG server...${NC}"
docker run -d \
    --name "$MCP_CONTAINER" \
    --network "$NETWORK_NAME" \
    -p 8080:8080 \
    -e CHROMADB_HOST=chromadb \
    -e CHROMADB_PORT=8000 \
    -e MCP_HOST=0.0.0.0 \
    -e MCP_PORT=8080 \
    -e MCP_TRANSPORT=http \
    "$GITHUB_IMAGE"

# Step 6: Wait and verify
echo -e "${YELLOW}⏳ Waiting for MCP RAG server to start...${NC}"
sleep 8

# Check if container is still running
if is_container_running "$MCP_CONTAINER"; then
    echo -e "${GREEN}✅ MCP RAG server started successfully!${NC}"
    
    # Show container logs (last 10 lines)
    echo -e "\n${YELLOW}📋 Recent logs:${NC}"
    docker logs --tail 10 "$MCP_CONTAINER"
    
    # Test connectivity
    echo -e "\n${YELLOW}🔍 Testing server connectivity...${NC}"
    sleep 2
    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check not available (server may still be starting)${NC}"
    fi
    
    # Show connection info
    echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"
    echo "=========================================="
    echo -e "${BLUE}MCP RAG Server:${NC} http://localhost:8080"
    echo -e "${BLUE}ChromaDB:${NC} http://localhost:8000"
    echo -e "${BLUE}Using Production API Key:${NC} ✅"
    echo ""
    echo -e "${YELLOW}📝 Useful commands:${NC}"
    echo "  View logs:    docker logs -f $MCP_CONTAINER"
    echo "  Stop server:  docker stop $MCP_CONTAINER"
    echo "  Restart:      $0"
    echo "  Stop ChromaDB: ./setup_chroma_db/chromadb-server.sh stop"
    echo ""
else
    echo -e "${RED}❌ MCP RAG server failed to start${NC}"
    echo -e "${YELLOW}📋 Container logs:${NC}"
    docker logs "$MCP_CONTAINER"
    echo -e "\n${YELLOW}💡 Troubleshooting:${NC}"
    echo "  1. Check if ChromaDB is healthy: ./setup_chroma_db/chromadb-server.sh health"
    echo "  2. Check container status: docker ps -a"
    echo "  3. Check network: docker network ls"
    exit 1
fi