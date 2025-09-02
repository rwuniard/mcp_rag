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
Independent service for semantic search and MCP integration with **multi-client support**:
```bash
# Search documents via CLI
python main.py search "machine learning concepts"
rag-fetch-cli "interesting facts"

# Start MCP server for multiple clients (HTTP - default)
python main.py server
rag-mcp-server
# Server available at http://127.0.0.1:8000/mcp

# Start with HTTPS (SSL/TLS encryption)
export MCP_USE_SSL=true
export MCP_SSL_CERT_PATH=/path/to/cert.pem
export MCP_SSL_KEY_PATH=/path/to/key.pem
rag-mcp-server
# Server available at https://127.0.0.1:8000/mcp

# For debugging with single client (Claude Desktop)
export MCP_TRANSPORT=stdio
rag-mcp-server
```

## 🚀 Three Ways to Use


## Quick Start

1. **Install & Setup**:
   ```bash
   # Install dependencies (fast with uv)
   uv sync
   
   # Create environment files from templates
   cp src/rag_fetch/.env_template src/rag_fetch/.env
   cp src/rag_store/.env_template src/rag_store/.env
   # Add your GOOGLE_API_KEY to both .env files
   
   # Start ChromaDB server
   ./scripts/chromadb-server.sh start
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
   
   # Run comprehensive tests with HTML coverage
   python run_html_coverage.py --open
   ```

## Testing & Coverage

The project includes a comprehensive test suite with **86% coverage** and complete dependency management:

### Quick Coverage Commands
```bash
# Simple HTML coverage (recommended)
python run_html_coverage.py --open

# Alternative: Direct pytest 
uv run pytest --cov=src --cov-report=html

# Full-featured coverage tool (legacy)
python run_coverage.py --html-only --open
```

### Coverage Features & Configuration
- **HTML-Only Reports**: Clean `htmlcov/` directory with interactive line-by-line coverage
- **No File Clutter**: Configured to avoid generating `coverage.xml` or `coverage.json` files
- **Professional Configuration**: `.coveragerc` with 85% coverage threshold and proper exclusions
- **Browser Integration**: Automatically opens HTML reports with `--open` flag
- **Complete Dependencies**: All OCR, MHT, and document processing dependencies installed

### Current Coverage Status
- **Overall Project**: **86% coverage** (Above 85% requirement ✅)
- **Core Processors**: 95%+ coverage (PDF: 96%, Text: 95%, Word: 93%)
- **Document Processing**: 97% coverage with universal processor interface
- **168 Unit Tests**: Complete test coverage including OCR, BeautifulSoup, and Tesseract integration
  - **164 Pass in Full Suite**: All tests pass when run together with pytest
  - **4 Environment Isolation Tests**: Embedding tests skipped in full suite due to .env loading at import time
  - **Individual Validation**: Use `python test_embedding_isolation.py` to validate skipped tests work correctly
- **All Dependencies**: PyMuPDF, pytesseract, Pillow, BeautifulSoup4, langchain-unstructured  
- **Coverage Tools**: Both simple (`run_html_coverage.py`) and full-featured (`run_coverage.py`) scripts

## Development Commands

**Package Management (uv)**:
- `uv sync` - Install dependencies and sync environment
- `uv add <package>` - Add new dependency
- `uv run python main.py` - Run CLI application
- `uv run python mcp_server.py` - Start MCP server

**ChromaDB Server Management**:
- `./scripts/chromadb-server.sh start` - Start ChromaDB server
- `./scripts/chromadb-server.sh stop` - Stop ChromaDB server  
- `./scripts/chromadb-server.sh status` - Check server status
- `./scripts/chromadb-server.sh health` - Check server health
- `./scripts/chromadb-server.sh logs` - View server logs

**RAG Operations**:
- `python main.py store` - Store text and PDF documents to ChromaDB (RAG Store service)
- `python main.py search "<query>"` - Search documents via CLI (RAG Fetch service)
- `python main.py server` - Start MCP server for AI assistants (RAG Fetch service)
- `rag-store-cli store` - Direct access to ingestion service
- `rag-fetch-cli "<query>"` - Direct access to search service
- `rag-mcp-server` - Direct access to MCP server

