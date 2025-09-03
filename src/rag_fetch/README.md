# RAG Fetch - Document Search & Retrieval Service

A professional semantic search and retrieval service for RAG (Retrieval-Augmented Generation) systems. Provides fast similarity search across vector-embedded documents with MCP (Model Context Protocol) integration for AI assistants.

## 🎯 Purpose

RAG Fetch is the **search microservice** that:
- Performs semantic similarity search across stored documents
- Returns MCP-compatible JSON responses for AI assistants
- Provides both CLI and MCP server interfaces
- Connects to ChromaDB server via HTTP client

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in this directory:
```bash
# Required for Google embeddings (default)
GOOGLE_API_KEY=your_google_api_key_here

# Optional for OpenAI embeddings
OPENAI_API_KEY=your_openai_api_key_here

# ChromaDB Server Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION_NAME=langchain
```

### 2. Start ChromaDB Server

Start the ChromaDB server before searching:
```bash
# Start ChromaDB server (from project root)
./scripts/chromadb-server.sh start

# Check server health
./scripts/chromadb-server.sh health
```

### 3. Ensure Documents are Indexed

Make sure you have documents stored by the RAG Store service:
```bash
# Store documents to ChromaDB server
python main.py store
```

### 4. Search Documents

```bash
# From project root - CLI search
python main.py search "machine learning concepts"

# Or directly
python src/rag_fetch/cli.py "artificial intelligence"

# Or using the CLI command (if installed)
rag-fetch-cli "interesting facts about animals"

# Start MCP server for AI assistants
python main.py server
# Or: rag-mcp-server

# Start with HTTPS (SSL/TLS encryption)
export MCP_USE_SSL=true
export MCP_SSL_CERT_PATH=/path/to/cert.pem
export MCP_SSL_KEY_PATH=/path/to/key.pem
rag-mcp-server
# Server available at https://127.0.0.1:8000/mcp
```

## 📁 Project Structure

```
src/rag_fetch/
├── README.md                 # This file
├── .env                     # Environment variables
├── search_similarity.py     # Core search functionality
├── mcp_server.py           # MCP server implementation
└── cli.py                  # Command-line interface
```

## 🔧 Components

### **Search Similarity** (`search_similarity.py`)
- **Purpose**: Core semantic search functionality with real-time data access
- **Technology**: ChromaDB HTTP Client + LangChain + Google/OpenAI embeddings
- **Features**: Similarity search with scores, MCP-compatible JSON responses, cached connections
- **Models**: Google `text-embedding-004` (default), OpenAI `text-embedding-ada-002`
- **Architecture**: Client-server with persistent HTTP connections to ChromaDB

### **MCP Server** (`mcp_server.py`)
- **Purpose**: Model Context Protocol server for AI assistant integration
- **Framework**: FastMCP with HTTP/HTTPS transport support
- **Tools**: `search_documents(query, limit)`, `server_status()`, `list_active_connections()`
- **Transport**: HTTP (default), HTTPS (SSL/TLS), STDIO (debug mode)
- **Response**: Structured JSON with content, metadata, and relevance scores
- **Real-time Data**: Server architecture ensures immediate access to new documents
- **Security**: SSL/TLS encryption support for production deployments

### **CLI Interface** (`cli.py`)
- **Purpose**: Command-line search interface
- **Usage**: `rag-fetch-cli "search query"`
- **Features**: Human-friendly output, error handling

## 🔄 Real-time Data Access

### **Problem Solved**
Previously, when new documents were added to ChromaDB via RAG Store, the MCP server wouldn't see them until manually restarted due to file-based ChromaDB internal caching.

### **Solution Architecture**
The client-server architecture provides **real-time data freshness** with three key components:

#### **1. ChromaDB HTTP Client**
```python
def get_chromadb_client() -> chromadb.Client:
    """Connect to ChromaDB server via HTTP."""
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    client.heartbeat()  # Test connection
    return client
```

