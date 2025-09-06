# Local Docker Deployment (Build from Local Source)

This deployment configuration builds the Docker image locally from your current source code instead of pulling from GitHub Container Registry (GHCR). This is useful for testing local changes before merging to the main branch.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git repository with your local changes

### Deploy Services

**Linux/macOS:**
```bash
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### Stop Services

**Linux/macOS:**
```bash
./shutdown.sh
```

**Windows:**
```cmd
shutdown.bat
```

## Services

- **ChromaDB**: Vector database at http://localhost:8000
- **MCP RAG Server**: Built locally from current source code at http://localhost:8080
  - Health Check: http://localhost:8080/health

## Differences from GHCR Deployment

| Feature | GHCR Deployment | Local Build Deployment |
|---------|-----------------|-------------------------|
| Image Source | `ghcr.io/rwuniard/mcp_rag:latest` | Built from local source |
| Container Name | `mcp-rag-server` | `mcp-rag-server-local` |
| Build Time | Fast (pulls pre-built) | Slower (builds locally) |
| Use Case | Production/stable testing | Development/pre-merge testing |
| Code Changes | Requires CI/CD pipeline | Immediate local testing |

## Environment Configuration

The MCP RAG Server requires API keys for AI services. Create a `.env` file at `src/rag_fetch/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

Or set them as environment variables before running the deployment script.

## Data Persistence

ChromaDB data is persisted in `./data/chroma_data`. This directory will be created automatically and data will survive container restarts.

## Build Metadata

The build includes metadata about your current Git state:
- Build timestamp
- Git commit hash
- Git branch name
- Version tag (if available)

## Troubleshooting

### View Logs

```bash
# ChromaDB logs
docker-compose -f docker-compose.yml logs -f chromadb

# MCP RAG Server logs
docker-compose -f docker-compose.mcp-server.yml logs -f mcp-rag-server
```

### Common Issues

1. **Docker not running**: Ensure Docker Desktop is started
2. **Port conflicts**: Make sure ports 8000 and 8080 are not in use
3. **Build failures**: Check that you have a valid Dockerfile in the project root
4. **Network issues**: The script creates a `mcp-network` Docker network automatically

### Manual Commands

If you prefer manual control:

```bash
# Create network
docker network create mcp-network

# Start ChromaDB only
docker-compose -f docker-compose.yml up -d chromadb

# Build and start MCP RAG Server
docker-compose -f docker-compose.mcp-server.yml up -d --build

# Stop everything
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.mcp-server.yml down
```

## Development Workflow

1. Make changes to your source code
2. Run `./deploy.sh` to build and test locally
3. Verify functionality at http://localhost:8080
4. When satisfied, commit and push to trigger CI/CD
5. Use the GHCR deployment for production testing