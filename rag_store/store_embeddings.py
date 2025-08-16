from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_core.embeddings import Embeddings
from enum import Enum
from pathlib import Path
import os
from pdf_processor import PDFProcessor

load_dotenv()

# Configuration - use same structure as search_similarity.py
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class ModelVendor (Enum):
    OPENAI = "openai"
    GOOGLE = "google"

def load_documents(file_path):
    """Load documents from text files."""
    loader = TextLoader(file_path)
    return loader.load_and_split(
        text_splitter=get_text_splitter()
    )

def load_pdf_documents(pdf_path: Path, chunk_size: int = None, chunk_overlap: int = None) -> list[Document]:
    """Load and process PDF documents with optimized chunking."""
    processor = PDFProcessor()
    return processor.pdf_to_documents(pdf_path, chunk_size, chunk_overlap)

def load_documents_from_directory(directory_path: Path) -> list[Document]:
    """Load documents from a directory containing text and PDF files with optimized chunking."""
    all_documents = []
    directory = Path(directory_path)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Process text files with optimized text chunking
    for txt_file in directory.glob("*.txt"):
        try:
            print(f"Processing text file: {txt_file.name}")
            docs = load_documents(str(txt_file))
            all_documents.extend(docs)
            print(f"  ✓ Loaded {len(docs)} chunks from {txt_file.name}")
        except Exception as e:
            print(f"  ✗ Error processing {txt_file.name}: {e}")
    
    # Process PDF files with RecursiveCharacterTextSplitter (proven better search quality)
    processor = PDFProcessor()
    
    # Use recursive method for better search quality
    pdf_files = [f for f in directory.glob("*.pdf") if f.is_file()]
    pdf_docs = []
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing PDF: {pdf_file.name}")
            docs = processor.pdf_to_documents_recursive(pdf_file)
            pdf_docs.extend(docs)
            print(f"  ✓ Extracted {len(docs)} chunks using RecursiveCharacterTextSplitter")
        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {e}")
    
    # Add PDF documents to the total collection
    all_documents.extend(pdf_docs)
    
    return all_documents

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
    
    # Try to load from current directory first
    current_dir = Path(".")
    all_documents = []
    
    # Load individual facts.txt if it exists
    facts_file = current_dir / "facts.txt"
    if facts_file.exists():
        fact_doc = load_documents(str(facts_file))
        all_documents.extend(fact_doc)
        print(f"Loaded {len(fact_doc)} chunks from facts.txt")
    
    # Load all documents from current directory (including PDFs)
    try:
        dir_docs = load_documents_from_directory(current_dir)
        # Avoid duplicating facts.txt if already loaded
        if facts_file.exists():
            dir_docs = [doc for doc in dir_docs if doc.metadata.get('source') != str(facts_file)]
        all_documents.extend(dir_docs)
        print(f"Loaded {len(dir_docs)} additional chunks from directory")
    except Exception as e:
        print(f"Error loading from directory: {e}")
    
    if not all_documents:
        print("No documents found. Please ensure you have .txt or .pdf files in the current directory.")
        return
    
    print(f"Total documents to store: {len(all_documents)}")

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
