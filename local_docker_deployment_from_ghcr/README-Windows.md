# Windows Deployment Scripts

Windows batch file equivalents of the Linux/macOS shell scripts for deploying the MCP RAG system.

**Note:** ChromaDB server management has been moved to the kiro-project. This document now covers only MCP RAG server deployment.

## Prerequisites

- **Docker Desktop** installed and running
- **curl** available in PATH (usually comes with Git for Windows or can be installed separately)
- Command Prompt or PowerShell with Administrator privileges (for Docker operations)

## Files

- `deploy-mcp-server.bat` - MCP RAG server deployment
- `docker-compose.yml` - ChromaDB configuration (managed by kiro-project)
- `docker-compose.mcp-server.yml` - MCP server configuration

**Note:** ChromaDB server management (`chromadb-server.bat`) is now handled by kiro-project.

## Usage

### 1. ChromaDB Server Management (Moved to kiro-project)

ChromaDB server management is now handled by the kiro-project. Please refer to kiro-project documentation for:
- Starting and stopping ChromaDB server
- Health checks and monitoring
- Log viewing and troubleshooting
- Data management and cleanup

### 2. MCP RAG Server Deployment

```batch
REM Deploy MCP RAG server (pulls latest from GitHub Container Registry)
deploy-mcp-server.bat
```

## Step-by-Step Deployment

1. **Start ChromaDB server (via kiro-project):**
   - Use kiro-project tools to start ChromaDB server
   - Refer to kiro-project documentation for specific commands

2. **Verify ChromaDB is healthy:**
   - Use kiro-project health check commands
   - Ensure ChromaDB is accessible at http://localhost:8000

3. **Deploy MCP RAG server:**
   ```batch
   deploy-mcp-server.bat
   ```

4. **Verify deployment:**
   - MCP Server: http://localhost:8080
   - ChromaDB: http://localhost:8000  
   - Health endpoint: http://localhost:8080/health

## Troubleshooting

### Common Issues

**"Network not found" error:**
```batch
REM Manually create the network
docker network create mcp-network
```

**"curl command not found":**
- Install Git for Windows (includes curl)
- Or install curl separately from https://curl.se/windows/
- Or use PowerShell's `Invoke-WebRequest` as alternative

**Permission errors:**
- Run Command Prompt as Administrator
- Ensure Docker Desktop has necessary permissions

**Health check fails:**
```batch
REM Check container logs
docker logs mcp-rag-server

REM Check if ports are available
netstat -an | findstr :8080
netstat -an | findstr :8000
```

### Manual Commands

If batch files don't work, use these manual commands:

```batch
REM Create network
docker network create mcp-network

REM Start ChromaDB
docker-compose -f docker-compose.yml up -d chromadb

REM Pull and start MCP server
docker pull ghcr.io/rwuniard/mcp_rag:latest
docker-compose -f docker-compose.mcp-server.yml up -d mcp-rag-server

REM Check status
docker ps
```

## Differences from Linux/macOS Scripts

1. **File paths:** Use backslashes (`\`) instead of forward slashes (`/`)
2. **Environment variables:** Use `%VAR%` instead of `$VAR`
3. **Command availability:** `curl` may need separate installation
4. **Colors:** Emoji and colors may not display properly in older Command Prompt
5. **Error handling:** Windows batch error handling is more basic than Bash

## Alternative: PowerShell Scripts

For more advanced features, consider using PowerShell equivalents with better error handling and modern Windows features.