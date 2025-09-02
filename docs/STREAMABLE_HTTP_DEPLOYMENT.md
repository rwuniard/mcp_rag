# MCP RAG Server - Streamable HTTP Deployment Guide

This guide covers deploying the MCP RAG server with Streamable HTTP transport for multiple client connections.

## Overview

The MCP RAG server now supports both STDIO and Streamable HTTP transports:

- **STDIO Transport**: Default mode for single-client usage (e.g., Claude Desktop)
- **Streamable HTTP Transport**: Network-based mode supporting multiple concurrent clients

## Quick Start

### 1. HTTP Mode (Default)
```bash
# Run with default HTTP transport
python -m rag_fetch.mcp_server

# Or using the CLI script
rag-mcp-server
```

The server will be available at: `http://127.0.0.1:8000/mcp`

### 2. STDIO Mode (Debug)
```bash
# Set transport to STDIO for debugging/single-client
export MCP_TRANSPORT=stdio

# Run the server
python -m rag_fetch.mcp_server
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `http` | Transport type: `http` or `stdio` |
| `MCP_HOST` | `127.0.0.1` | HTTP server host address |
| `MCP_PORT` | `8000` | HTTP server port |
| `MCP_HTTP_PATH` | `/mcp` | HTTP endpoint path |
| `MCP_MAX_CONNECTIONS` | `100` | Maximum concurrent connections |
| `MCP_CONNECTION_TIMEOUT` | `300` | Connection timeout (seconds) |
| `MCP_LOG_LEVEL` | `INFO` | Logging level |
| `MCP_ENABLE_CORS` | `true` | Enable CORS for web clients |
| `MCP_CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `MCP_SERVER_NAME` | `RAG World Fact Knowledge Base` | Server display name |

### Configuration Examples

#### Development Setup
```bash
# .env file for development
MCP_TRANSPORT=http
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_LOG_LEVEL=DEBUG
MCP_ENABLE_CORS=true
MCP_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Production Setup
```bash
# .env file for production
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_MAX_CONNECTIONS=200
MCP_CONNECTION_TIMEOUT=600
MCP_LOG_LEVEL=INFO
MCP_ENABLE_CORS=true
MCP_CORS_ORIGINS=https://yourapp.com,https://api.yourapp.com
```

## Client Connections

### Using FastMCP Client

#### Python Client
```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
    
    async with Client(transport) as client:
        # Test connection
        await client.ping()
        
        # Search documents
        result = await client.call_tool('search_documents', {
            'query': 'machine learning',
            'limit': 5
        })
        print(result.text)
        
        # Get server status
        status = await client.call_tool('server_status', {})
        print(status.text)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Multiple Clients
```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def client_task(client_id: int):
    """Task for individual client."""
    transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
    
    async with Client(transport) as client:
        result = await client.call_tool('search_documents', {
            'query': f'search from client {client_id}',
            'limit': 3
        })
        return f"Client {client_id}: {len(result.text)} chars"

async def main():
    # Run 5 concurrent clients
    tasks = [client_task(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Web Client (JavaScript)

```javascript
// Using fetch API for HTTP requests
class MCPClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.sessionId = Math.random().toString(36).substring(2);
    }
    
    async callTool(toolName, params = {}) {
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': this.sessionId
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                id: Date.now(),
                method: 'tools/call',
                params: {
                    name: toolName,
                    arguments: params
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data.result;
    }
}

// Usage
const client = new MCPClient('http://127.0.0.1:8000/mcp');

client.callTool('search_documents', {
    query: 'artificial intelligence',
    limit: 3
}).then(result => {
    console.log('Search results:', result);
}).catch(error => {
    console.error('Error:', error);
});
```

## Available Tools

### 1. search_documents
Search for relevant documents using semantic similarity.

```python
result = await client.call_tool('search_documents', {
    'query': 'your search query',
    'limit': 6  # optional, default: 6
})
```

### 2. server_status
Get current server status and connection metrics.

```python
status = await client.call_tool('server_status', {})
```

Example response:
```json
{
  "server_name": "RAG World Fact Knowledge Base",
  "transport": "http",
  "status": "running",
  "config": {
    "host": "127.0.0.1",
    "port": 8000,
    "endpoint": "http://127.0.0.1:8000/mcp",
    "max_connections": 100,
    "connection_timeout": 300,
    "chromadb": "localhost:8000"
  },
  "metrics": {
    "total_connections": 15,
    "current_connections": 3,
    "failed_connections": 0,
    "timed_out_connections": 1,
    "rejected_connections": 0
  },
  "active_connections": {
    "conn-abc123": {
      "client_ip": "192.168.1.100",
      "user_agent": "FastMCP-Client/2.11.3",
      "duration": 120.5,
      "requests_count": 8
    }
  }
}
```

### 3. list_active_connections
Get detailed information about all active connections.

```python
connections = await client.call_tool('list_active_connections', {})
```

## Deployment Scenarios

### 1. Single Server Instance

```bash
# Simple single server
export MCP_TRANSPORT=http
export MCP_HOST=0.0.0.0
export MCP_PORT=8000