#### **2. Cached HTTP Connections**
```python
def get_cached_vectorstore(model_vendor: ModelVendor, collection_name: str = None):
    """Get vectorstore with cached HTTP connections."""
    # 30-second TTL for connection performance
    # Server ensures data freshness automatically
    # Cached connections per model/collection
```

#### **3. Server-Guaranteed Freshness**
```python
def similarity_search_mcp_tool(query: str, ...):
    """MCP tool with server-guaranteed fresh data."""
    # Uses cached HTTP connection to ChromaDB server
    vectorstore = get_cached_vectorstore(model_vendor, collection)
    # Server is single source of truth for data
```

### **Performance Characteristics**
- **HTTP Client**: Persistent connections with minimal overhead
- **Connection Caching**: 30-second TTL reduces connection establishment costs
- **Memory Impact**: Minimal (single cached connection per model/collection)
- **Error Handling**: Clear error messages if server unavailable

### **Benefits**
- ✅ **Zero Downtime**: No MCP server restarts needed
- ✅ **Always Fresh**: Server ensures all clients see latest data immediately
- ✅ **Server Architecture**: Centralized ChromaDB server with HTTP API
- ✅ **Docker Integration**: Easy server management with Docker Compose
- ✅ **Production Ready**: Comprehensive error handling and monitoring

## 🔍 Search Functionality

### **Basic Similarity Search**
```python
from rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor

# Search with Google embeddings (default)
results = similarity_search_mcp_tool(
    query="machine learning algorithms",
    model_vendor=ModelVendor.GOOGLE,
    limit=6
)
```

### **MCP Tool Integration**
```python
# Used by AI assistants via MCP
search_documents(
    query="What are the privacy laws in California?",
    limit=6
)
```

### **Response Format**
```json
{
  "query": "machine learning algorithms",
  "results": [
    {
      "content": "Machine learning is a subset of artificial intelligence...",
      "metadata": {
        "source": "ai_handbook.pdf",
        "chunk_id": "chunk_0",
        "document_id": "ai_handbook_pdf",
        "page": 15
      },
      "relevance_score": 0.89
    }
  ],
  "total_results": 3,
  "status": "success"
}
```

## 🤖 MCP Server Integration

### **Available Tools**

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `search_documents` | Semantic document search | `query` (string), `limit` (int, default: 6) | JSON with results, metadata, scores |
| `server_status` | Get server status and metrics | None | JSON with server config, transport, and connection metrics |
| `list_active_connections` | Monitor active connections | None | JSON with connection details (HTTP/HTTPS mode only) |

### **Adding to Claude Desktop**

#### Option 1: HTTP Transport (Default)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

#### Option 2: HTTPS Transport (Secure)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http", 
      "url": "https://127.0.0.1:8002/mcp"
    }
  }
}
```

**For MCP Inspector with HTTPS:**
```bash
# Trust the self-signed certificate
export NODE_EXTRA_CA_CERTS=$(pwd)/tests/ssl_certs/ca-cert.pem
npx @modelcontextprotocol/inspector

# Then connect to: https://127.0.0.1:8002/mcp
```

#### Option 3: STDIO Transport (Debug)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/Users/YOUR_USERNAME/Projects/python/mcp_rag",
        "run", "python", "src/rag_fetch/mcp_server.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### **Adding to Cursor**

#### Option 1: HTTP Transport (Default)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http",
      "url": "http://127.0.0.1:8002/mcp"
    }
  }
}
```

#### Option 2: HTTPS Transport (Secure)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http",
      "url": "https://127.0.0.1:8002/mcp"
    }
  }
}
```

#### Option 3: STDIO Transport (Debug)
```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/absolute/path/to/mcp_rag",
        "run", "python", "src/rag_fetch/mcp_server.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## 🎛️ Configuration