**Testing & Quality**:
- `python run_html_coverage.py --open` - Run tests with HTML coverage and open report (recommended)
- `uv run pytest --cov=src --cov-report=html` - Direct pytest with HTML coverage  
- `python run_coverage.py --html-only --open` - Full-featured coverage tool with statistics
- `python run_coverage.py --console-only` - Console-only coverage report
- `uv run pytest tests/test_rag_store/ -v` - Test RAG Store service
- `uv run pytest tests/test_rag_fetch/ -v` - Test RAG Fetch service
- `python test_embedding_isolation.py` - Validate 4 embedding tests that require environment isolation

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
├── data/                     # Runtime databases and server storage
│   └── chroma_data/         # ChromaDB server persistent storage
├── scripts/                  # Server management utilities
│   └── chromadb-server.sh   # ChromaDB server management wrapper
├── setup_chroma_db/          # ChromaDB server setup and configuration
│   ├── chromadb-server.sh   # Main ChromaDB server management script
│   └── docker-compose.yml   # ChromaDB server Docker configuration
├── main.py                  # Convenience router (store|search|server)
├── run_coverage.py          # Full-featured coverage tool (legacy)
├── run_html_coverage.py     # Simple HTML coverage runner
├── .coveragerc              # Coverage configuration (HTML-only)
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
The RAG system exposes document search through MCP tools with **dual transport support**:
- `search_documents(query, limit)` - Semantic search using Google embeddings
- `server_status()` - Get server metrics and connection information
- `list_active_connections()` - Monitor active HTTP connections (HTTP mode)
- **HTTP Transport** - Default mode supporting concurrent web and API clients  
- **HTTPS Transport** - Secure HTTP with SSL/TLS encryption for production deployments
- **STDIO Transport** - Debug mode for single-client usage (Claude Desktop)
- Returns JSON with content, metadata, and relevance scores

**🔄 Real-time Data Freshness**:
The MCP server now provides real-time data access without requiring restarts:
- **Client-Server Architecture**: ChromaDB server ensures all clients see fresh data immediately
- **Cached Connections**: Persistent HTTP connections cached for 30 seconds for performance
- **Server-Guaranteed Freshness**: ChromaDB server is single source of truth for all data
- **Zero Downtime**: No need to restart MCP server when adding new documents
- **Docker Integration**: Easy ChromaDB server management with Docker Compose

**Core Dependencies**:
- **ChromaDB** (>=1.0.17) - Vector database for embeddings storage
- **FastMCP** (>=2.11.3) - MCP server framework
- **LangChain** (>=0.3.27) - RAG orchestration framework
- **LangChain-Chroma** (>=0.2.5) - ChromaDB integration
- **LangChain-Community** (>=0.3.27) - Community integrations
- **LangChain-Google-GenAI** (>=2.0.10) - Google AI integration
- **LangChain-OpenAI** (>=0.3.30) - OpenAI integration (optional)
- **Google-GenerativeAI** (>=0.8.5) - Google's generative AI client
- **PyMuPDF** (>=1.26.4) - Advanced PDF processing with OCR support
- **pytesseract** (>=0.3.13) + **Pillow** (>=11.3.0) - OCR for image-based PDFs
- **BeautifulSoup4** (>=4.13.5) - HTML parsing for MHT/MHTML files
- **langchain-unstructured** (>=0.1.6) - Unstructured document processing
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
- ✅ **ChromaDB Client-Server Architecture**: Dockerized ChromaDB server with HTTP clients
- ✅ **PDF Processing**: Advanced RecursiveCharacterTextSplitter with page number tracking
- ✅ **Word Processing**: Docx2txtLoader with RecursiveCharacterTextSplitter for modern .docx files
- ✅ **Text Processing**: CharacterTextSplitter optimized for text and markdown files
- ✅ **Semantic Search**: Query documents using natural language with similarity scoring
- ✅ **MCP-Compatible Responses**: JSON-formatted responses ready for MCP integration
- ✅ **Multi-Model Support**: Google and OpenAI embedding models
- ✅ **Server-Based Storage**: ChromaDB server provides centralized, persistent data storage
- ✅ **Production Ready**: Complete document-to-search pipeline verified and tested
- ✅ **Professional Structure**: Modern Python package with src/tests organization
- ✅ **Comprehensive Testing**: 168 unit tests with complete dependency coverage (86%)
- ✅ **Dual Entry Points**: Both CLI and MCP server interfaces
- ✅ **Real-time Data Access**: MCP server sees new documents immediately without restarts
- ✅ **Persistent Connections**: Cached HTTP connections for optimal performance
- ✅ **Docker Integration**: Easy server management with scripts and Docker Compose

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
- **Advanced Text Extraction**: PyMuPDF with OCR fallback using Tesseract
- **OCR Integration**: Tesseract OCR for image-based PDFs with smart text detection
- **RecursiveCharacterTextSplitter**: Intelligent chunking at natural language boundaries
- **Multiple Extraction Methods**: PyMuPDF text → PyMuPDF blocks → Tesseract OCR fallback
- **Rich Metadata**: Page numbers, extraction methods, file properties, OCR investigation
- **Optimized Parameters**: Industry best-practice 1800 chars with 270 overlap (96% coverage)

