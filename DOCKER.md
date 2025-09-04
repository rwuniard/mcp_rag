# Docker Deployment Guide

This guide covers containerized deployment of the RAG Fetch MCP Server with version tracking and admin visibility.

## Quick Start

```bash
# Build and start the complete stack
docker-compose up -d

# Check version information
curl http://localhost:8080/health | jq
```

## Version Management

### Automatic Version Detection

The system uses Git-based versioning with the format: `v0.1.0` (tagged releases) or `0.1.0.dev3+g2898506` (development builds).

### Building with Version Information

```bash
# Automatic version detection
./docker-build.sh

# Manual version specification
docker build \
  --build-arg VERSION="0.1.0" \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t rag-fetch:0.1.0 .
```

## Admin Version Visibility

### 1. Container Labels (Primary Method)

```bash
# Check version labels on running container
docker inspect mcp-rag-fetch | jq '.[0].Config.Labels'

# Specific version info
docker inspect mcp-rag-fetch | jq '.[0].Config.Labels.version'
docker inspect mcp-rag-fetch | jq '.[0].Config.Labels."git.commit"'
```

### 2. Health Check Endpoint

```bash
# Complete server status with version
curl http://localhost:8080/health | jq

# Response includes:
{
  "server_name": "RAG Fetch MCP Server",
  "version": "0.1.0",
  "git_info": {
    "sha": "2898506",
    "branch": "versioning_docker_container_deploy",
    "dirty": false
  },
  "timestamp": "2025-01-03T15:30:00Z",
  "status": "healthy"
}
```

### 3. Container Logs (Startup Banner)

```bash
# View version in startup logs
docker logs mcp-rag-fetch | head -10

# Output includes:
# 🚀 RAG Fetch MCP Server v0.1.0 starting...
# 📦 Git SHA: 2898506
# 🌿 Git Branch: versioning_docker_container_deploy
```

### 4. Execute Version Command

```bash
# Run version command inside container
docker exec mcp-rag-fetch rag-fetch-cli --version

# Output:
# rag-fetch version 0.1.0
# Git SHA: 2898506
# Git Branch: versioning_docker_container_deploy
```

### 5. Environment Variables

```bash
# Check environment variables
docker exec mcp-rag-fetch printenv | grep -E "(VERSION|COMMIT|BUILD)"
```

## Architecture

### Multi-Stage Dockerfile

- **Base**: Common Python 3.12 setup
- **Builder**: Install dependencies and build wheel
- **Production**: Minimal runtime with security hardening
- **Development**: Full development environment with hot reload

### Container Security

- Non-root user execution (`ragfetch` user)
- Minimal attack surface (production stage)
- Health checks for orchestration
- Resource isolation via networks

### Network Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   rag-fetch     │────│    chromadb     │
│   Port: 8080    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 │
         rag-network (bridge)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server bind address |
| `MCP_PORT` | `8080` | Server port |
| `MCP_TRANSPORT` | `http` | Transport protocol |
| `CHROMADB_HOST` | `chromadb` | ChromaDB hostname |
| `CHROMADB_PORT` | `8000` | ChromaDB port |
| `LOG_LEVEL` | `INFO` | Logging level |

### Secrets Management

```bash
# Create .env file with API keys
cat > src/rag_fetch/.env << EOF
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
EOF

# The .env file is mounted read-only into the container
```

## Deployment Modes

### Production Deployment

```bash
# Complete production stack
docker-compose up -d

# Scale rag-fetch service
docker-compose up -d --scale rag-fetch=3

# View logs
docker-compose logs -f rag-fetch
```

### Development Mode

```bash
# Enable development override in docker-compose.yml
# Uncomment the rag-fetch-dev service

# Hot reload development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Load Balancing

For production scale, add a reverse proxy:

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - rag-fetch
```

## Monitoring and Maintenance

### Health Checks

Both services include comprehensive health checks:

```bash
# Check service health
docker-compose ps

# Manual health check
curl -f http://localhost:8080/health
curl -f http://localhost:8000/api/v1/heartbeat
```

### Log Management

```bash
# Follow logs from all services
docker-compose logs -f

# Service-specific logs
docker-compose logs -f rag-fetch
docker-compose logs -f chromadb

# Log rotation (configure in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Backup and Persistence

```bash
# Backup ChromaDB data
docker run --rm -v mcp-rag-chroma-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore ChromaDB data
docker run --rm -v mcp-rag-chroma-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/chroma-backup-20250103.tar.gz -C /data
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8080 and 8000 are available
2. **API keys**: Verify `.env` file contains valid API keys
3. **ChromaDB connection**: Check network connectivity between services
4. **Version mismatch**: Rebuild images after code changes

### Debug Commands

```bash
# Check network connectivity
docker exec mcp-rag-fetch ping chromadb

# Verify environment
docker exec mcp-rag-fetch env | grep -E "(CHROMA|API_KEY)"

# Test ChromaDB directly
curl http://localhost:8000/api/v1/heartbeat

# Container resource usage
docker stats mcp-rag-fetch mcp-rag-chromadb
```

### Performance Tuning

```bash
# Monitor resource usage
docker stats

# Adjust memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 512M
```

This containerized setup provides a production-ready RAG system with full version traceability and admin visibility.