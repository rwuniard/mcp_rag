"""
RAG Fetch - Document Search Service

Independent service for semantic search and retrieval from vector database.
Includes MCP server for AI assistant integration.
Can be deployed separately from the ingestion service.
"""

from .search_similarity import similarity_search_mcp_tool, ModelVendor

__version__ = "0.1.0"
__all__ = ["similarity_search_mcp_tool", "ModelVendor"]