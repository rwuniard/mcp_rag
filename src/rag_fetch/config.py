"""
Configuration management for MCP RAG Server.

Handles transport selection, server settings, and connection management.
Optimized for Streamable HTTP transport.
"""

import os
import ssl
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple
import logging

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
        
        # SSL/HTTPS configuration
        self.use_ssl = os.getenv("MCP_USE_SSL", "false").lower() == "true"
        self.ssl_cert_path = os.getenv("MCP_SSL_CERT_PATH")
        self.ssl_key_path = os.getenv("MCP_SSL_KEY_PATH")
        self.ssl_ca_certs = os.getenv("MCP_SSL_CA_CERTS")  # Optional CA certificates
        self.environment = os.getenv("MCP_ENVIRONMENT", "production").lower()
        self.ssl_verify_mode = os.getenv("MCP_SSL_VERIFY_MODE", "strict").lower()
        
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
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"
    
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
            
            # Add SSL configuration via uvicorn_config if enabled
            if self.use_ssl:
                ssl_config = self.get_ssl_config()
                base_config["uvicorn_config"] = ssl_config
            
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
    
    def validate_ssl_config(self) -> Tuple[bool, str]:
        """
        Validate SSL configuration and certificate files.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not self.use_ssl:
            return True, "SSL is disabled"
            
        logger = logging.getLogger(__name__)
        
        # Check if certificate and key files are provided
        if not self.ssl_cert_path or not self.ssl_key_path:
            return False, "SSL enabled but certificate or key path not provided"
        
        # Check if certificate file exists and is readable
        cert_path = Path(self.ssl_cert_path)
        if not cert_path.exists():
            return False, f"SSL certificate file not found: {self.ssl_cert_path}"
        if not cert_path.is_file():
            return False, f"SSL certificate path is not a file: {self.ssl_cert_path}"
        if not os.access(cert_path, os.R_OK):
            return False, f"SSL certificate file is not readable: {self.ssl_cert_path}"
            
        # Check if key file exists and is readable
        key_path = Path(self.ssl_key_path)
        if not key_path.exists():
            return False, f"SSL key file not found: {self.ssl_key_path}"
        if not key_path.is_file():
            return False, f"SSL key path is not a file: {self.ssl_key_path}"
        if not os.access(key_path, os.R_OK):
            return False, f"SSL key file is not readable: {self.ssl_key_path}"
            
        # Check CA certificates if provided
        if self.ssl_ca_certs:
            ca_path = Path(self.ssl_ca_certs)
            if not ca_path.exists():
                return False, f"SSL CA certificates file not found: {self.ssl_ca_certs}"
            if not ca_path.is_file():
                return False, f"SSL CA certificates path is not a file: {self.ssl_ca_certs}"
            if not os.access(ca_path, os.R_OK):
                return False, f"SSL CA certificates file is not readable: {self.ssl_ca_certs}"
        
        # Try to load the certificate to validate format
        try:
            import cryptography.x509
            from cryptography.hazmat.primitives import serialization
            
            # Load and validate certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            try:
                cert = cryptography.x509.load_pem_x509_certificate(cert_data)
            except ValueError as e:
                return False, f"Invalid SSL certificate format: {e}"
                
            # Load and validate private key
            with open(key_path, 'rb') as f:
                key_data = f.read()
                
            try:
                private_key = serialization.load_pem_private_key(key_data, password=None)
            except ValueError as e:
                return False, f"Invalid SSL private key format: {e}"
                
            # Check if certificate and key match
            public_key = cert.public_key()
            if public_key.public_numbers() != private_key.public_key().public_numbers():
                return False, "SSL certificate and private key do not match"
                
            # Check certificate expiration
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            
            # Use UTC-aware certificate dates for comparison
            try:
                # Try to use new UTC-aware properties if available (cryptography >= 42)
                not_valid_after = getattr(cert, 'not_valid_after_utc', None)
                not_valid_before = getattr(cert, 'not_valid_before_utc', None)
                
                if not_valid_after is None:
                    # Fallback to naive datetime and assume UTC
                    not_valid_after = cert.not_valid_after.replace(tzinfo=timezone.utc)
                if not_valid_before is None:
                    not_valid_before = cert.not_valid_before.replace(tzinfo=timezone.utc)
            except AttributeError:
                # For very old versions, use naive datetimes
                not_valid_after = cert.not_valid_after.replace(tzinfo=timezone.utc) if cert.not_valid_after.tzinfo is None else cert.not_valid_after
                not_valid_before = cert.not_valid_before.replace(tzinfo=timezone.utc) if cert.not_valid_before.tzinfo is None else cert.not_valid_before
            
            if not_valid_after < now:
                return False, f"SSL certificate has expired on {not_valid_after}"
            if not_valid_before > now:
                return False, f"SSL certificate is not yet valid (valid from {not_valid_before})"
                
            # Warn about certificates expiring soon (30 days)
            if not_valid_after < now + timedelta(days=30):
                logger.warning(f"SSL certificate expires soon: {not_valid_after}")
                
            # Check for self-signed certificate in production
            if self.environment == "production":
                if cert.issuer == cert.subject:
                    logger.warning("Self-signed SSL certificate detected in production environment")
                    
        except ImportError:
            # cryptography library not available, skip advanced validation
            logger.warning("Cryptography library not available, skipping advanced SSL certificate validation")
            
        return True, "SSL configuration is valid"
    
    def get_ssl_config(self) -> dict:
        """Get SSL configuration for FastMCP transport."""
        if not self.use_ssl:
            return {}
            
        # FastMCP/Uvicorn uses these parameter names for SSL
        ssl_config = {
            "ssl_certfile": self.ssl_cert_path,
            "ssl_keyfile": self.ssl_key_path,
        }
        
        # Add CA certificates if provided
        if self.ssl_ca_certs:
            ssl_config["ssl_ca_certs"] = self.ssl_ca_certs
            
        # Set certificate requirements based on verification mode
        if self.ssl_verify_mode == "strict":
            ssl_config["ssl_cert_reqs"] = ssl.CERT_REQUIRED
        elif self.ssl_verify_mode == "relaxed":
            ssl_config["ssl_cert_reqs"] = ssl.CERT_OPTIONAL
        else:
            ssl_config["ssl_cert_reqs"] = ssl.CERT_NONE
            
        return ssl_config
    
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
                f"  SSL Enabled: {self.use_ssl}",
                f"  Log Level: {self.log_level}",
                f"  Max Connections: {self.max_connections}",
                f"  Connection Timeout: {self.connection_timeout}s",
                f"  CORS Enabled: {self.enable_cors}",
            ])
            
            if self.use_ssl:
                config_lines.extend([
                    f"  SSL Certificate: {self.ssl_cert_path}",
                    f"  SSL Key: {self.ssl_key_path}",
                    f"  SSL CA Certs: {self.ssl_ca_certs or 'None'}",
                    f"  SSL Verify Mode: {self.ssl_verify_mode}",
                    f"  Environment: {self.environment}",
                ])
            
        config_lines.extend([
            f"  ChromaDB: {self.chromadb_host}:{self.chromadb_port}",
            f"  Request Logging: {self.enable_request_logging}",
        ])
        
        return "\n".join(config_lines)


# Global configuration instance
config = ServerConfig()