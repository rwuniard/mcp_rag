# RAG Fetch - Document Search & Retrieval Service

A professional semantic search and retrieval service for RAG (Retrieval-Augmented Generation) systems. Provides fast similarity search across vector-embedded documents with MCP (Model Context Protocol) integration for AI assistants.

## 🎯 Purpose

RAG Fetch is the **search microservice** that:
- Performs semantic similarity search across stored documents
- Returns MCP-compatible JSON responses for AI assistants
- Provides both CLI and MCP server interfaces
- Integrates with ChromaDB vector databases

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in this directory:
```bash
# Required for Google embeddings (default)
GOOGLE_API_KEY=your_google_api_key_here

# Optional for OpenAI embeddings
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Ensure Documents are Indexed

Make sure you have documents stored by the RAG Store service:
```bash
# Check if vector database exists
ls ../../../data/chroma_db_google/

# If empty, run RAG Store first
python main.py store
```

### 3. Search Documents

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
- **Purpose**: Core semantic search functionality
- **Technology**: ChromaDB + LangChain + Google/OpenAI embeddings
- **Features**: Similarity search with scores, MCP-compatible JSON responses
- **Models**: Google `text-embedding-004` (default), OpenAI `text-embedding-ada-002`

### **MCP Server** (`mcp_server.py`)
- **Purpose**: Model Context Protocol server for AI assistant integration
- **Framework**: FastMCP
- **Tools**: `search_documents(query, limit)` 
- **Response**: Structured JSON with content, metadata, and relevance scores

### **CLI Interface** (`cli.py`)
- **Purpose**: Command-line search interface
- **Usage**: `rag-fetch-cli "search query"`
- **Features**: Human-friendly output, error handling

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

### **Adding to Claude Desktop**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/Users/YOUR_USERNAME/Projects/python/mcp_rag",
        "run", "python", "src/rag_fetch/mcp_server.py"
      ]
    }
  }
}
```

### **Adding to Cursor**

Add to Cursor MCP configuration:

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/absolute/path/to/mcp_rag",
        "run", "python", "src/rag_fetch/mcp_server.py"
      ]
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
```

### **Model Selection**
```python
from rag_fetch.search_similarity import ModelVendor

# Use Google embeddings (default)
ModelVendor.GOOGLE

# Use OpenAI embeddings
ModelVendor.OPENAI
```

### **Database Paths**
- **Google**: `../../../data/chroma_db_google/`
- **OpenAI**: `../../../data/chroma_db_openai/`

## 🔧 API Reference

### **Core Functions**

```python
# Load vector database
vectorstore = load_vectorstore(ModelVendor.GOOGLE)

# Basic similarity search
documents = search_similarity(query, vectorstore, k=6)

# Search with JSON response
json_result = search_similarity_with_json_result(query, vectorstore, number_result=6)

# MCP tool wrapper
mcp_response = similarity_search_mcp_tool(query, ModelVendor.GOOGLE, limit=6)
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
- **Data Source**: ChromaDB vector databases (created by RAG Store)
- **Output**: Structured JSON responses with content and metadata

**Microservices Flow**:
```
AI Assistant → MCP Server → RAG Fetch → ChromaDB → Search Results
     ↓
User Query → CLI → RAG Fetch → ChromaDB → Human-friendly Output
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

**"Database not found" error**:
```bash
# Solution: Run RAG Store first to create the database
python main.py store
```

**"API key required" error**:
```bash
# Solution: Add API key to .env file
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

**No search results**:
```bash
# Check if documents are stored
ls ../../../data/chroma_db_google/
# If empty, run document ingestion first
```

## 📄 License

Part of the MCP RAG project - MIT License