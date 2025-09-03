"""
Similarity search functionality for RAG system using ChromaDB.
Provides MCP-compatible JSON responses for document retrieval.
"""

import json
import os
import time

from enum import Enum
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
print(f"Loaded .env from {env_path}")

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ChromaDB server configuration
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8000"))
CHROMADB_URL = f"http://{CHROMADB_HOST}:{CHROMADB_PORT}"
DEFAULT_COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "langchain")

# Legacy file-based configuration (fallback)
DATA_DIR = PROJECT_ROOT / "data"

# Cache management for vectorstore connections
_vectorstore_cache = {}
_cache_ttl = 30  # 30 seconds TTL for connection caching


class ModelVendor(Enum):
    OPENAI = "openai"
    GOOGLE = "google"


def get_chromadb_client() -> chromadb.Client:
    """
    Get ChromaDB HTTP client - requires server mode.
    
    Returns:
        chromadb.HttpClient: ChromaDB HTTP client
        
    Raises:
        ConnectionError: If cannot connect to ChromaDB server
    """
    try:
        # Connect to ChromaDB server
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        # Test connection
        client.heartbeat()
        print(f"✅ Connected to ChromaDB server at {CHROMADB_URL}")
        return client
    except Exception as e:
        raise ConnectionError(
            f"❌ Cannot connect to ChromaDB server at {CHROMADB_URL}\n"
            f"Error: {e}\n\n"
            f"💡 Please ensure ChromaDB server is running:\n"
            f"   ./scripts/chromadb-server.sh start\n"
            f"   or: ./setup_chroma_db/chromadb-server.sh start"
        )


# Legacy function removed - using ChromaDB server mode instead of file-based storage
# def ensure_chroma_directory(model_vendor: ModelVendor) -> Path:
#     """Ensure the Chroma database directory exists for the specified model vendor."""
#     if model_vendor == ModelVendor.OPENAI:
#         db_path = DATA_DIR / "chroma_db_openai"
#     elif model_vendor == ModelVendor.GOOGLE:
#         db_path = DATA_DIR / "chroma_db_google"
#     else:
#         raise ValueError(f"Unsupported model vendor: {model_vendor}")
#     return db_path


def load_embedding_model(model_vendor: ModelVendor):
    """Load the embedding model based on the vendor."""
    if model_vendor == ModelVendor.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return OpenAIEmbeddings(openai_api_key=api_key)
    if model_vendor == ModelVendor.GOOGLE:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", google_api_key=api_key
        )
    raise ValueError(f"Unsupported model vendor: {model_vendor}")


def load_vectorstore(model_vendor: ModelVendor, collection_name: str = None):
    """
    Load the vectorstore using ChromaDB server.
    
    Args:
        model_vendor: Which embedding model to use
        collection_name: Collection name to use (defaults to 'langchain')
        
    Returns:
        Chroma vectorstore instance connected to ChromaDB server
        
    Raises:
        ConnectionError: If cannot connect to ChromaDB server
    """
    # Get ChromaDB client (server mode only)
    client = get_chromadb_client()
    embedding_function = load_embedding_model(model_vendor)
    
    # Use default collection name if not specified
    collection_name = collection_name or DEFAULT_COLLECTION_NAME
    
    # Create vectorstore with HTTP client
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_function,
    )


def get_cached_vectorstore(model_vendor: ModelVendor, collection_name: str = None, force_refresh: bool = False):
    """
    Get cached vectorstore connection to ChromaDB server.
    Server mode ensures data freshness, caching provides performance.
    
    Args:
        model_vendor: Which embedding model to use
        collection_name: Collection name to search
        force_refresh: Force creation of new vectorstore connection
        
    Returns:
        Chroma vectorstore instance with persistent server connection
    """
    cache_key = f"{model_vendor.value}_{collection_name or 'default'}"
    current_time = time.time()
    
    # Check if we have a cached vectorstore connection that's still valid
    if (not force_refresh and 
        cache_key in _vectorstore_cache and 
        current_time - _vectorstore_cache[cache_key]['timestamp'] < _cache_ttl):
        
        # Return cached connection - server ensures data freshness
        return _vectorstore_cache[cache_key]['vectorstore']
    
    # Create new vectorstore connection to server
    vectorstore = load_vectorstore(model_vendor, collection_name)
    _vectorstore_cache[cache_key] = {
        'vectorstore': vectorstore,
        'timestamp': current_time
    }
    
    return vectorstore


