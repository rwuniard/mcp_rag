"""
Comprehensive tests for MCP server functions in mcp_server.py.

This test file focuses on directly testing the functions and logic in mcp_server.py
to improve code coverage beyond the integration tests.
"""

import asyncio
import json
import signal
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, call, AsyncMock
from unittest import TestCase

# Import the module under test
from rag_fetch import mcp_server
from rag_fetch.search_similarity import ModelVendor


class TestMCPServerTools(TestCase):
    """Test the MCP tool functions directly."""

    @patch('rag_fetch.mcp_server.similarity_search_mcp_tool')
    def test_search_documents_default_limit(self, mock_search):
        """Test search_documents with default limit."""
        # Setup mock
        expected_result = '{"results": [{"content": "test"}]}'
        mock_search.return_value = expected_result
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.search_documents.fn("test query")
        
        # Verify
        mock_search.assert_called_once_with("test query", ModelVendor.GOOGLE, limit=6)
        self.assertEqual(result, expected_result)

    @patch('rag_fetch.mcp_server.similarity_search_mcp_tool')
    def test_search_documents_custom_limit(self, mock_search):
        """Test search_documents with custom limit."""
        # Setup mock
        expected_result = '{"results": [{"content": "test"}]}'
        mock_search.return_value = expected_result
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.search_documents.fn("test query", limit=10)
        
        # Verify
        mock_search.assert_called_once_with("test query", ModelVendor.GOOGLE, limit=10)
        self.assertEqual(result, expected_result)

    @patch('rag_fetch.mcp_server.connection_manager')
    @patch('rag_fetch.mcp_server.config')
    def test_server_status_http_transport(self, mock_config, mock_connection_manager):
        """Test server_status function with HTTP transport."""
        # Setup mocks
        mock_config.server_name = "Test Server"
        mock_config.transport.value = "http"
        mock_config.is_network_transport = True
        mock_config.host = "localhost"
        mock_config.port = 8000
        mock_config.mcp_endpoint = "http://localhost:8000/mcp"
        mock_config.max_connections = 100
        mock_config.connection_timeout = 300
        mock_config.chromadb_host = "localhost"
        mock_config.chromadb_port = 8001
        
        mock_metrics = {"total_connections": 5, "current_connections": 2}
        mock_connections = {"conn1": {"client_ip": "127.0.0.1"}}
        mock_connection_manager.get_metrics.return_value = mock_metrics
        mock_connection_manager.get_active_connections.return_value = mock_connections
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.server_status.fn()
        
        # Parse and verify result
        status = json.loads(result)
        self.assertEqual(status["server_name"], "Test Server")
        self.assertEqual(status["transport"], "http")
        self.assertEqual(status["status"], "running")
        self.assertEqual(status["config"]["host"], "localhost")
        self.assertEqual(status["config"]["port"], 8000)
        self.assertEqual(status["config"]["endpoint"], "http://localhost:8000/mcp")
        self.assertEqual(status["config"]["max_connections"], 100)
        self.assertEqual(status["config"]["connection_timeout"], 300)
        self.assertEqual(status["config"]["chromadb"], "localhost:8001")
        self.assertEqual(status["metrics"], mock_metrics)
        self.assertEqual(status["active_connections"], mock_connections)

    @patch('rag_fetch.mcp_server.connection_manager')
    @patch('rag_fetch.mcp_server.config')
    def test_server_status_stdio_transport(self, mock_config, mock_connection_manager):
        """Test server_status function with STDIO transport."""
        # Setup mocks
        mock_config.server_name = "Test Server"
        mock_config.transport.value = "stdio"
        mock_config.is_network_transport = False
        mock_config.max_connections = 100
        mock_config.connection_timeout = 300
        mock_config.chromadb_host = "localhost"
        mock_config.chromadb_port = 8001
        
        mock_metrics = {"total_connections": 0, "current_connections": 0}
        mock_connections = {}
        mock_connection_manager.get_metrics.return_value = mock_metrics
        mock_connection_manager.get_active_connections.return_value = mock_connections
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.server_status.fn()
        
        # Parse and verify result
        status = json.loads(result)
        self.assertEqual(status["server_name"], "Test Server")
        self.assertEqual(status["transport"], "stdio")
        self.assertEqual(status["status"], "running")
        self.assertIsNone(status["config"]["host"])
        self.assertIsNone(status["config"]["port"])
        self.assertIsNone(status["config"]["endpoint"])
        self.assertEqual(status["config"]["max_connections"], 100)
        self.assertEqual(status["config"]["connection_timeout"], 300)
        self.assertEqual(status["config"]["chromadb"], "localhost:8001")
        self.assertEqual(status["metrics"], mock_metrics)
        self.assertEqual(status["active_connections"], mock_connections)

    @patch('rag_fetch.mcp_server.connection_manager')
    def test_list_active_connections_with_connections(self, mock_connection_manager):
        """Test list_active_connections with active connections."""
        # Setup mocks
        mock_connections = {
            "conn1": {"client_ip": "127.0.0.1", "user_agent": "TestClient"},
            "conn2": {"client_ip": "192.168.1.100", "user_agent": "AnotherClient"}
        }
        mock_metrics = {"total_connections": 10, "current_connections": 2}
        mock_connection_manager.get_active_connections.return_value = mock_connections
        mock_connection_manager.get_metrics.return_value = mock_metrics
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.list_active_connections.fn()
        
        # Parse and verify result
        data = json.loads(result)
        self.assertEqual(data["active_connection_count"], 2)
        self.assertEqual(data["connections"], mock_connections)
        self.assertEqual(data["metrics"], mock_metrics)

    @patch('rag_fetch.mcp_server.connection_manager')
    def test_list_active_connections_empty(self, mock_connection_manager):
        """Test list_active_connections with no active connections."""
        # Setup mocks
        mock_connections = {}
        mock_metrics = {"total_connections": 5, "current_connections": 0}
        mock_connection_manager.get_active_connections.return_value = mock_connections
        mock_connection_manager.get_metrics.return_value = mock_metrics
        
        # Call the underlying function (not the decorated version)
        result = mcp_server.list_active_connections.fn()
        
        # Parse and verify result
        data = json.loads(result)
        self.assertEqual(data["active_connection_count"], 0)
        self.assertEqual(data["connections"], {})
        self.assertEqual(data["metrics"], mock_metrics)


