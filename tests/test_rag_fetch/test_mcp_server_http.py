"""
Unit tests for MCP Server HTTP transport functionality.

Tests Streamable HTTP transport, connection management, and multi-client support.
"""

import asyncio
import json
import os
import unittest
from unittest.mock import patch, MagicMock

import pytest

from rag_fetch.config import ServerConfig, TransportType
from rag_fetch.connection_manager import ConnectionManager, ConnectionInfo
from rag_fetch.mcp_server import mcp


class TestServerConfig(unittest.TestCase):
    """Test server configuration management."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment variables including SSL ones
        env_vars = [
            "MCP_TRANSPORT", "MCP_HOST", "MCP_PORT", "MCP_HTTP_PATH",
            "MCP_MAX_CONNECTIONS", "MCP_CONNECTION_TIMEOUT", "MCP_LOG_LEVEL",
            "MCP_ENABLE_CORS", "MCP_CORS_ORIGINS", "MCP_USE_SSL",
            "MCP_SSL_CERT_PATH", "MCP_SSL_KEY_PATH", "MCP_SSL_CA_CERTS"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        self.assertEqual(config.transport, TransportType.HTTP)  # HTTP is now default
        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.http_path, "/mcp")
        self.assertEqual(config.max_connections, 100)
        self.assertEqual(config.connection_timeout, 300)
        self.assertTrue(config.enable_cors)
    
    @patch.dict(os.environ, {}, clear=True)  # Clear all env vars
    def test_http_transport_config(self):
        """Test HTTP transport configuration."""
        os.environ["MCP_TRANSPORT"] = "http"
        os.environ["MCP_HOST"] = "0.0.0.0"
        os.environ["MCP_PORT"] = "9000"
        os.environ["MCP_USE_SSL"] = "false"  # Explicitly disable SSL
        
        config = ServerConfig()
        
        self.assertEqual(config.transport, TransportType.HTTP)
        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.port, 9000)
        self.assertTrue(config.is_network_transport)
        self.assertEqual(config.server_url, "http://0.0.0.0:9000")
        self.assertEqual(config.mcp_endpoint, "http://0.0.0.0:9000/mcp")
    
    @patch.dict(os.environ, {}, clear=True)  # Clear all env vars
    def test_transport_config_generation(self):
        """Test transport configuration generation for FastMCP."""
        os.environ["MCP_TRANSPORT"] = "http"
        os.environ["MCP_HOST"] = "localhost"
        os.environ["MCP_PORT"] = "8080"
        os.environ["MCP_HTTP_PATH"] = "/api/mcp"
        os.environ["MCP_USE_SSL"] = "false"  # Explicitly disable SSL
        
        config = ServerConfig()
        transport_config = config.get_transport_config()
        
        expected = {
            "host": "localhost",
            "port": 8080,
            "log_level": "info",
            "path": "/api/mcp"
        }
        
        self.assertEqual(transport_config, expected)
    
    def test_cors_config(self):
        """Test CORS configuration."""
        os.environ["MCP_ENABLE_CORS"] = "true"
        os.environ["MCP_CORS_ORIGINS"] = "http://localhost:3000,https://app.example.com"
        
        config = ServerConfig()
        cors_config = config.get_cors_config()
        
        expected = {
            "allow_origins": ["http://localhost:3000", "https://app.example.com"],
            "allow_methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["*"],
            "allow_credentials": True,
        }
        
        self.assertEqual(cors_config, expected)


class TestConnectionManager(unittest.TestCase):
    """Test connection management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = ConnectionManager(max_connections=3, connection_timeout=60)
    
    def tearDown(self):
        """Clean up after tests."""
        self.manager.shutdown()
    
    def test_create_connection(self):
        """Test connection creation."""
        connection_id = self.manager.create_connection("192.168.1.1", "TestClient/1.0")
        
        self.assertIsNotNone(connection_id)
        self.assertIn(connection_id, self.manager.connections)
        
        connection = self.manager.get_connection(connection_id)
        self.assertEqual(connection.client_ip, "192.168.1.1")
        self.assertEqual(connection.user_agent, "TestClient/1.0")
        self.assertEqual(connection.requests_count, 0)
    
    def test_connection_limit(self):
        """Test connection limit enforcement."""
        # Create max connections
        for i in range(3):
            self.manager.create_connection(f"192.168.1.{i}", f"Client{i}")
        
        # Should raise error on exceeding limit
        with self.assertRaises(ConnectionError) as context:
            self.manager.create_connection("192.168.1.4", "Client4")
        
        self.assertIn("Maximum connections", str(context.exception))
        self.assertEqual(self.manager.metrics["rejected_connections"], 1)
    
    def test_connection_activity_tracking(self):
        """Test connection activity tracking."""
        connection_id = self.manager.create_connection("192.168.1.1", "TestClient")
        
        # Update activity
        self.manager.update_connection_activity(connection_id)
        
        connection = self.manager.get_connection(connection_id)
        self.assertEqual(connection.requests_count, 1)
        
        # Update again
        self.manager.update_connection_activity(connection_id)
        self.assertEqual(connection.requests_count, 2)
    
    def test_connection_timeout_cleanup(self):
        """Test automatic cleanup of timed out connections."""
        # Create connection with very short timeout
        manager = ConnectionManager(connection_timeout=0.1)
        
        try:
            connection_id = manager.create_connection("192.168.1.1", "TestClient")
            self.assertIn(connection_id, manager.connections)
            
            # Wait for timeout
            import time
            time.sleep(0.2)
            
            # Trigger cleanup
            manager._cleanup_timed_out_connections()
            
            # Connection should be removed
            self.assertNotIn(connection_id, manager.connections)
            self.assertEqual(manager.metrics["timed_out_connections"], 1)
        
        finally:
            manager.shutdown()
    
    def test_get_active_connections(self):
        """Test getting active connection information."""
        connection_id = self.manager.create_connection("192.168.1.1", "TestClient/1.0")
        self.manager.update_connection_activity(connection_id)
        
        active = self.manager.get_active_connections()
        
        self.assertIn(connection_id, active)
        connection_info = active[connection_id]
        
        self.assertEqual(connection_info["client_ip"], "192.168.1.1")
        self.assertEqual(connection_info["user_agent"], "TestClient/1.0")
        self.assertEqual(connection_info["requests_count"], 1)
        self.assertIsInstance(connection_info["duration"], float)
        self.assertIsInstance(connection_info["idle_time"], float)
    
    def test_metrics_tracking(self):
        """Test connection metrics tracking."""
        initial_metrics = self.manager.get_metrics()
        
        # Create connections
        conn1 = self.manager.create_connection("192.168.1.1", "Client1")
        conn2 = self.manager.create_connection("192.168.1.2", "Client2")
        
        metrics = self.manager.get_metrics()
        self.assertEqual(metrics["total_connections"], 2)
        self.assertEqual(metrics["current_connections"], 2)
        
        # Close one connection
        self.manager.close_connection(conn1)
        
        metrics = self.manager.get_metrics()
        self.assertEqual(metrics["total_connections"], 2)
        self.assertEqual(metrics["current_connections"], 1)


