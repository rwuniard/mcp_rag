"""
MCP RAG Server - Model Context Protocol server for RAG functionality.

This server provides semantic document search using ChromaDB and Google embeddings.
Supports both STDIO and Streamable HTTP transports for multiple client connections.
"""

import logging
import signal
import sys
from typing import Dict, Set

from fastmcp import FastMCP

from rag_fetch.config import config
from rag_fetch.connection_manager import connection_manager
from rag_fetch.search_similarity import ModelVendor, similarity_search_mcp_tool

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with configuration
mcp = FastMCP(config.server_name)

# Configure connection manager with settings from config
connection_manager.max_connections = config.max_connections
connection_manager.connection_timeout = config.connection_timeout


@mcp.tool
def search_documents(query: str, limit: int = 6) -> str:
    """
    Search for relevant world facts and interesting facts in the world.

    Args:
        query: The search query string
        limit: Maximum number of results to return (default: 6)

    Returns:
        JSON string containing search results with
          content, metadata, and relevance scores
    """
    return similarity_search_mcp_tool(query, ModelVendor.GOOGLE, limit=limit)


@mcp.tool
def server_status() -> str:
    """
    Get current server status and connection metrics.
    
    Returns:
        JSON string containing server status and connection information
    """
    import json
    
    status = {
        "server_name": config.server_name,
        "transport": config.transport.value,
        "status": "running",
        "config": {
            "host": config.host if config.is_network_transport else None,
            "port": config.port if config.is_network_transport else None,
            "endpoint": config.mcp_endpoint if config.is_network_transport else None,
            "max_connections": config.max_connections,
            "connection_timeout": config.connection_timeout,
            "chromadb": f"{config.chromadb_host}:{config.chromadb_port}",
        },
        "metrics": connection_manager.get_metrics(),
        "active_connections": connection_manager.get_active_connections(),
    }
    
    return json.dumps(status, indent=2)


@mcp.tool  
def list_active_connections() -> str:
    """
    List all currently active connections with details.
    
    Returns:
        JSON string containing detailed information about active connections
    """
    import json
    
    connections = connection_manager.get_active_connections()
    result = {
        "active_connection_count": len(connections),
        "connections": connections,
        "metrics": connection_manager.get_metrics(),
    }
    
    return json.dumps(result, indent=2)


def setup_signal_handlers():
    """Setup graceful shutdown handlers."""
    def signal_handler(signum, _):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        
        # Shutdown connection manager
        connection_manager.shutdown()
        
        logger.info("Graceful shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Entry point for the MCP server."""
    # Print configuration
    logger.info(f"\n{config}")
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    try:
        if config.transport.value == "http":
            protocol = "HTTPS" if config.use_ssl else "HTTP"
            logger.info(f"Starting MCP server with Streamable {protocol} transport...")
            logger.info(f"Server will be available at: {config.mcp_endpoint}")
            
            # Validate SSL configuration if enabled
            if config.use_ssl:
                is_valid, error_message = config.validate_ssl_config()
                if not is_valid:
                    logger.error(f"SSL configuration error: {error_message}")
                    sys.exit(1)
                else:
                    logger.info("SSL configuration validated successfully")
                    logger.info(f"SSL Certificate: {config.ssl_cert_path}")
                    logger.info(f"SSL Environment: {config.environment}")
            
            # Add CORS middleware if enabled
            if config.enable_cors:
                cors_config = config.get_cors_config()
                logger.info(f"CORS enabled for origins: {cors_config['allow_origins']}")
            
            # Run with transport configuration
            transport_config = config.get_transport_config()
            
            # Display correct HTTPS endpoint (FastMCP banner shows incorrect http://)
            if config.use_ssl:
                logger.info("=" * 60)
                logger.info(f"✅ HTTPS Server Running: {config.mcp_endpoint}")
                logger.info(f"   (FastMCP banner may show http:// - ignore that)")
                logger.info("=" * 60)
            
            mcp.run(transport="http", **transport_config)
            
        elif config.transport.value == "stdio":
            logger.info("Starting MCP server with STDIO transport (debug mode)...")
            mcp.run()
            
        else:
            logger.error(f"Unsupported transport: {config.transport.value}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()