**Word Document Processing**:
- **Modern Format Support**: Handles .docx files (Word 2007+) efficiently
- **Docx2txtLoader**: Reliable text extraction from .docx files
- **RecursiveCharacterTextSplitter**: Intelligent chunking at natural language boundaries
- **Fast Processing**: Optimized for speed and reliability
- **Optimized Chunking**: Medium-sized chunks (1000 chars, 150 overlap) for structured Word content

**MHT/MHTML Processing**:
- **Web Archive Support**: Handles .mht and .mhtml web page archive files
- **Dual Processing**: UnstructuredLoader primary, manual MIME parsing fallback
- **HTML Text Extraction**: BeautifulSoup4 for clean text extraction from HTML content
- **Email MIME Parsing**: Built-in email module for MIME message structure parsing
- **Optimized Chunking**: 1200 chars with 180 overlap for structured HTML content (79% coverage)

**General Features**:
- **Universal Document Support**: PDF, DOCX, TXT, MD, MHT/MHTML with specialized processors
- **Mixed Content Support**: Processes text, markdown, Word, PDF, and web archive files
- **Advanced Error Handling**: Graceful fallbacks, OCR investigation, encoding detection
- **Registry Pattern**: Dynamic processor selection by file extension with 97% interface coverage

### Chunking Technology (Evidence-Based)
- **PDF Method**: RecursiveCharacterTextSplitter with optimized 1800/270 parameters
- **Boundary Detection**: Splits at paragraphs → sentences → words → characters
- **Search Quality**: Proven 3% better relevance scores vs custom chunking
- **Text Files**: Enhanced CharacterTextSplitter with 300/50 parameters
- **Metadata Enhancement**: Comprehensive tracking including splitting method and PDF properties

## Environment Setup

Required environment variables in module `.env` files:

**src/rag_fetch/.env**:
```bash
GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here  # Optional, for OpenAI embeddings
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION_NAME=langchain
```

**src/rag_store/.env**:
```bash
GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here  # Optional, for OpenAI embeddings
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION_NAME=langchain
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

#### Option 1: HTTP Transport (Default - Recommended)
Start the server manually, then connect via HTTP:

```bash
# Start the HTTP server
cd /Users/YOUR_USERNAME/Projects/python/mcp_rag
rag-mcp-server
# Server runs at http://127.0.0.1:8000/mcp
```

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

#### Option 2: HTTPS Transport (Production - Secure)
For production deployments with SSL/TLS encryption:

```bash
# Start the HTTPS server with SSL certificates
cd /Users/YOUR_USERNAME/Projects/python/mcp_rag
export MCP_USE_SSL=true
export MCP_SSL_CERT_PATH=/path/to/your/cert.pem
export MCP_SSL_KEY_PATH=/path/to/your/key.pem
rag-mcp-server
# Server runs at https://127.0.0.1:8000/mcp
```

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http",
      "url": "https://127.0.0.1:8000/mcp"
    }
  }
}
```

#### Option 3: STDIO Transport (Debug Mode)
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

### Adding to Cursor

Add this to your Cursor MCP configuration:

**Location**: Cursor Settings → MCP Servers

#### Option 1: HTTP Transport (Default - Recommended)
Start the server manually first:

```bash
# Start the HTTP server
cd /absolute/path/to/mcp_rag
rag-mcp-server
# Server runs at http://127.0.0.1:8000/mcp
```

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

#### Option 2: HTTPS Transport (Production - Secure)
For production deployments with SSL/TLS encryption:

```bash
# Start the HTTPS server with SSL certificates
cd /absolute/path/to/mcp_rag
export MCP_USE_SSL=true
export MCP_SSL_CERT_PATH=/path/to/your/cert.pem
export MCP_SSL_KEY_PATH=/path/to/your/key.pem
rag-mcp-server
# Server runs at https://127.0.0.1:8000/mcp
```

