from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from enum import Enum
from pathlib import Path
import os
try:
    from .document_processor import ProcessorRegistry
    from .pdf_processor import PDFProcessor
    from .text_processor import TextProcessor
except ImportError:
    # Fallback for direct execution
    from document_processor import ProcessorRegistry
    from pdf_processor import PDFProcessor
    from text_processor import TextProcessor

# Load .env from the same directory as this script
load_dotenv(Path(__file__).parent / ".env")
print(f"Loaded .env from {Path(__file__).parent / '.env'}")

# Configuration - use same structure as search_similarity.py
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class ModelVendor (Enum):
    OPENAI = "openai"
    GOOGLE = "google"

def get_document_processor_registry() -> ProcessorRegistry:
    """
    Initialize and return a document processor registry with all supported processors.
    
    Returns:
        ProcessorRegistry configured with PDF and Text processors
    """
    registry = ProcessorRegistry()
    
    # Register all available processors
    registry.register_processor(PDFProcessor())
    registry.register_processor(TextProcessor())
    
    return registry

def process_documents_from_directory(directory_path: Path) -> list[Document]:
    """
    Process all supported documents from directory using the processor registry.
    
    Args:
        directory_path: Path to directory containing documents
        
    Returns:
        List of processed Document objects
    """
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    registry = get_document_processor_registry()
    supported_extensions = registry.get_supported_extensions()
    
    all_documents = []
    
    # Process all files with supported extensions
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                processor = registry.get_processor_for_file(file_path)
                if processor:
                    print(f"Processing {processor.file_type_description}: {file_path.name}")
                    docs = registry.process_document(file_path)
                    all_documents.extend(docs)
                    print(f"  ✓ Extracted {len(docs)} chunks using {processor.processor_name}")
                else:
                    print(f"  ⚠ No processor found for {file_path.name}")
            except Exception as e:
                print(f"  ✗ Error processing {file_path.name}: {e}")
    
    if not all_documents:
        print(f"No supported documents found in {directory_path}")
        print(f"Supported extensions: {sorted(supported_extensions)}")
    
    return all_documents

# Legacy functions for backward compatibility
def load_txt_documents(file_path):
    """Load documents from text files (legacy function)."""
    registry = get_document_processor_registry()
    return registry.process_document(Path(file_path))

def process_text_files(directory_path: Path) -> list[Document]:
    """Process all .txt files in directory (legacy function)."""
    documents = []
    registry = get_document_processor_registry()
    
    for txt_file in directory_path.glob("*.txt"):
        try:
            print(f"Processing text file: {txt_file.name}")
            docs = registry.process_document(txt_file)
            documents.extend(docs)
            print(f"  ✓ Loaded {len(docs)} chunks from {txt_file.name}")
        except Exception as e:
            print(f"  ✗ Error processing {txt_file.name}: {e}")
    return documents

def process_pdf_files(directory_path: Path) -> list[Document]:
    """Process all .pdf files in directory (legacy function)."""
    documents = []
    registry = get_document_processor_registry()
    
    for pdf_file in directory_path.glob("*.pdf"):
        try:
            print(f"Processing PDF: {pdf_file.name}")
            docs = registry.process_document(pdf_file)
            documents.extend(docs)
            print(f"  ✓ Extracted {len(docs)} chunks using RecursiveCharacterTextSplitter")
        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {e}")
    return documents

def load_documents_from_directory(directory_path: Path) -> list[Document]:
    """Load all supported documents from directory (legacy function)."""
    return process_documents_from_directory(directory_path)

def ensure_data_directory(model_vendor: ModelVendor) -> Path:
    """Ensure the data directory exists for the specified model vendor."""
    if model_vendor == ModelVendor.OPENAI:
        db_path = DATA_DIR / "chroma_db_openai"
    elif model_vendor == ModelVendor.GOOGLE:
        db_path = DATA_DIR / "chroma_db_google"
    else:
        raise ValueError(f"Unsupported model vendor: {model_vendor}")
    
    db_path.mkdir(parents=True, exist_ok=True)
    return db_path

def load_embedding_model(model_vendor: ModelVendor):
    """Load the embedding model based on the vendor."""
    if model_vendor == ModelVendor.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return OpenAIEmbeddings(openai_api_key=api_key)
    elif model_vendor == ModelVendor.GOOGLE:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported model vendor: {model_vendor}")

def get_text_splitter():
    """Get optimized text splitter for mixed factual content."""
    return CharacterTextSplitter(
        separator="\n",
        chunk_size=300,  # Increased from 200 for better context
        chunk_overlap=50  # Added overlap for better continuity
    )

def store_to_chroma(documents: list[Document], model_vendor: ModelVendor) -> Chroma:
    """Store documents to ChromaDB using the centralized data directory."""
    # Get the database path
    db_path = ensure_data_directory(model_vendor)
    
    # Get the embedding model
    embedding_model = load_embedding_model(model_vendor)
    
    # Create vectorstore
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=str(db_path)
    )
    
    print(f"Stored {len(documents)} documents to {db_path}")
    return vectorstore

def main():
    """Store documents (text and PDF) to ChromaDB using Google embeddings."""
    print("Store embeddings to Chroma!")
    
    # Use the new unified document processing
    data_source_dir = Path("./data_source")
    
    try:
        all_documents = process_documents_from_directory(data_source_dir)
        
        if not all_documents:
            print("No documents found. Please ensure you have supported files in the data_source directory.")
            print("Supported formats:")
            registry = get_document_processor_registry()
            for processor_name, processor in registry.get_all_processors().items():
                print(f"  - {processor.file_type_description}")
            return
        
        print(f"Total documents to store: {len(all_documents)}")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    # Store documents using Google embeddings
    vectorstore = store_to_chroma(all_documents, ModelVendor.GOOGLE)
    print(f"Successfully stored documents. Database location: {DATA_DIR / 'chroma_db_google'}")
    
    # Test the storage by doing a quick search
    test_results = vectorstore.similarity_search("interesting fact", k=6)
    print(f"Test search returned {len(test_results)} results")
    for i, result in enumerate(test_results, 1): 
        print(f"Result {i}:")
        print(f"Content: {result.page_content[:200]}...")
        print(f"Metadata: {result.metadata}")
        print("--------------------------------")

    query = "Find me a python class example."
    print(f"Query: {query}")
    print("--------------------------------")
    test_results_pdf = vectorstore.similarity_search(query, k=3)
    print(f"Test search returned {len(test_results_pdf)} results")
    for i, result_pdf in enumerate(test_results_pdf, 1): 
        print(f"Result {i}:")
        print(f"Content: {result_pdf.page_content[:200]}...")
        print(f"Metadata: {result_pdf.metadata}")
        print("--------------------------------")



if __name__ == "__main__":
    main()
