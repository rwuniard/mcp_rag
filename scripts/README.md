# MCP RAG Local Deployment Scripts

Simple scripts to deploy the MCP RAG server locally using the production Docker images from GitHub Container Registry.

## Quick Start

### 1. Start ChromaDB
```bash
./setup_chroma_db/chromadb-server.sh start
```

### 2. Deploy MCP RAG Server
```bash
./scripts/deploy-mcp-server.sh
```

### 3. Verify Deployment
- **MCP RAG Server**: http://localhost:8080
- **ChromaDB**: http://localhost:8000

## Scripts Overview

### ChromaDB Management (`setup_chroma_db/chromadb-server.sh`)
- **Purpose**: Manages ChromaDB vector database
- **Network**: Creates and uses `mcp-network`
- **Container**: `chromadb`
- **Data**: Persisted in `setup_chroma_db/data/chroma_data/`

**Commands:**
- `start` - Start ChromaDB server
- `stop` - Stop ChromaDB server
- `restart` - Restart ChromaDB server
- `status` - Show server status
- `logs` - Show server logs
- `health` - Check server health
- `clean` - Stop and remove all data (DANGEROUS)

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
1. ChromaDB Setup
   ├─ Creates mcp-network
   ├─ Starts chromadb container
   └─ Exposes port 8000

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
# Check ChromaDB is running
./setup_chroma_db/chromadb-server.sh status

# Check logs
docker logs mcp-rag-server

# Restart ChromaDB
./setup_chroma_db/chromadb-server.sh restart
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
./setup_chroma_db/chromadb-server.sh start
./scripts/deploy-mcp-server.sh
```