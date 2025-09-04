"""
RAG Fetch - Document Search Service

Independent service for semantic search and retrieval from vector database.
Includes MCP server for AI assistant integration.
Can be deployed separately from the ingestion service.
"""

from .search_similarity import ModelVendor, similarity_search_mcp_tool
from ._version import __version__

__all__ = ["ModelVendor", "similarity_search_mcp_tool", "__version__"]
