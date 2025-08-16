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

## Development Commands

**Package Management (uv)**:
- `uv sync` - Install dependencies and sync environment
- `uv add <package>` - Add new dependency
- `uv run python main.py` - Run main application
- `uv run python -m <module>` - Run specific module

**RAG Operations**:
- `cd rag_store && uv run python store_embeddings.py` - Store documents to ChromaDB
- `cd rag_fetch && uv run python search_similarity.py` - Test similarity search
- `uv run python test_search.py` - Test MCP-compatible search responses

## Architecture

**Project Structure**:
- `main.py` - Application entry point
- `data/` - Centralized database storage
  - `chroma_db_google/` - Google embeddings database
  - `chroma_db_openai/` - OpenAI embeddings database (if used)
- `mcp_server/` - MCP (Model Context Protocol) server implementation
- `rag_fetch/` - Document retrieval and search functionality
  - `search_similarity.py` - Semantic search with MCP-compatible responses
- `rag_store/` - Document storage and embedding management
  - `store_embeddings.py` - Store documents to ChromaDB
  - `facts.txt` - Sample document collection

**MCP Integration Design**:
The RAG system will be exposed through MCP server tools, allowing AI assistants to:
- Query document collections using semantic search
- Retrieve relevant context for answering questions
- Add new documents to the knowledge base
- Manage embeddings and vector storage

**Core Dependencies**:
- **ChromaDB** (>=1.0.17) - Vector database for embeddings storage
- **LangChain** (>=0.3.27) - RAG orchestration framework
- **LangChain-Chroma** (>=0.2.5) - ChromaDB integration
- **LangChain-Community** (>=0.3.27) - Community integrations
- **LangChain-Google-GenAI** (>=2.0.10) - Google AI integration
- **LangChain-OpenAI** (>=0.3.30) - OpenAI integration
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

## Development Notes

- Uses `uv` for fast dependency management instead of pip
- ChromaDB collections: Default collection for storage, named collections for organization
- Centralized database structure in `data/` folder for both storage and retrieval
- MCP-ready: JSON responses designed for Model Context Protocol integration
- Error handling: Graceful fallbacks and meaningful error messages