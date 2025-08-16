"""
MCP RAG Server - Model Context Protocol server for RAG functionality.

This server provides semantic document search using ChromaDB and Google embeddings.
"""

from fastmcp import FastMCP
from rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor

# Initialize FastMCP server
mcp = FastMCP("RAG Knowledge Base")

@mcp.tool
def search_documents(query: str, limit: int = 6) -> str:
    """
    Search for relevant world facts and interesting facts in the world.
    
    Args:
        query: The search query string
        limit: Maximum number of results to return (default: 6)
        
    Returns:
        JSON string containing search results with content, metadata, and relevance scores
    """
    return similarity_search_mcp_tool(query, ModelVendor.GOOGLE, limit=limit)

if __name__ == "__main__":
    mcp.run()