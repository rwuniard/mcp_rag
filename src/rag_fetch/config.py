"""
Configuration management for MCP RAG Server.

Handles transport selection, server settings, and connection management.
Optimized for Streamable HTTP transport.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class TransportType(Enum):
    """Supported MCP transport types."""
    HTTP = "http"  # Streamable HTTP (default, recommended)
    STDIO = "stdio"  # For debugging and single-client use
    SSE = "sse"    # Legacy SSE support


class ServerConfig:
    """MCP Server configuration with environment variable support."""
    
    def __init__(self):
        # Transport configuration - HTTP is default for production
        self.transport = TransportType(
            os.getenv("MCP_TRANSPORT", "http").lower()
        )
        
        # Server network settings
        self.host = os.getenv("MCP_HOST", "127.0.0.1")
        self.port = int(os.getenv("MCP_PORT", "8000"))
        
        # HTTP transport settings
        self.http_path = os.getenv("MCP_HTTP_PATH", "/mcp")
        
        # Connection management
        self.max_connections = int(os.getenv("MCP_MAX_CONNECTIONS", "100"))
        self.connection_timeout = int(os.getenv("MCP_CONNECTION_TIMEOUT", "300"))  # 5 minutes
        
        # HTTP-specific settings
        self.enable_cors = os.getenv("MCP_ENABLE_CORS", "true").lower() == "true"
        self.cors_origins = os.getenv("MCP_CORS_ORIGINS", "*").split(",")
        
        # Logging and monitoring
        self.log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
        self.enable_request_logging = os.getenv("MCP_ENABLE_REQUEST_LOGGING", "false").lower() == "true"
        
        # ChromaDB connection (inherited from search_similarity.py)
        self.chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
        self.chromadb_port = int(os.getenv("CHROMADB_PORT", "8000"))
        
        # Server identification
        self.server_name = os.getenv("MCP_SERVER_NAME", "RAG World Fact Knowledge Base")
        
        # Performance settings
        self.enable_gzip = os.getenv("MCP_ENABLE_GZIP", "true").lower() == "true"
        self.max_request_size = int(os.getenv("MCP_MAX_REQUEST_SIZE", "10485760"))  # 10MB
        
    @property
    def is_network_transport(self) -> bool:
        """Check if the transport requires network configuration."""
        return self.transport in [TransportType.HTTP, TransportType.SSE]
    
    @property
    def server_url(self) -> str:
        """Get the complete server URL for network transports."""
        if not self.is_network_transport:
            return ""
        return f"http://{self.host}:{self.port}"
    
    @property
    def mcp_endpoint(self) -> str:
        """Get the complete MCP endpoint URL."""
        if not self.is_network_transport:
            return ""
        return f"{self.server_url}{self.http_path}"
    
    def get_transport_config(self) -> dict:
        """Get transport-specific configuration for FastMCP."""
        base_config = {}
        
        if self.is_network_transport:
            base_config.update({
                "host": self.host,
                "port": self.port,
                "log_level": self.log_level.lower()
            })
            
        if self.transport == TransportType.HTTP:
            base_config["path"] = self.http_path
            
        return base_config
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration for HTTP transport."""
        if not self.enable_cors:
            return {}
            
        return {
            "allow_origins": self.cors_origins,
            "allow_methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["*"],
            "allow_credentials": True,
        }
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        config_lines = [
            f"MCP Server Configuration:",
            f"  Transport: {self.transport.value}",
            f"  Server Name: {self.server_name}",
        ]
        
        if self.is_network_transport:
            config_lines.extend([
                f"  Host: {self.host}",
                f"  Port: {self.port}",
                f"  Endpoint: {self.mcp_endpoint}",
                f"  Log Level: {self.log_level}",
                f"  Max Connections: {self.max_connections}",
                f"  Connection Timeout: {self.connection_timeout}s",
                f"  CORS Enabled: {self.enable_cors}",
            ])
            
        config_lines.extend([
            f"  ChromaDB: {self.chromadb_host}:{self.chromadb_port}",
            f"  Request Logging: {self.enable_request_logging}",
        ])
        
        return "\n".join(config_lines)


# Global configuration instance
config = ServerConfig()