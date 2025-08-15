# MCP RAG

A RAG (Retrieval-Augmented Generation) system built with Python that will be wrapped with MCP (Model Context Protocol). The project uses ChromaDB for vector storage, LangChain for orchestration, and Google's Generative AI. The core goal is to expose RAG functionality through MCP server interfaces, allowing AI assistants to query and retrieve relevant information from document collections.

## Development Commands

**Package Management (uv)**:
- `uv sync` - Install dependencies and sync environment
- `uv add <package>` - Add new dependency
- `uv run python main.py` - Run main application
- `uv run python -m <module>` - Run specific module

**Basic Execution**:
- `python main.py` - Run main application (currently prints hello message)

## Architecture

**Project Structure**:
- `main.py` - Application entry point
- `mcp_server/` - MCP (Model Context Protocol) server implementation - wraps RAG functionality as MCP tools
- `rag_fetch/` - Document retrieval and processing components
  - `retriever.py` - Document retrieval logic
- `rag_store/` - Vector storage and embeddings management
  - `store_embeddings` - Embedding storage functionality

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
- **LangChain-Google-GenAI** (>=2.0.10) - Google AI integration
- **Google-GenerativeAI** (>=0.8.5) - Google's generative AI client
- **python-dotenv** (>=1.1.1) - Environment variable management

**Technology Stack**:
- **Python 3.12+** required
- **uv** for fast dependency management
- **ChromaDB** for vector similarity search
- **LangChain** ecosystem for RAG pipeline
- **Google Generative AI** for embeddings and generation
- **MCP** for exposing RAG as standardized AI assistant tools

## Development Notes

- The project uses uv instead of pip for faster dependency resolution
- Environment variables likely needed for Google AI API keys (use .env file)
- Most implementation files are currently empty placeholders
- MCP server will provide standardized interface for AI assistants to access RAG functionality
- Focus on building reusable RAG components that can be easily exposed via MCP tools