### **Environment Variables**
```bash
# Google AI (default)
GOOGLE_API_KEY=your_google_api_key

# OpenAI (alternative)
OPENAI_API_KEY=your_openai_api_key

# ChromaDB Server
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# MCP Server Configuration
MCP_TRANSPORT=http              # Transport: http, stdio
MCP_HOST=127.0.0.1              # HTTP server host
MCP_PORT=8000                   # HTTP server port

# HTTPS/SSL Configuration (Optional)
MCP_USE_SSL=true                # Enable HTTPS
MCP_SSL_CERT_PATH=/path/to/cert.pem  # SSL certificate
MCP_SSL_KEY_PATH=/path/to/key.pem    # SSL private key
MCP_ENVIRONMENT=production      # Environment: production or development
MCP_SSL_VERIFY_MODE=strict      # Verification: strict, relaxed, none
```

### **Model Selection**
```python
from rag_fetch.search_similarity import ModelVendor

# Use Google embeddings (default)
ModelVendor.GOOGLE

# Use OpenAI embeddings
ModelVendor.OPENAI
```

### **ChromaDB Server**
- **Server URL**: `http://localhost:8000`
- **Data Storage**: `../../../data/chroma_data/`
- **Management**: `./scripts/chromadb-server.sh`

## 🔧 API Reference

### **Core Functions**

```python
# Load vector database
vectorstore = load_vectorstore(ModelVendor.GOOGLE)

# Basic similarity search
documents = search_similarity(query, vectorstore, k=6)

# Search with JSON response
json_result = search_similarity_with_json_result(query, vectorstore, number_result=6)

# MCP tool wrapper (with auto-refresh)
mcp_response = similarity_search_mcp_tool(query, ModelVendor.GOOGLE, limit=6)

# Auto-refresh functions (new in latest version)
success = refresh_vectorstore_data(vectorstore)
cached_vectorstore = get_cached_vectorstore(ModelVendor.GOOGLE)
```

### **Search Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Natural language search query |
| `model_vendor` | ModelVendor | GOOGLE | Embedding model to use |
| `limit` | int | 6 | Maximum number of results |
| `collection` | string | None | Specific collection to search |

## 🔍 Usage Examples

### **CLI Search**
```bash
# Simple search
rag-fetch-cli "What is Python?"

# Search from any directory
python src/rag_fetch/cli.py "machine learning concepts"
```

### **MCP Server**
```bash
# Start MCP server
rag-mcp-server

# Server provides 'search_documents' tool to AI assistants
```

### **Programmatic Usage**
```python
from rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor
import json

# Perform search
result_json = similarity_search_mcp_tool(
    "California privacy laws",
    ModelVendor.GOOGLE,
    limit=5
)

# Parse results
result = json.loads(result_json)
for doc in result["results"]:
    print(f"Content: {doc['content'][:100]}...")
    print(f"Source: {doc['metadata']['source']}")
    print(f"Score: {doc['relevance_score']}")
```

## 🏗️ Architecture Integration

RAG Fetch works as an **independent search microservice**:

- **Input**: Search queries via CLI, MCP, or API
- **Data Source**: ChromaDB server (populated by RAG Store)
- **Output**: Structured JSON responses with content and metadata

**Microservices Flow**:
```
AI Assistant → MCP Server → RAG Fetch → ChromaDB Server → Search Results
     ↓
User Query → CLI → RAG Fetch → ChromaDB Server → Human-friendly Output
```

## 🧪 Quality Features

### **Advanced Search**
- **Semantic Search**: Uses vector embeddings for meaning-based matching
- **Relevance Scoring**: Returns similarity scores for result ranking
- **Multiple Models**: Support for Google and OpenAI embedding models
- **Error Handling**: Graceful degradation with meaningful error messages

### **MCP Compatibility**
- **Structured JSON**: Standardized response format for AI tools
- **Metadata Rich**: Includes source files, page numbers, chunk IDs
- **Tool Discovery**: Proper MCP tool registration and documentation