class TestMCPServerTools(unittest.TestCase):
    """Test MCP server tools functionality."""
    
    @patch("rag_fetch.mcp_server.connection_manager")
    def test_server_status_tool(self, mock_manager):
        """Test server_status tool using in-memory FastMCP."""
        # Mock connection manager
        mock_manager.get_metrics.return_value = {
            "total_connections": 5,
            "current_connections": 2,
            "failed_connections": 0,
        }
        mock_manager.get_active_connections.return_value = {
            "conn-123": {
                "client_ip": "192.168.1.1",
                "user_agent": "TestClient/1.0",
                "duration": 120.5,
                "requests_count": 10,
            }
        }
        
        # Test using the FastMCP client with in-memory transport
        import asyncio
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        async def test_server_status():
            async with Client(mcp) as client:
                result = await client.call_tool("server_status", {})
                # FastMCP returns CallToolResult with data attribute
                status_data = json.loads(result.data)
                
                self.assertEqual(status_data["server_name"], "RAG World Fact Knowledge Base")
                self.assertIn("metrics", status_data)
                self.assertIn("active_connections", status_data)
                self.assertEqual(status_data["metrics"]["total_connections"], 5)
        
        # Run the async test
        asyncio.run(test_server_status())
    
    @patch("rag_fetch.mcp_server.connection_manager")
    def test_list_active_connections_tool(self, mock_manager):
        """Test list_active_connections tool using in-memory FastMCP."""
        mock_connections = {
            "conn-123": {
                "client_ip": "192.168.1.1",
                "user_agent": "TestClient/1.0",
                "duration": 120.5,
                "requests_count": 10,
            },
            "conn-456": {
                "client_ip": "192.168.1.2", 
                "user_agent": "TestClient/2.0",
                "duration": 60.2,
                "requests_count": 5,
            }
        }
        
        mock_manager.get_active_connections.return_value = mock_connections
        mock_manager.get_metrics.return_value = {
            "total_connections": 10,
            "current_connections": 2,
        }
        
        # Test using the FastMCP client with in-memory transport
        import asyncio
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        async def test_list_connections():
            async with Client(mcp) as client:
                result = await client.call_tool("list_active_connections", {})
                # FastMCP returns CallToolResult with data attribute
                data = json.loads(result.data)
                
                self.assertEqual(data["active_connection_count"], 2)
                self.assertEqual(len(data["connections"]), 2)
                self.assertIn("conn-123", data["connections"])
                self.assertIn("conn-456", data["connections"])
        
        # Run the async test
        asyncio.run(test_list_connections())


if __name__ == "__main__":
    unittest.main()