class TestSignalHandlers(TestCase):
    """Test signal handling functionality."""

    @patch('rag_fetch.mcp_server.signal.signal')
    def test_setup_signal_handlers(self, mock_signal):
        """Test setup_signal_handlers function."""
        # Call function
        mcp_server.setup_signal_handlers()
        
        # Verify signal handlers were set up
        self.assertEqual(mock_signal.call_count, 2)
        mock_signal.assert_has_calls([
            call(signal.SIGINT, unittest.mock.ANY),
            call(signal.SIGTERM, unittest.mock.ANY)
        ])

    @patch('rag_fetch.mcp_server.sys.exit')
    @patch('rag_fetch.mcp_server.connection_manager')
    @patch('rag_fetch.mcp_server.logger')
    def test_signal_handler_sigint(self, mock_logger, mock_connection_manager, mock_sys_exit):
        """Test signal handler for SIGINT."""
        # Setup signal handlers
        mcp_server.setup_signal_handlers()
        
        # Get the signal handler function
        with patch('rag_fetch.mcp_server.signal.signal') as mock_signal:
            mcp_server.setup_signal_handlers()
            # Get the handler function from the first call (SIGINT)
            signal_handler = mock_signal.call_args_list[0][0][1]
        
        # Call the signal handler
        signal_handler(signal.SIGINT, None)
        
        # Verify behavior
        mock_logger.info.assert_has_calls([
            call(f"Received signal {signal.SIGINT}, shutting down gracefully..."),
            call("Graceful shutdown complete")
        ])
        mock_connection_manager.shutdown.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)

    @patch('rag_fetch.mcp_server.sys.exit')
    @patch('rag_fetch.mcp_server.connection_manager')
    @patch('rag_fetch.mcp_server.logger')
    def test_signal_handler_sigterm(self, mock_logger, mock_connection_manager, mock_sys_exit):
        """Test signal handler for SIGTERM."""
        # Setup signal handlers
        mcp_server.setup_signal_handlers()
        
        # Get the signal handler function
        with patch('rag_fetch.mcp_server.signal.signal') as mock_signal:
            mcp_server.setup_signal_handlers()
            # Get the handler function from the second call (SIGTERM)
            signal_handler = mock_signal.call_args_list[1][0][1]
        
        # Call the signal handler
        signal_handler(signal.SIGTERM, None)
        
        # Verify behavior
        mock_logger.info.assert_has_calls([
            call(f"Received signal {signal.SIGTERM}, shutting down gracefully..."),
            call("Graceful shutdown complete")
        ])
        mock_connection_manager.shutdown.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)


