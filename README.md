# MCP RAG - Microservices Architecture

A professional RAG (Retrieval-Augmented Generation) system built with Python and Model Context Protocol (MCP). This project implements a **microservices architecture** with independent document ingestion and search services for semantic document search using ChromaDB, LangChain, and Google's Generative AI.

## 🏗️ Microservices Architecture

### 📥 **RAG Store** - Document Ingestion Service
Independent service with **universal document processor interface** for processing and storing documents:
```bash
# Store documents to vector database (supports PDF, Word, TXT, MD)
python main.py store
rag-store-cli store
```

### 🔍 **RAG Fetch** - Search & Retrieval Service  
Independent service for semantic search and MCP integration:
```bash
# Search documents via CLI
python main.py search "machine learning concepts"
rag-fetch-cli "interesting facts"

# Start MCP server for AI assistants
python main.py server
rag-mcp-server
```

## 🚀 Three Ways to Use


## Quick Start

1. **Install & Setup**:
   ```bash
   # Install dependencies (fast with uv)
   uv sync
   
   # Create environment file
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

2. **Store Documents**:
   ```bash
   # Place your .txt, .md, .pdf, and .docx files in src/rag_store/data_source/
   python main.py store
   ```

3. **Search & Use**:
   ```bash
   # Command line search
   python main.py search "interesting facts about English"
   
   # Start MCP server for AI assistants
   python main.py server
   
   # Run comprehensive tests with coverage
   python run_coverage.py --open
   ```

## Testing & Coverage

The project includes a comprehensive test suite with a professional coverage tool:

### Coverage Tool Usage
```bash
# Run all tests with coverage and open HTML report
python run_coverage.py --open

# Generate both console and HTML reports
python run_coverage.py

# Console report only
python run_coverage.py --console-only

# HTML report only (no console output)
python run_coverage.py --html-only

