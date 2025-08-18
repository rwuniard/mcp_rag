# RAG Store - Document Ingestion Service

A professional document processing and storage service for RAG (Retrieval-Augmented Generation) systems. Converts PDF and text documents into searchable vector embeddings using ChromaDB.

## 🎯 Purpose

RAG Store is the **ingestion microservice** that:
- Processes PDF and text documents 
- Converts them into vector embeddings
- Stores them in ChromaDB for semantic search
- Optimizes chunking for better search quality

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in this directory:
```bash
# Required for Google embeddings
GOOGLE_API_KEY=your_google_api_key_here

# Optional for OpenAI embeddings
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Add Documents

Place your documents in the `data_source/` directory:
```
src/rag_store/data_source/
├── your_document.pdf
├── facts.txt
└── other_files.pdf
```

Supported formats:
- **PDF files** (`.pdf`) - Processed with PyPDFLoader + RecursiveCharacterTextSplitter
- **Text files** (`.txt`) - Processed with CharacterTextSplitter

### 3. Run Document Ingestion

```bash
# From project root
python main.py store

# Or directly
python src/rag_store/store_embeddings.py

# Or using the CLI command (if installed)
rag-store-cli store
```

## 📁 Project Structure

```
src/rag_store/
├── README.md                 # This file
├── .env                     # Environment variables
├── data_source/            # Input documents directory
│   ├── *.pdf              # PDF documents
│   └── *.txt              # Text documents
├── pdf_processor.py        # PDF processing and chunking
├── store_embeddings.py     # Main ingestion script
└── cli.py                 # Command-line interface
```

## 🔧 Components

### **PDF Processor** (`pdf_processor.py`)
- **Purpose**: Extract and chunk text from PDF documents
- **Technology**: PyPDFLoader + RecursiveCharacterTextSplitter
- **Parameters**: 1800 chars with 270 overlap (industry best practices)
- **Features**: Page number tracking, metadata extraction, error handling

### **Store Embeddings** (`store_embeddings.py`)
- **Purpose**: Convert documents to vectors and store in ChromaDB
- **Models**: Google (`text-embedding-004`) and OpenAI support
- **Database**: ChromaDB with separate collections per model
- **Output**: Stored in `../../../data/chroma_db_google/` or `chroma_db_openai/`

### **CLI Interface** (`cli.py`)
- **Purpose**: Command-line entry point for document ingestion
- **Usage**: `rag-store-cli store`
- **Features**: Usage help, environment validation

## 📊 Processing Details

### **PDF Processing**
- **Loader**: PyPDFLoader (LangChain integration)
- **Splitter**: RecursiveCharacterTextSplitter
- **Chunk Size**: 1800 characters
- **Overlap**: 270 characters
- **Metadata**: Page numbers, document properties, chunk IDs

### **Text Processing** 
- **Loader**: TextLoader (LangChain)
- **Splitter**: CharacterTextSplitter
- **Chunk Size**: 300 characters
- **Overlap**: 50 characters
- **Separator**: Double newlines (`\n\n`)

### **Embedding Models**

| Model | Provider | Dimensions | Use Case |
|-------|----------|------------|----------|
| `text-embedding-004` | Google | 768 | Default, high quality |
| `text-embedding-ada-002` | OpenAI | 1536 | Alternative option |

## 🗄️ Database Structure

Documents are stored in ChromaDB collections:

```
data/
├── chroma_db_google/       # Google embeddings
│   ├── chroma.sqlite3     # SQLite database
│   └── [collection data]  # Vector data
└── chroma_db_openai/      # OpenAI embeddings (if used)
    ├── chroma.sqlite3
    └── [collection data]
```

**Collection Schema**:
- **Document Content**: Chunked text content
- **Metadata**: Source file, page numbers, chunk IDs
- **Embeddings**: Vector representations (768d for Google, 1536d for OpenAI)

## 🎛️ Configuration

### **Environment Variables**
```bash
# Required
GOOGLE_API_KEY=your_key_here

# Optional  
OPENAI_API_KEY=your_key_here
```

### **Model Selection**
```python
# In store_embeddings.py
from rag_store.store_embeddings import ModelVendor

# Use Google (default)
load_embedding_model(ModelVendor.GOOGLE)

# Use OpenAI
load_embedding_model(ModelVendor.OPENAI)
```

## 🔍 Usage Examples

### **Basic Document Processing**
```bash
# Add documents to data_source/
cp ~/Documents/*.pdf src/rag_store/data_source/

# Process all documents
python main.py store
```

### **Check Processing Results**
```bash
# View processed documents count
ls data/chroma_db_google/
```

### **Programmatic Usage**
```python
from rag_store.store_embeddings import process_pdf_files, process_text_files
from pathlib import Path

# Process specific directory
pdf_docs = process_pdf_files(Path("my_pdfs/"))
text_docs = process_text_files(Path("my_texts/"))
```

## 🏗️ Architecture Integration

RAG Store is designed as an **independent microservice**:

- **Input**: Documents in `data_source/`
- **Output**: Vector database in `data/chroma_db_*/`
- **Consumers**: RAG Fetch service, MCP servers, other search services

**Microservices Flow**:
```
Documents → RAG Store → ChromaDB → RAG Fetch → Search Results
```

## 🧪 Quality Features

### **Optimized Chunking**
- **Evidence-based parameters** from 2024 industry benchmarks
- **RecursiveCharacterTextSplitter** for natural language boundaries
- **3% better relevance** vs. custom chunking methods

### **Error Handling**
- Graceful handling of corrupted PDFs
- Detailed logging and progress tracking
- Validation of environment variables

### **Performance**
- Efficient batch processing
- Memory-optimized for large documents
- Progress indicators for long operations

## 📝 Development

### **Testing**
```bash
# Run store-specific tests
python -m unittest tests.test_rag_store.test_pdf_processor -v
python -m unittest tests.test_rag_store.test_store_embeddings -v
```

### **Dependencies**
```toml
# Core dependencies
chromadb = ">=1.0.17"
langchain = ">=0.3.27"
langchain-chroma = ">=0.2.5"
langchain-community = ">=0.3.27"
langchain-google-genai = ">=2.0.10"
pypdf = ">=5.1.0"
python-dotenv = ">=1.1.1"
```

## 🔗 Related Services

- **RAG Fetch**: Semantic search and retrieval service
- **MCP Server**: Model Context Protocol integration
- **Main CLI**: Unified command interface

## 📄 License

Part of the MCP RAG project - MIT License