class TestMainFunction(TestCase):
    """Test the main function with different configurations."""

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_stdio_transport(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with STDIO transport."""
        # Setup mocks
        mock_config.transport.value = "stdio"
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Call function
        mcp_server.main()
        
        # Verify
        mock_logger.info.assert_has_calls([
            call("\nConfig Details"),
            call("Starting MCP server with STDIO transport (debug mode)..."),
            call("Server shutdown complete")
        ])
        mock_setup_signals.assert_called_once()
        mock_mcp.run.assert_called_once_with()

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_http_transport_no_ssl(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with HTTP transport without SSL."""
        # Setup mocks
        mock_config.transport.value = "http"
        mock_config.use_ssl = False
        mock_config.enable_cors = False
        mock_config.mcp_endpoint = "http://localhost:8000/mcp"
        mock_config.get_transport_config.return_value = {"host": "localhost", "port": 8000}
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Call function
        mcp_server.main()
        
        # Verify
        mock_logger.info.assert_has_calls([
            call("\nConfig Details"),
            call("Starting MCP server with Streamable HTTP transport..."),
            call("Server will be available at: http://localhost:8000/mcp"),
            call("Server shutdown complete")
        ])
        mock_setup_signals.assert_called_once()
        mock_mcp.run.assert_called_once_with(transport="http", host="localhost", port=8000)

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_https_transport_with_ssl(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with HTTPS transport with SSL."""
        # Setup mocks
        mock_config.transport.value = "http"
        mock_config.use_ssl = True
        mock_config.enable_cors = False
        mock_config.mcp_endpoint = "https://localhost:8443/mcp"
        mock_config.ssl_cert_path = "/path/to/cert.pem"
        mock_config.environment = "production"
        mock_config.validate_ssl_config.return_value = (True, None)
        mock_config.get_transport_config.return_value = {"host": "localhost", "port": 8443}
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Call function
        mcp_server.main()
        
        # Verify
        mock_logger.info.assert_has_calls([
            call("\nConfig Details"),
            call("Starting MCP server with Streamable HTTPS transport..."),
            call("Server will be available at: https://localhost:8443/mcp"),
            call("SSL configuration validated successfully"),
            call("SSL Certificate: /path/to/cert.pem"),
            call("SSL Environment: production"),
            call("=" * 60),
            call("✅ HTTPS Server Running: https://localhost:8443/mcp"),
            call("   (FastMCP banner may show http:// - ignore that)"),
            call("=" * 60),
            call("Server shutdown complete")
        ])
        mock_setup_signals.assert_called_once()
        mock_config.validate_ssl_config.assert_called_once()
        mock_mcp.run.assert_called_once_with(transport="http", host="localhost", port=8443)

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.sys.exit')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_ssl_validation_failure(self, mock_config, mock_logger, mock_setup_signals, mock_sys_exit, mock_mcp):
        """Test main function with SSL validation failure."""
        # Setup mocks
        mock_config.transport.value = "http"
        mock_config.use_ssl = True
        mock_config.mcp_endpoint = "https://localhost:8443/mcp"
        mock_config.validate_ssl_config.return_value = (False, "Certificate not found")
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Make sys.exit actually raise SystemExit to stop execution
        mock_sys_exit.side_effect = SystemExit(1)
        
        # Call function and expect SystemExit
        with self.assertRaises(SystemExit):
            mcp_server.main()
        
        # Verify
        mock_logger.error.assert_called_with("SSL configuration error: Certificate not found")
        mock_sys_exit.assert_called_once_with(1)
        # Should not try to start server when SSL validation fails
        mock_mcp.run.assert_not_called()

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_with_cors_enabled(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with CORS enabled."""
        # Setup mocks
        mock_config.transport.value = "http"
        mock_config.use_ssl = False
        mock_config.enable_cors = True
        mock_config.mcp_endpoint = "http://localhost:8000/mcp"
        mock_cors_config = {"allow_origins": ["*"], "allow_methods": ["GET", "POST"]}
        mock_config.get_cors_config.return_value = mock_cors_config
        mock_config.get_transport_config.return_value = {"host": "localhost", "port": 8000}
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Call function
        mcp_server.main()
        
        # Verify CORS logging
        mock_logger.info.assert_any_call("CORS enabled for origins: ['*']")
        mock_config.get_cors_config.assert_called_once()

    @patch('rag_fetch.mcp_server.sys.exit')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_unsupported_transport(self, mock_config, mock_logger, mock_setup_signals, mock_sys_exit):
        """Test main function with unsupported transport."""
        # Setup mocks
        mock_config.transport.value = "websocket"  # Unsupported
        mock_config.__str__ = Mock(return_value="Config Details")
        
        # Make sys.exit actually raise SystemExit to stop execution
        mock_sys_exit.side_effect = SystemExit(1)
        
        # Call function and expect SystemExit
        with self.assertRaises(SystemExit):
            mcp_server.main()
        
        # Verify
        mock_logger.error.assert_called_with("Unsupported transport: websocket")
        mock_sys_exit.assert_called_once_with(1)

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_keyboard_interrupt(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with KeyboardInterrupt."""
        # Setup mocks
        mock_config.transport.value = "stdio"
        mock_config.__str__ = Mock(return_value="Config Details")
        mock_mcp.run.side_effect = KeyboardInterrupt()
        
        # Call function
        mcp_server.main()
        
        # Verify
        mock_logger.info.assert_has_calls([
            call("\nConfig Details"),
            call("Starting MCP server with STDIO transport (debug mode)..."),
            call("Server interrupted by user"),
            call("Server shutdown complete")
        ])

    @patch('rag_fetch.mcp_server.mcp')
    @patch('rag_fetch.mcp_server.setup_signal_handlers')
    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.config')
    def test_main_general_exception(self, mock_config, mock_logger, mock_setup_signals, mock_mcp):
        """Test main function with general exception."""
        # Setup mocks
        mock_config.transport.value = "stdio"
        mock_config.__str__ = Mock(return_value="Config Details")
        test_exception = RuntimeError("Test error")
        mock_mcp.run.side_effect = test_exception
        
        # Call function and expect exception to be re-raised
        with self.assertRaises(RuntimeError):
            mcp_server.main()
        
        # Verify
        mock_logger.error.assert_called_with("Server error: Test error")
        mock_logger.info.assert_has_calls([
            call("\nConfig Details"),
            call("Starting MCP server with STDIO transport (debug mode)..."),
            call("Server shutdown complete")
        ])


class TestConnectionTrackingMiddleware(TestCase):
    """Test the connection tracking middleware functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock request and call_next objects
        self.mock_request = Mock()
        self.mock_call_next = AsyncMock()
        self.mock_response = Mock()
        self.mock_call_next.return_value = self.mock_response
    
    def run_async_test(self, async_test_func):
        """Helper to run async test functions in sync context."""
        return asyncio.run(async_test_func())

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_basic_functionality(self, mock_connection_manager):
        """Test basic middleware functionality."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-123"
        
        # Set up request attributes
        self.mock_request.client = {'ip': '192.168.1.100'}
        self.mock_request.headers = {'user-agent': 'TestClient/1.0'}
        
        # Call middleware
        result = await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify behavior
        mock_connection_manager.create_connection.assert_called_once_with(
            '192.168.1.100', 'TestClient/1.0'
        )
        mock_connection_manager.close_connection.assert_called_once_with("test-conn-123")
        self.mock_call_next.assert_called_once_with(self.mock_request)
        self.assertEqual(result, self.mock_response)

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_with_forwarded_headers(self, mock_connection_manager):
        """Test middleware with X-Forwarded-For headers."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-456"
        
        # Set up request with forwarded headers
        self.mock_request.client = {'ip': '10.0.0.1'}  # Internal IP
        self.mock_request.headers = {
            'user-agent': 'ProxyClient/2.0',
            'x-forwarded-for': '203.0.113.45, 10.0.0.1',  # Real IP first
            'x-real-ip': '203.0.113.45'
        }
        
        # Call middleware
        await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify it uses the forwarded IP
        mock_connection_manager.create_connection.assert_called_once_with(
            '203.0.113.45', 'ProxyClient/2.0'
        )

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_with_real_ip_header(self, mock_connection_manager):
        """Test middleware with X-Real-IP header."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-789"
        
        # Set up request with real IP header (no forwarded-for)
        self.mock_request.client = {'ip': '10.0.0.1'}
        self.mock_request.headers = {
            'user-agent': 'RealIPClient/1.5',
            'x-real-ip': '198.51.100.42'
        }
        
        # Call middleware
        await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify it uses the real IP
        mock_connection_manager.create_connection.assert_called_once_with(
            '198.51.100.42', 'RealIPClient/1.5'
        )

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_with_no_headers(self, mock_connection_manager):
        """Test middleware with no headers available."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-default"
        
        # Set up request with minimal attributes
        self.mock_request.client = {'ip': 'unknown'}
        self.mock_request.headers = None
        
        # Call middleware
        await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify it uses defaults
        mock_connection_manager.create_connection.assert_called_once_with(
            'unknown', 'FastMCP-Client'
        )

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_with_no_client_info(self, mock_connection_manager):
        """Test middleware when request has no client info."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-noclient"
        
        # Set up request with no client attribute
        if hasattr(self.mock_request, 'client'):
            delattr(self.mock_request, 'client')
        self.mock_request.headers = {'user-agent': 'NoClientInfo/1.0'}
        
        # Call middleware
        await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify it uses defaults
        mock_connection_manager.create_connection.assert_called_once_with(
            'unknown', 'NoClientInfo/1.0'
        )

    @patch('rag_fetch.mcp_server.logger')
    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_connection_creation_failure(self, mock_connection_manager, mock_logger):
        """Test middleware when connection creation fails."""
        # Setup mocks
        mock_connection_manager.create_connection.side_effect = Exception("Connection limit exceeded")
        
        # Set up request
        self.mock_request.client = {'ip': '192.168.1.200'}
        self.mock_request.headers = {'user-agent': 'FailClient/1.0'}
        
        # Call middleware
        result = await mcp_server.connection_tracking_middleware(
            self.mock_request, self.mock_call_next
        )
        
        # Verify it continues processing despite failure
        mock_logger.warning.assert_called_once_with("Failed to track request: Connection limit exceeded")
        self.mock_call_next.assert_called_once_with(self.mock_request)
        self.assertEqual(result, self.mock_response)

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_middleware_request_processing_exception(self, mock_connection_manager):
        """Test middleware when request processing raises exception."""
        # Setup mocks
        mock_connection_manager.create_connection.return_value = "test-conn-exception"
        self.mock_call_next.side_effect = Exception("Request processing failed")
        
        # Set up request
        self.mock_request.client = {'ip': '192.168.1.300'}
        self.mock_request.headers = {'user-agent': 'ExceptionClient/1.0'}
        
        # Call middleware and expect exception to propagate
        with self.assertRaises(Exception) as context:
            await mcp_server.connection_tracking_middleware(
                self.mock_request, self.mock_call_next
            )
        
        self.assertEqual(str(context.exception), "Request processing failed")
        
        # Verify connection was still closed
        mock_connection_manager.close_connection.assert_called_once_with("test-conn-exception")

    def test_middleware_sync_wrapper(self):
        """Test running middleware in sync context for coverage."""
        # This test ensures the async middleware can be tested
        async def run_test():
            with patch('rag_fetch.mcp_server.connection_manager') as mock_cm:
                mock_cm.create_connection.return_value = "sync-test-conn"
                
                # Set up request
                mock_request = Mock()
                mock_request.client = {'ip': '127.0.0.1'}
                mock_request.headers = {'user-agent': 'SyncTest/1.0'}
                
                mock_call_next = AsyncMock()
                mock_response = Mock()
                mock_call_next.return_value = mock_response
                
                # Call middleware
                result = await mcp_server.connection_tracking_middleware(
                    mock_request, mock_call_next
                )
                
                # Verify
                self.assertEqual(result, mock_response)
                mock_cm.create_connection.assert_called_once()
                mock_cm.close_connection.assert_called_once()
        
        # Run the async test
        asyncio.run(run_test())


class TestModuleLevelConfiguration(TestCase):
    """Test module-level configuration and initialization."""

    @patch('rag_fetch.mcp_server.connection_manager')
    @patch('rag_fetch.mcp_server.config')
    def test_module_initialization(self, mock_config, mock_connection_manager):
        """Test that module-level configuration is applied correctly."""
        # This test verifies that the module initialization code runs
        # The actual initialization happens when the module is imported
        # So we verify the current state
        
        # Import the module to trigger initialization
        import importlib
        importlib.reload(mcp_server)
        
        # Verify that connection manager settings were configured
        # Note: These assertions check the actual values set during import
        self.assertIsNotNone(mcp_server.connection_manager.max_connections)
        self.assertIsNotNone(mcp_server.connection_manager.connection_timeout)

    def test_middleware_is_added_to_mcp(self):
        """Test that middleware is properly added to MCP server."""
        # Verify the middleware function exists
        self.assertTrue(hasattr(mcp_server, 'connection_tracking_middleware'))
        self.assertTrue(callable(mcp_server.connection_tracking_middleware))
        
        # Verify the middleware is added to the MCP server
        # Note: We can't easily test the internal middleware list without accessing private attributes
        # But we can verify the function exists and is callable
        import inspect
        self.assertTrue(inspect.iscoroutinefunction(mcp_server.connection_tracking_middleware))


class TestMCPServerIntegrationWithMiddleware(TestCase):
    """Integration tests for MCP server with middleware."""

    @patch('rag_fetch.mcp_server.connection_manager')
    async def test_server_tools_with_middleware_integration(self, mock_connection_manager):
        """Test that server tools work correctly with middleware."""
        # Setup connection manager mocks
        mock_connection_manager.create_connection.return_value = "integration-test-conn"
        mock_connection_manager.get_metrics.return_value = {
            "total_connections": 5,
            "current_connections": 2,
            "failed_connections": 0
        }
        mock_connection_manager.get_active_connections.return_value = {
            "conn-1": {"client_ip": "192.168.1.100", "user_agent": "TestClient"}
        }
        
        # Test server_status tool
        with patch('rag_fetch.mcp_server.config') as mock_config:
            mock_config.server_name = "Test Server"
            mock_config.transport.value = "http"
            mock_config.is_network_transport = True
            mock_config.host = "localhost"
            mock_config.port = 8000
            mock_config.mcp_endpoint = "http://localhost:8000/mcp"
            mock_config.max_connections = 100
            mock_config.connection_timeout = 300
            mock_config.chromadb_host = "localhost"
            mock_config.chromadb_port = 8001
            
            # Call the tool function directly
            result = mcp_server.server_status.fn()
            
            # Parse and verify result
            status = json.loads(result)
            self.assertEqual(status["server_name"], "Test Server")
            self.assertEqual(status["metrics"]["total_connections"], 5)
            self.assertEqual(status["metrics"]["current_connections"], 2)

    def test_async_test_runner_helper(self):
        """Helper to run async tests in sync context."""
        async def async_test():
            # This is a placeholder for async integration tests
            # In a real scenario, you might test the full MCP server with FastMCP Client
            self.assertTrue(True)
        
        # Run async test
        asyncio.run(async_test())


# Convert async test methods to sync for unittest
def run_async_test(test_func):
    """Helper to run async test functions."""
    def wrapper(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_func(self))
        finally:
            loop.close()
    return wrapper

# Apply the wrapper to async test methods in various classes
for cls in [TestConnectionTrackingMiddleware, TestMCPServerIntegrationWithMiddleware]:
    for name, method in cls.__dict__.items():
        if name.startswith('test_') and asyncio.iscoroutinefunction(method):
            setattr(cls, name, run_async_test(method))


if __name__ == "__main__":
    unittest.main()
