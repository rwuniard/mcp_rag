# MCP RAG

A RAG (Retrieval-Augmented Generation) system built with Python that will be wrapped with MCP (Model Context Protocol). The project uses ChromaDB for vector storage, LangChain for orchestration, and Google's Generative AI. The core goal is to expose RAG functionality through MCP server interfaces, allowing AI assistants to query and retrieve relevant information from document collections.

## Quick Start

1. **Setup Environment**:
   ```bash
   uv sync  # Install dependencies
   cp .env.example .env  # Create environment file
   # Add your GOOGLE_API_KEY to .env
   ```

2. **Store Documents**:
   ```bash
   cd rag_store
   uv run python store_embeddings.py  # Store facts.txt to ChromaDB
   ```

3. **Test Search**:
   ```bash
   cd rag_fetch
   uv run python search_similarity.py  # Test similarity search
   ```

4. **Start MCP Server**:
   ```bash
   uv run python mcp_server.py  # Start MCP server for AI assistants
   ```

## Development Commands

**Package Management (uv)**:
- `uv sync` - Install dependencies and sync environment
- `uv add <package>` - Add new dependency
- `uv run python main.py` - Run main application
- `uv run python -m <module>` - Run specific module

**RAG Operations**:
- `cd rag_store && uv run python store_embeddings.py` - Store documents to ChromaDB
- `cd rag_fetch && uv run python search_similarity.py` - Test similarity search
- `uv run python mcp_server.py` - Start MCP server for AI assistants

## Architecture

**Project Structure**:
- `main.py` - Application entry point
- `mcp_server.py` - MCP (Model Context Protocol) server for AI assistants
- `data/` - Centralized database storage
  - `chroma_db_google/` - Google embeddings database
  - `chroma_db_openai/` - OpenAI embeddings database (if used)
- `rag_fetch/` - Document retrieval and search functionality
  - `search_similarity.py` - Semantic search with MCP-compatible responses
- `rag_store/` - Document storage and embedding management
  - `store_embeddings.py` - Store documents to ChromaDB
  - `facts.txt` - Sample document collection

**MCP Integration Design**:
The RAG system exposes document search through a single MCP tool:
- `search_documents(query, limit)` - Semantic search using Google embeddings
- Returns JSON with content, metadata, and relevance scores
- Hardcoded to use Google embeddings for simplicity and consistency

**Core Dependencies**:
- **ChromaDB** (>=1.0.17) - Vector database for embeddings storage
- **FastMCP** (>=2.11.3) - MCP server framework
- **LangChain** (>=0.3.27) - RAG orchestration framework
- **LangChain-Chroma** (>=0.2.5) - ChromaDB integration
- **LangChain-Community** (>=0.3.27) - Community integrations
- **LangChain-Google-GenAI** (>=2.0.10) - Google AI integration
- **LangChain-OpenAI** (>=0.3.30) - OpenAI integration (optional)
- **Google-GenerativeAI** (>=0.8.5) - Google's generative AI client
- **python-dotenv** (>=1.1.1) - Environment variable management

**Technology Stack**:
- **Python 3.12+** required
- **uv** for fast dependency management
- **ChromaDB** for vector similarity search
- **LangChain** ecosystem for RAG pipeline
- **Google Generative AI** for embeddings and generation
- **MCP** for exposing RAG as standardized AI assistant tools

## Features

### Current Implementation
- ✅ **Document Storage**: Store text documents with ChromaDB vector embeddings
- ✅ **Semantic Search**: Query documents using natural language with similarity scoring
- ✅ **MCP-Compatible Responses**: JSON-formatted responses ready for MCP integration
- ✅ **Multi-Model Support**: Google and OpenAI embedding models
- ✅ **Centralized Database**: Unified data storage in `data/` directory

### MCP Response Format
```json
{
  "query": "What is interesting fact about the English language?",
  "results": [
    {
      "content": "Document content...",
      "metadata": {
        "source": "facts.txt",
        "chunk_id": null,
        "document_id": null
      },
      "relevance_score": 0.85
    }
  ],
  "total_results": 1,
  "status": "success"
}
```

## Environment Setup

Required environment variables in `.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here  # Optional, for OpenAI embeddings
```

## MCP Integration

### Adding to Claude Desktop

Add this to your Claude Desktop configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/Users/YOUR_USERNAME/Projects/python/mcp_rag",
        "run", "python", "mcp_server.py"
      ]
    }
  }
}
```

### Adding to Cursor

Add this to your Cursor MCP configuration:

**Location**: Cursor Settings → MCP Servers

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory", "/absolute/path/to/mcp_rag",
        "run", "python", "mcp_server.py"
      ]
    }
  }
}
```

### Configuration Steps

1. **Find your uv path** (after activating virtual environment):
   ```bash
   # Activate virtual environment first (if using one)
   # source venv/bin/activate  # or your preferred activation method
   
   which uv
   # Usually: /usr/local/bin/uv or /opt/homebrew/bin/uv
   # Note: Use the uv path from your activated environment
   ```

2. **Get absolute project path**:
   ```bash
   pwd
   # Use this path in the "directory" field
   ```

3. **Set environment variables** (create `.env` in project root):
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Ensure documents are stored**:
   ```bash
   cd rag_store && uv run python store_embeddings.py
   ```

### Available MCP Tools

Once connected, your AI assistant will have access to:

- **`search_documents`**: Search for relevant world facts and interesting information
  - Args: `query` (string), `limit` (optional int, default: 6)
  - Returns: JSON with search results, metadata, and relevance scores

### Example Usage in AI Chat

```
User: "Can you search for interesting facts about animals?"
AI: [Uses search_documents tool] Here are some fascinating animal facts I found...
```

## Development Notes

- Uses `uv` for fast dependency management instead of pip
- ChromaDB collections: Default collection for storage, named collections for organization
- Centralized database structure in `data/` folder for both storage and retrieval
- MCP-ready: JSON responses designed for Model Context Protocol integration
- Error handling: Graceful fallbacks and meaningful error messages