def documents_to_mcp_format(
    documents: list[Document], include_scores: bool = False
) -> list[dict[str, Any]]:
    """
    Convert LangChain Documents to MCP-compatible JSON format.

    Args:
        documents: List of LangChain Document objects
        include_scores: Whether to include relevance scores

    Returns:
        List of dictionaries in MCP-compatible format
    """
    results = []

    for doc in documents:
        result = {
            "content": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "document_id": doc.metadata.get("document_id"),
                **{
                    k: v
                    for k, v in doc.metadata.items()
                    if k not in ["relevance_score"]
                },
            },
        }

        if include_scores and "relevance_score" in doc.metadata:
            result["relevance_score"] = doc.metadata["relevance_score"]

        results.append(result)

    return results


def search_similarity(query: str, vectorstore: Chroma, k: int = 6) -> list[Document]:
    """Search the vectorstore for the most similar documents to the query."""
    try:
        results = vectorstore.similarity_search(query, k=k)
        return results
    except Exception as e:
        print(f"Error in similarity search: {e}")
        return []


def search_similarity_with_json_result(
    query: str, vectorstore: Chroma, number_result: int = 6
) -> dict[str, Any]:
    """
    Search with similarity scores and return MCP-compatible JSON format.
    Fixed the original implementation to properly return JSON results.
    """
    try:
        # Get results with scores
        results_with_scores = vectorstore.similarity_search_with_relevance_scores(
            query, k=number_result
        )

        # Process results
        documents = []
        for doc, score in results_with_scores:
            doc.metadata["relevance_score"] = score
            documents.append(doc)

        # Return MCP-compatible format
        return {
            "query": query,
            "results": documents_to_mcp_format(documents, include_scores=True),
            "total_results": len(documents),
            "status": "success",
        }

    except Exception as e:
        return {
            "query": query,
            "results": [],
            "total_results": 0,
            "error": str(e),
            "status": "error",
        }


def similarity_search_mcp_tool(
    query: str,
    model_vendor: ModelVendor = ModelVendor.GOOGLE,
    limit: int = 6,
    collection: str = None,
) -> str:
    """
    MCP tool wrapper for similarity search with ChromaDB server.
    Uses cached persistent connection to ChromaDB server for optimal performance.
    Server mode ensures fresh data without connection overhead.
    
    Args:
        query: Search query
        model_vendor: Which embedding model to use
        limit: Maximum number of results
        collection: Collection name to search

    Returns:
        JSON string containing search results
    """
    try:
        # Use cached vectorstore connection to ChromaDB server
        # Server mode ensures fresh data, caching provides performance
        vectorstore = get_cached_vectorstore(model_vendor, collection)
        
        # Perform search - server guarantees fresh data
        result = search_similarity_with_json_result(query, vectorstore, limit)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "query": query,
            "results": [],
            "total_results": 0,
            "error": str(e),
            "status": "error",
        }
        return json.dumps(error_result, indent=2)


def main():
    """Test the similarity search functionality."""
    print("Testing similarity search...")

    try:
        # Test with Google embeddings
        print("\\n1. Testing basic similarity search...")
        vectorstore = load_vectorstore(ModelVendor.GOOGLE)
        results = search_similarity("What is class in python?", vectorstore)

        # for result in results:
        #     print(result.page_content)
        #     print(result.metadata)
        #     print("--------------------------------")

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:2]):  # Show first 2 results
            print(f"Result {i + 1}: {result.page_content[:100]}...")
            print(f"Source: {result.metadata}")
            print("--------------------------------")

        print("\\n2. Testing MCP-compatible JSON format...")
        json_results = search_similarity_with_json_result(
            "What is interesting fact about the English language?",
            vectorstore,
            number_result=3,
        )
        print("JSON results:")
        print(json.dumps(json_results, indent=2))

        print("\\n3. Testing MCP tool wrapper...")
        mcp_result = similarity_search_mcp_tool(
            "What is machine learning?", ModelVendor.GOOGLE, limit=2
        )
        print("MCP Tool Result:")
        print(mcp_result)

        print("\\n4. Testing OCR")
        mcp_result = similarity_search_mcp_tool(
            "Voluntarty compliance", ModelVendor.GOOGLE, limit=2
        )
        print("MCP Tool Result:")
        print(mcp_result)

    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure you have:")
        print("1. GOOGLE_API_KEY set in your .env file")
        print("2. Documents stored in the ChromaDB database")


if __name__ == "__main__":
    main()