### **Performance**
- **Fast Retrieval**: Optimized vector similarity search
- **Configurable Limits**: Adjustable result count for different use cases
- **Efficient Loading**: Smart database connection management
- **Secure Transport**: HTTPS/SSL encryption for production deployments

### **Security Features**
- **SSL/TLS Encryption**: Full HTTPS transport support for secure connections
- **Certificate Validation**: Comprehensive SSL certificate verification
- **Environment Awareness**: Development vs production security policies
- **Client Verification**: Optional CA certificate validation for client connections
- **Security Monitoring**: SSL configuration validation and certificate expiration warnings

### **SSL/HTTPS Troubleshooting**

**Self-Signed Certificate Connection Issues:**

When connecting to HTTPS endpoints with self-signed certificates, clients may show certificate verification errors like:
```
Error: unable to verify the first certificate
UNABLE_TO_VERIFY_LEAF_SIGNATURE
```

**Solution 1 - Trust the CA Certificate (Recommended):**
```bash
# For Node.js MCP clients (MCP Inspector, Claude Desktop, etc.)
# Run from the mcp_rag project root directory:
export NODE_EXTRA_CA_CERTS=$(pwd)/tests/ssl_certs/ca-cert.pem
npx @modelcontextprotocol/inspector

# Or with absolute path (replace with your actual project path):
export NODE_EXTRA_CA_CERTS=/Users/YOUR_USERNAME/Projects/python/mcp_rag/tests/ssl_certs/ca-cert.pem
npx @modelcontextprotocol/inspector

# For permanent use, add to your shell profile:
echo "export NODE_EXTRA_CA_CERTS=$(pwd)/tests/ssl_certs/ca-cert.pem" >> ~/.zshrc
```

**Solution 2 - Disable SSL Verification (Development Only):**
```bash
# SECURITY WARNING: Only use in development environments
NODE_TLS_REJECT_UNAUTHORIZED=0 npx @modelcontextprotocol/inspector
```

**Note on System Certificate Installation:**
Installing custom CA certificates system-wide on macOS is restricted by System Integrity Protection and requires disabling security features. For development purposes, **Solutions 1 and 2 above are recommended** as they work reliably without modifying system security settings.

**FastMCP Banner Display Issue:**
The FastMCP banner may show `http://` even when SSL is enabled. This is a cosmetic issue only - the server actually runs HTTPS correctly. Look for the Uvicorn log message showing `https://` for the actual protocol.

## 📊 Performance Metrics

### **Search Speed**
- **Typical Query**: < 200ms for 6 results
- **Large Database**: Scales with ChromaDB performance
- **Memory Usage**: < 100MB for typical workloads

### **Accuracy**
- **Embedding Quality**: Leverages Google's `text-embedding-004` model
- **Relevance Scores**: 0.0-1.0 scale for result ranking
- **Search Quality**: Optimized chunking from RAG Store improves relevance

## 🔗 Integration Examples

### **AI Assistant Usage**
```
User: "Can you find information about machine learning algorithms?"
AI Assistant: [Uses search_documents tool via MCP]
AI: "I found several relevant documents about machine learning algorithms..."
```

### **Development Workflow**
```bash
# 1. Store documents
python main.py store

# 2. Test search
python main.py search "test query"

# 3. Start MCP server for AI integration
python main.py server
```

## 🧪 Development

### **Testing**
```bash
# Test search functionality
python src/rag_fetch/search_similarity.py

# Run fetch-specific tests
python -m unittest tests.test_rag_fetch.test_search_similarity -v
```

### **Dependencies**
```toml
# Core dependencies
chromadb = ">=1.0.17"
fastmcp = ">=2.11.3"
langchain = ">=0.3.27"
langchain-chroma = ">=0.2.5"
langchain-google-genai = ">=2.0.10"
langchain-openai = ">=0.3.30"
python-dotenv = ">=1.1.1"
```

## 🔗 Related Services

