"""
Similarity search functionality for RAG system using ChromaDB.
Provides MCP-compatible JSON responses for document retrieval.
"""

import json
import os

from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

load_dotenv(Path(__file__).parent / ".env")
print(f"Loaded .env from {Path(__file__).parent / '.env'}")

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_COLLECTION_NAME = "documents"

# Configuration - use same structure as search_similarity.py
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class ModelVendor(Enum):
    OPENAI = "openai"
    GOOGLE = "google"


def ensure_chroma_directory(model_vendor: ModelVendor) -> Path:
    """Ensure the Chroma database directory exists for the specified model vendor."""
    if model_vendor == ModelVendor.OPENAI:
        db_path = DATA_DIR / "chroma_db_openai"
    elif model_vendor == ModelVendor.GOOGLE:
        db_path = DATA_DIR / "chroma_db_google"
    else:
        raise ValueError(f"Unsupported model vendor: {model_vendor}")

    # db_path.mkdir(parents=True, exist_ok=True)
    return db_path


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
    """Load the vectorstore from the persist directory based on the model vendor."""
    db_path = ensure_chroma_directory(model_vendor)
    print("DB path: ", db_path)
    db_path_object = Path(db_path)
    if not db_path_object.exists():
        raise FileNotFoundError(f"Database directory not found: {db_path}")
    embedding_function = load_embedding_model(model_vendor)

    # Use default collection if none specified (same as storage)
    if collection_name:
        return Chroma(
            embedding_function=embedding_function,
            persist_directory=str(db_path),
            collection_name=collection_name,
        )
    return Chroma(embedding_function=embedding_function, persist_directory=str(db_path))


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
    MCP tool wrapper for similarity search.
    Returns JSON string for MCP compatibility.

    Args:
        query: Search query
        model_vendor: Which embedding model to use
        limit: Maximum number of results
        collection: Collection name to search

    Returns:
        JSON string containing search results
    """
    try:
        vectorstore = load_vectorstore(model_vendor, collection)
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

    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure you have:")
        print("1. GOOGLE_API_KEY set in your .env file")
        print("2. Documents stored in the ChromaDB database")


if __name__ == "__main__":
    main()
