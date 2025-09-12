# MCP RAG Local Deployment Scripts

Simple scripts to deploy the MCP RAG server locally using the production Docker images from GitHub Container Registry.

**Note:** ChromaDB server management has been moved to the kiro-project. This deployment now focuses on the MCP RAG server only.

## Quick Start

### 1. Start ChromaDB (via kiro-project)
```bash
# ChromaDB server management is now handled by kiro-project
# Please refer to kiro-project documentation for ChromaDB setup
```

### 2. Deploy MCP RAG Server
```bash
./scripts/deploy-mcp-server.sh
```

### 3. Verify Deployment
- **MCP RAG Server**: http://localhost:8080
- **ChromaDB**: http://localhost:8000

## Scripts Overview

### ChromaDB Management (Moved to kiro-project)
- **Purpose**: ChromaDB server management is now handled by kiro-project
- **Setup**: Use kiro-project tools to manage ChromaDB server
- **Network**: Ensure `mcp-network` exists for container communication
- **Data**: ChromaDB data persistence is managed by kiro-project

Please refer to kiro-project documentation for:
- Starting and stopping ChromaDB server
- Health monitoring and status checks
- Log viewing and troubleshooting
- Data management and cleanup

### MCP Server Deployment (`scripts/deploy-mcp-server.sh`)
- **Purpose**: Deploys production MCP RAG server
- **Source**: `ghcr.io/rwuniard/mcp_rag:latest`
- **Network**: Uses existing `mcp-network`
- **Container**: `mcp-rag-server`
- **API Key**: Uses production Google API key (baked into image)

**Features:**
- Pulls latest production image
- Stops/removes existing containers
- Verifies ChromaDB connectivity
- Shows deployment status and logs

## Deployment Flow

```
1. ChromaDB Setup (via kiro-project)
   ├─ Use kiro-project to create mcp-network
   ├─ Use kiro-project to start chromadb container
   └─ Ensure ChromaDB is accessible on port 8000

2. MCP Server Deployment
   ├─ Verifies network exists
   ├─ Checks ChromaDB is running
   ├─ Pulls production image
   ├─ Starts mcp-rag-server container
   └─ Exposes port 8080
```

## Production vs Local Images

- **Production Image**: `ghcr.io/rwuniard/mcp_rag:latest`
  - Built by GitHub Actions
  - Contains production Google API key
  - Automatically updated on releases

- **Local Images**: Built manually
  - May contain test/development API keys
  - Used for development only

## Troubleshooting

### MCP Server Won't Start
```bash
# Check ChromaDB is running (use kiro-project tools)
# Refer to kiro-project documentation for status checks

# Check MCP server logs
docker logs mcp-rag-server

# Restart ChromaDB using kiro-project tools
# Refer to kiro-project documentation for restart commands
```

### Network Issues
```bash
# Check network exists
docker network ls | grep mcp-network

# Recreate network
docker network rm mcp-network
docker network create mcp-network
```

### Clean Restart
```bash
# Stop everything
docker stop mcp-rag-server chromadb
docker rm mcp-rag-server chromadb

# Start fresh
# Use kiro-project to start ChromaDB server
./scripts/deploy-mcp-server.sh
```