```json
{
  "mcpServers": {
    "rag-knowledge-base": {
      "transport": "http",
      "url": "https://127.0.0.1:8000/mcp"
    }
  }
}
```

#### Option 3: STDIO Transport (Debug Mode)
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

### Configuration Steps

#### For HTTP Transport (Recommended)

1. **Set up environment**:
   ```bash
   # Copy and configure the environment file
   cp src/rag_fetch/.env_template src/rag_fetch/.env
   # Edit .env and add your GOOGLE_API_KEY
   ```

2. **Start the server**:
   ```bash
   # Start HTTP server (runs on port 8000 by default)
   rag-mcp-server
   ```

3. **Connect your AI client**: Use the HTTP configuration shown above

#### For HTTPS Transport (Production)

1. **Set up SSL certificates**:
   ```bash
   # For development - generate self-signed certificates:
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
     -subj "/C=US/ST=Test/L=Test/O=Dev/CN=localhost"
   
   # For production - use CA-signed certificates from your provider
   # Place cert.pem and key.pem in a secure location
   ```

2. **Configure environment**:
   ```bash
   # Copy and configure the environment file  
   cp src/rag_fetch/.env_template src/rag_fetch/.env
   # Edit .env and add:
   # GOOGLE_API_KEY=your_key_here
   # MCP_USE_SSL=true
   # MCP_SSL_CERT_PATH=/path/to/cert.pem
   # MCP_SSL_KEY_PATH=/path/to/key.pem
   ```

3. **Start the HTTPS server**:
   ```bash
   # Start HTTPS server (runs on port 8000 with SSL)
   rag-mcp-server
   ```

4. **Connect your AI client**: Use the HTTPS configuration shown above

#### For STDIO Transport (Debug Mode)

1. **Find your uv path**:
   ```bash
   which uv
   # Usually: /usr/local/bin/uv or /opt/homebrew/bin/uv
   ```

2. **Get absolute project path**:
   ```bash
   pwd
   # Use this path in the "directory" field
   ```

3. **Set environment variables**:
   ```bash
   # Copy and configure the environment file
   cp src/rag_fetch/.env_template src/rag_fetch/.env
   # Edit .env and add your GOOGLE_API_KEY
   ```

#### Common Setup Steps

1. **Ensure documents are stored**:
   ```bash
   python main.py store
   # or: rag-store-cli store
   ```

2. **Start ChromaDB server**:
   ```bash
   ./scripts/chromadb-server.sh start
   ```

### Available MCP Tools

Once connected, your AI assistant will have access to:

- **`search_documents`**: Search for relevant world facts and interesting information
  - Args: `query` (string), `limit` (optional int, default: 6)
  - Returns: JSON with search results, metadata, and relevance scores

- **`server_status`**: Get current server status and connection metrics
  - Args: None
  - Returns: JSON with server config, transport mode, and connection metrics

- **`list_active_connections`**: Monitor active connections (HTTP transport only)
  - Args: None  
  - Returns: JSON with detailed connection information and metrics

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
- **ChromaDB Server**: Dockerized ChromaDB server running on http://localhost:8000
- **Client-Server Architecture**: HTTP clients connect to centralized ChromaDB server
- **Multiple Models**: Support for both Google and OpenAI embeddings
- **Document Types**: Handles both text (.txt) and PDF (.pdf) files with optimized processing
- **Server Management**: Easy start/stop/status commands via `./scripts/chromadb-server.sh`

### Testing & Quality
- **Comprehensive Tests**: 168 unit tests covering all document types, OCR, MHT, and complete dependency stack
- **High Coverage**: 86% overall project coverage with 95%+ on core processors
- **Advanced Testing**: PDF with OCR, MHT/HTML parsing, BeautifulSoup integration, Tesseract OCR
- **Complete Dependencies**: All OCR, web archive, and document processing dependencies tested
- **Coverage Tools**: Simple `run_html_coverage.py` (pytest-based) + professional `run_coverage.py` (unittest-based)
- **Clean Reports**: HTML-only coverage reports, no file clutter, 85% coverage threshold
- **Multiple Runners**: pytest (recommended), unittest discover, both with uv integration
- **CI Ready**: Configured for automated testing with proper dependency management

### MCP Integration
- **Dual Interfaces**: Both standalone CLI and MCP server functionality
- **JSON Responses**: Structured responses designed for Model Context Protocol
- **Error Handling**: Graceful fallbacks and meaningful error messages
- **Production Ready**: Verified end-to-end pipeline from PDF to search results