# Skip HTML generation
python run_coverage.py --no-html
```

### Coverage Features
- **Professional HTML Reports**: Interactive coverage visualization with line-by-line analysis
- **Browser Integration**: Automatically opens HTML reports in your default browser
- **Multi-format Output**: Both console and HTML coverage reports
- **Test Statistics**: Comprehensive test execution metrics and timing
- **CI-Ready**: Suitable for continuous integration pipelines

### Current Coverage Status
- **Overall Project**: 70% coverage across all modules
- **Core Processors**: 95%+ coverage (Text, Word, PDF processors)
- **Document Processing**: 93%+ coverage
- **60+ Unit Tests**: Comprehensive test coverage for all major functionality

## Development Commands

**Package Management (uv)**:
- `uv sync` - Install dependencies and sync environment
- `uv add <package>` - Add new dependency
- `uv run python main.py` - Run CLI application
- `uv run python mcp_server.py` - Start MCP server

**RAG Operations**:
- `python main.py store` - Store text and PDF documents to ChromaDB (RAG Store service)
- `python main.py search "<query>"` - Search documents via CLI (RAG Fetch service)
- `python main.py server` - Start MCP server for AI assistants (RAG Fetch service)
- `rag-store-cli store` - Direct access to ingestion service
- `rag-fetch-cli "<query>"` - Direct access to search service
- `rag-mcp-server` - Direct access to MCP server

**Testing & Quality**:
- `python run_coverage.py` - Run comprehensive test suite with coverage reports
- `python run_coverage.py --open` - Run tests with coverage and open HTML report in browser
- `python -m unittest discover tests -v` - Run all unit tests
- `python -m unittest tests.test_rag_store.test_pdf_processor -v` - Test RAG Store
- `python -m unittest tests.test_rag_fetch.test_search_similarity -v` - Test RAG Fetch

## Architecture

**Microservices Project Structure**:
```
mcp_rag/
├── src/                      # Source packages (installable)
│   ├── rag_store/           # 📥 Document Ingestion Service
│   │   ├── README.md        # RAG Store documentation
│   │   ├── .env             # Service environment variables
│   │   ├── data_source/     # Input documents directory
│   │   ├── document_processor.py # Universal document processor interface
│   │   ├── pdf_processor.py # PDF text extraction and chunking
│   │   ├── text_processor.py # Text and Markdown processing
│   │   ├── store_embeddings.py # Vector storage to ChromaDB
│   │   └── cli.py           # rag-store-cli command
│   └── rag_fetch/           # 🔍 Search & Retrieval Service
│       ├── README.md        # RAG Fetch documentation
│       ├── .env             # Service environment variables
│       ├── search_similarity.py # Semantic search functionality
│       ├── mcp_server.py    # MCP server (rag-mcp-server)
│       └── cli.py           # rag-fetch-cli command
├── tests/                    # Unit tests (microservice structure)
│   ├── test_rag_store/      # RAG Store tests
│   │   ├── test_pdf_processor.py
│   │   ├── test_text_processor.py
│   │   ├── test_word_processor.py
│   │   └── test_store_embeddings.py
│   └── test_rag_fetch/      # RAG Fetch tests
│       └── test_search_similarity.py
├── data/                     # Runtime databases (shared)
│   ├── chroma_db_google/    # Google embeddings database
│   └── chroma_db_openai/    # OpenAI embeddings database
├── main.py                   # Convenience router (store|search|server)
├── run_coverage.py          # Comprehensive test coverage tool
└── pyproject.toml           # Package configuration with entry points
```

**Microservices Entry Points**:

| Service | CLI Command | Purpose | Usage |
|---------|-------------|---------|-------|
| **Router** | `python main.py` | Convenience router | `store\|search\|server` |
| **RAG Store** | `rag-store-cli` | Document ingestion | `rag-store-cli store` |
| **RAG Fetch** | `rag-fetch-cli` | Document search | `rag-fetch-cli "query"` |
| **MCP Server** | `rag-mcp-server` | AI assistant integration | Background MCP service |

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
- **PyPDF** (>=5.1.0) - PDF text extraction and processing
- **docx2txt** (>=0.8) - Word document text extraction
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
- ✅ **Universal Document Interface**: Extensible processor architecture for multiple document types
- ✅ **Multi-Format Support**: PDF, Word (DOCX), TXT, and Markdown files with optimized processing
- ✅ **Document Storage**: Store documents with ChromaDB vector embeddings
- ✅ **PDF Processing**: Advanced RecursiveCharacterTextSplitter with page number tracking
- ✅ **Word Processing**: Docx2txtLoader with RecursiveCharacterTextSplitter for modern .docx files
- ✅ **Text Processing**: CharacterTextSplitter optimized for text and markdown files
- ✅ **Semantic Search**: Query documents using natural language with similarity scoring
- ✅ **MCP-Compatible Responses**: JSON-formatted responses ready for MCP integration
- ✅ **Multi-Model Support**: Google and OpenAI embedding models
- ✅ **Centralized Database**: Unified data storage in `data/` directory
- ✅ **Production Ready**: Complete document-to-search pipeline verified and tested
- ✅ **Professional Structure**: Modern Python package with src/tests organization
- ✅ **Comprehensive Testing**: 42 unit tests with real PDF integration testing
- ✅ **Dual Entry Points**: Both CLI and MCP server interfaces

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

### Document Processing Features

**PDF Processing**:
- **Advanced Text Extraction**: Uses PyPDFLoader for better LangChain integration
- **RecursiveCharacterTextSplitter**: Intelligent chunking at natural language boundaries
- **Proven Search Quality**: 5/5 queries show better relevance vs custom chunking
- **Rich Metadata**: Includes page numbers, creation dates, author, and PDF properties
- **Optimized Parameters**: Industry best-practice 1800 chars with 270 overlap

**Word Document Processing**:
- **Modern Format Support**: Handles .docx files (Word 2007+) efficiently
- **Docx2txtLoader**: Reliable text extraction from .docx files
- **RecursiveCharacterTextSplitter**: Intelligent chunking at natural language boundaries
- **Fast Processing**: Optimized for speed and reliability
- **Optimized Chunking**: Medium-sized chunks (1000 chars, 150 overlap) for structured Word content

**General Features**:
- **Document-Type Aware**: Different strategies for PDFs, Word documents, text files, and markdown
- **Mixed Content Support**: Processes text (.txt), markdown (.md), Word (.docx), and PDF (.pdf) files
- **Error Handling**: Graceful handling of corrupted or unreadable files
- **Registry Pattern**: Dynamic processor selection by file extension

### Chunking Technology (Evidence-Based)
- **PDF Method**: RecursiveCharacterTextSplitter with optimized 1800/270 parameters
- **Boundary Detection**: Splits at paragraphs → sentences → words → characters
- **Search Quality**: Proven 3% better relevance scores vs custom chunking
- **Text Files**: Enhanced CharacterTextSplitter with 300/50 parameters
- **Metadata Enhancement**: Comprehensive tracking including splitting method and PDF properties

## Environment Setup

Required environment variables in `.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here  # Optional, for OpenAI embeddings
```

### IDE Configuration

To configure your IDE to use the correct Python interpreter and environment:

1. **Open Command Palette**: Press `Shift+Cmd+P` (macOS) or `Shift+Ctrl+P` (Windows/Linux)
2. **Select Python Interpreter**: Choose `Python: Select Interpreter`
3. **Enter Interpreter Path**: Select `Enter interpreter path...`
4. **Specify Virtual Environment**: Enter the absolute path to your virtual environment's Python executable:
   ```
   /absolute/path/to/your/project/.venv/bin/python
   ```

This ensures your IDE uses the correct virtual environment with all project dependencies installed via `uv sync`.

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
        "run", "python", "src/rag_fetch/mcp_server.py"
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
        "run", "python", "src/rag_fetch/mcp_server.py"
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

### Package Structure
- **Professional Python Package**: Follows src/tests best practices for Python development
- **Installable Package**: Can be installed with `pip install -e .` for development
- **Modern Tooling**: Uses `uv` for fast dependency management and `pytest` for testing
- **Type Safety**: Configured for modern Python development with proper imports

### Database & Storage
- **ChromaDB**: Vector database with centralized structure in `data/` folder
- **Multiple Models**: Support for both Google and OpenAI embeddings
- **Document Types**: Handles both text (.txt) and PDF (.pdf) files with optimized processing

### Testing & Quality
- **Comprehensive Tests**: 60+ unit tests covering document processing, PDF, text, Word, and search functionality
- **High Coverage**: 95%+ coverage on core processors (Text, Word, PDF) with overall 70% project coverage
- **Integration Testing**: Real PDF processing with `thinkpython.pdf` (394 chunks)
- **Interface Testing**: Universal document processor interface validation
- **Coverage Tool**: Professional `run_coverage.py` with HTML reports, browser integration, and CI support
- **Multiple Runners**: Custom runner, pytest, and unittest support
- **CI Ready**: Configured for automated testing and continuous integration

### MCP Integration
- **Dual Interfaces**: Both standalone CLI and MCP server functionality
- **JSON Responses**: Structured responses designed for Model Context Protocol
- **Error Handling**: Graceful fallbacks and meaningful error messages
- **Production Ready**: Verified end-to-end pipeline from PDF to search results