- **RAG Store**: Document ingestion and vector storage service
- **Main CLI**: Unified command interface for both services
- **MCP Integration**: Model Context Protocol server for AI assistants

## 🛠️ Troubleshooting

### **Common Issues**

**"Cannot connect to ChromaDB server" error**:
```bash
# Solution: Start ChromaDB server first
./scripts/chromadb-server.sh start

# Check server health
./scripts/chromadb-server.sh health
```

**"API key required" error**:
```bash
# Solution: Add API key to .env file
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

**No search results**:
```bash
# Check if ChromaDB server is running
./scripts/chromadb-server.sh status

# If no documents, run document ingestion
python main.py store
```

### **Server Connection Troubleshooting**

**MCP server not seeing new documents**:
```bash
# Check ChromaDB server status
./scripts/chromadb-server.sh health

# Test search directly
python src/rag_fetch/search_similarity.py
# Should show latest documents immediately
```

**Connection timeout errors**:
```bash
# Check if server is running
./scripts/chromadb-server.sh status

# Check server logs for issues
./scripts/chromadb-server.sh logs

# Restart server if needed
./scripts/chromadb-server.sh restart
```

**Performance issues**:
```bash
# Check connection cache TTL (default 30 seconds)
# Server handles data freshness, cache optimizes connections
```

**Memory usage increasing over time**:
```bash
# Connection cache automatically manages memory:
python -c "from src.rag_fetch.search_similarity import _vectorstore_cache; _vectorstore_cache.clear()"
```

### **Development & Testing**

**Running server-specific tests**:
```bash
# Test server connection
python -c "from src.rag_fetch.search_similarity import get_chromadb_client; client = get_chromadb_client(); print('✅ Connected')"

# Test caching system
python -m pytest tests/test_rag_fetch/test_search_similarity.py::TestCachedVectorstore -v

# Test MCP tool with server
python -m pytest tests/test_rag_fetch/test_search_similarity.py -v
```

**Performance testing**:
```bash
# Benchmark search performance
python -c "
import time
from src.rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor

start = time.time()
result = similarity_search_mcp_tool('test query', ModelVendor.GOOGLE, limit=3)
print(f'Search took: {(time.time() - start) * 1000:.2f}ms')
"
```

## 🔄 Version History & Changelog

### **v3.0.0 - HTTPS/SSL Security** *(Latest)*
- ✅ **HTTPS/SSL Transport**: Full SSL/TLS encryption support for secure connections
- ✅ **Certificate Validation**: Comprehensive SSL certificate verification and monitoring
- ✅ **Security Features**: Production-grade security with certificate expiration warnings
- ✅ **Environment Policies**: Development vs production security configurations
- ✅ **Dual Transport**: HTTP (default), HTTPS (secure), STDIO (debug) transport modes
- ✅ **Enhanced MCP Tools**: Added `server_status()` and `list_active_connections()` monitoring tools
- ✅ **Backward Compatible**: Existing HTTP configurations continue to work unchanged

### **v2.0.0 - Client-Server Architecture**
- ✅ **Client-Server Architecture**: ChromaDB server with HTTP clients
- ✅ **Real-time Data Access**: Server ensures immediate data freshness
- ✅ **Docker Integration**: Easy ChromaDB server management
- ✅ **Cached Connections**: 30-second TTL for HTTP connection optimization
- ✅ **Server Management**: Complete start/stop/status/health commands
- ✅ **Production Ready**: Robust server-based architecture

### **v1.0.0 - Initial Release**
- ✅ **Core Search Functionality**: Semantic similarity search with ChromaDB
- ✅ **MCP Integration**: Model Context Protocol server for AI assistants
- ✅ **Multi-Model Support**: Google and OpenAI embedding models
- ✅ **CLI Interface**: Command-line search capabilities
- ✅ **Production Ready**: Comprehensive error handling and testing

## 📄 License

Part of the MCP RAG project - MIT License