python -m rag_fetch.mcp_server
```

### 2. Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000

ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

CMD ["python", "-m", "rag_fetch.mcp_server"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  mcp-rag-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_MAX_CONNECTIONS=200
      - CHROMADB_HOST=chromadb
      - CHROMADB_PORT=8000
    depends_on:
      - chromadb
    
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma/chroma
      
volumes:
  chromadb_data:
```

Run with:
```bash
docker-compose up -d
```

### 3. Reverse Proxy Setup

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-mcp-server.com;
    
    location /mcp {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
}
```

## Monitoring and Logging

### Connection Monitoring

The server provides built-in connection monitoring:

```python
# Get current status
status = await client.call_tool('server_status', {})

# Get active connections
connections = await client.call_tool('list_active_connections', {})
```

### Log Configuration

```bash
# Set log level
export MCP_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Example log output
2024-01-15 10:30:15,123 - rag_fetch.mcp_server - INFO - Starting MCP server with Streamable HTTP transport...
2024-01-15 10:30:15,124 - rag_fetch.mcp_server - INFO - Server will be available at: http://127.0.0.1:8000/mcp
2024-01-15 10:30:15,125 - rag_fetch.connection_manager - INFO - New connection: abc-123 from 192.168.1.100
```

### Prometheus Metrics (Optional)

Add Prometheus metrics to your deployment:

```python
# In your application monitoring
from prometheus_client import Counter, Histogram, Gauge

connection_count = Gauge('mcp_active_connections', 'Number of active MCP connections')
request_duration = Histogram('mcp_request_duration_seconds', 'Time spent processing MCP requests')
total_requests = Counter('mcp_requests_total', 'Total number of MCP requests')
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```bash
# Check if server is running
curl http://127.0.0.1:8000/mcp

# Check logs for errors
export MCP_LOG_LEVEL=DEBUG
python -m rag_fetch.mcp_server
```

#### 2. CORS Errors
```bash
# Enable CORS for your domain
export MCP_ENABLE_CORS=true
export MCP_CORS_ORIGINS=https://yourapp.com
```

#### 3. Too Many Connections
```bash
# Increase connection limit
export MCP_MAX_CONNECTIONS=500

# Check current connections
# Use server_status tool to monitor
```

#### 4. ChromaDB Connection Issues
```bash
# Check ChromaDB server
export CHROMADB_HOST=localhost
export CHROMADB_PORT=8000

# Test ChromaDB connection
curl http://localhost:8000/api/v1/heartbeat
```

### Performance Tuning

#### Server Settings
```bash
# Increase connection limits
export MCP_MAX_CONNECTIONS=1000
export MCP_CONNECTION_TIMEOUT=600

# Optimize logging
export MCP_LOG_LEVEL=WARNING
export MCP_ENABLE_REQUEST_LOGGING=false
```

#### Client Settings
```python
# Use connection pooling
transport = StreamableHttpTransport(
    "http://127.0.0.1:8000/mcp",
    timeout=30.0  # Adjust timeout
)

# Implement client-side caching
```

## Security Considerations

1. **Network Security**: Run behind a reverse proxy with SSL/TLS
2. **Access Control**: Implement authentication/authorization if needed
3. **CORS Policy**: Configure specific origins instead of wildcard
4. **Resource Limits**: Set appropriate connection and timeout limits
5. **Monitoring**: Enable logging and monitoring for security events

## Migration from STDIO

To migrate from STDIO to HTTP transport:

1. **Update Configuration**:
   ```bash
   export MCP_TRANSPORT=http
   ```

2. **Update Client Code**:
   ```python
   # Old: STDIO transport
   client = Client("path/to/mcp_server.py")
   
   # New: HTTP transport  
   transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
   client = Client(transport)
   ```

3. **Test Deployment**: Use integration tests to verify functionality

4. **Monitor Performance**: Check connection metrics and server health

## Support

For issues and questions:
- Check server logs with `MCP_LOG_LEVEL=DEBUG`
- Use `server_status` tool for diagnostics
- Review ChromaDB connection settings
- Test with minimal client first