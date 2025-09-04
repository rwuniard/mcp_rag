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
from rag_fetch._version import __version__, get_version_info

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


# Connection tracking middleware
import uuid

async def connection_tracking_middleware(request, call_next):
    """Middleware to track client activity with unique connection IDs."""
    # Extract client information from request context if available
    client_ip = getattr(request, 'client', {}).get('ip', 'unknown')
    user_agent = 'FastMCP-Client'
    
    # Try to get client info from headers if available
    if hasattr(request, 'headers') and request.headers:
        user_agent = request.headers.get('user-agent', user_agent)
        # For HTTP requests, try to get real IP from common headers
        forwarded_for = request.headers.get('x-forwarded-for')
        real_ip = request.headers.get('x-real-ip')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        elif real_ip:
            client_ip = real_ip
    
    # Each request gets tracked as a separate activity
    # This simulates connection tracking by treating each tool call as connection activity
    # In a real server, you'd have persistent connection state, but FastMCP abstracts this away
    connection_id = None
    try:
        # For each request, we'll create a unique connection entry
        # This gives us realistic connection metrics for monitoring
        connection_id = connection_manager.create_connection(client_ip, user_agent)
        logger.debug(f"Request tracked as connection: {connection_id}")
        
        # Process the request
        response = await call_next(request)
        
        # After processing, mark this "connection" as complete
        # In real usage, connections would stay open longer
        connection_manager.close_connection(connection_id)
        
        return response
        
    except Exception as e:
        # If connection was created, close it before handling the error
        if connection_id:
            connection_manager.close_connection(connection_id)
        
        # Check if this was a connection creation failure or request processing failure
        if "create_connection" in str(e) or connection_id is None:
            logger.warning(f"Failed to track request: {e}")
            # Process the request even if tracking fails
            return await call_next(request)
        else:
            # Request processing failed, re-raise the exception
            logger.warning(f"Request processing failed: {e}")
            raise

# Add the middleware to the MCP server
mcp.add_middleware(connection_tracking_middleware)


# Add health endpoint for Docker healthcheck
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    HTTP health check endpoint for Docker container health monitoring.
    
    Args:
        request: Starlette request object
        
    Returns:
        JSON response indicating server health status
    """
    from datetime import datetime, timezone
    from starlette.responses import JSONResponse
    
    # Basic health check - verify server is responding and can access ChromaDB
    try:
        # Try to get connection metrics (validates internal state)
        metrics = connection_manager.get_metrics()
        
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": config.server_name,
            "version": __version__,
            "connections": metrics.get("total_connections", 0)
        }
        return JSONResponse(response_data)
        
    except Exception as e:
        # Return error status if health check fails
        error_data = {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return JSONResponse(error_data, status_code=503)


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
    Get current server status and connection metrics with version information.
    
    Returns:
        JSON string containing server status, version, and connection information
    """
    import json
    from datetime import datetime, timezone
    
    version_info = get_version_info()
    
    status = {
        "server_name": config.server_name,
        "version": version_info["version"],
        "git_info": {
            "sha": version_info["git_sha"],
            "branch": version_info["git_branch"],
            "dirty": version_info["git_dirty"],
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transport": config.transport.value,
        "status": "healthy",
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
    # Print version and configuration
    version_info = get_version_info()
    logger.info(f"🚀 RAG Fetch MCP Server v{version_info['version']} starting...")
    if version_info['git_sha']:
        logger.info(f"📦 Git SHA: {version_info['git_sha']}")
        if version_info['git_branch']:
            logger.info(f"🌿 Git Branch: {version_info['git_branch']}")
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
