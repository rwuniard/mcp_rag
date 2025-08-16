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

load_dotenv()

# Configuration - use same structure as search_similarity.py
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class ModelVendor (Enum):
    OPENAI = "openai"
    GOOGLE = "google"

def load_documents(file_path):
    loader = TextLoader(file_path)
    return loader.load_and_split(
        text_splitter=get_text_splitter()
    )

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
    return CharacterTextSplitter(
        separator="\n",
        chunk_size=200, 
        chunk_overlap=0
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
    """Store facts.txt documents to ChromaDB using Google embeddings."""
    print("Store embeddings to Chroma!")
    
    # Load documents from facts.txt
    fact_doc = load_documents("facts.txt")
    print(f"Loaded {len(fact_doc)} document chunks")

    # Store documents using Google embeddings
    vectorstore = store_to_chroma(fact_doc, ModelVendor.GOOGLE)
    print(f"Successfully stored documents. Database location: {DATA_DIR / 'chroma_db_google'}")
    
    # Test the storage by doing a quick search
    test_results = vectorstore.similarity_search("interesting fact", k=6)
    print(f"Test search returned {len(test_results)} results")
    for result in test_results: 
        print(result.page_content)
        print(result.metadata)
        print("--------------------------------")



if __name__ == "__main__":
    main()
