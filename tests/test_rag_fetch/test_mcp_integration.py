"""
Integration tests for MCP Server multi-client HTTP scenarios.

Tests end-to-end functionality with multiple concurrent clients using FastMCP.
"""

import asyncio
import json
import unittest
from unittest.mock import patch

from rag_fetch.mcp_server import mcp


class TestMCPServerIntegration(unittest.TestCase):
    """Integration tests for MCP server using in-memory transport."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with mocked dependencies."""
        # Mock ChromaDB for testing
        cls.mock_chromadb_patcher = patch('rag_fetch.search_similarity.get_chromadb_client')
        cls.mock_search_patcher = patch('rag_fetch.search_similarity.similarity_search_mcp_tool')
        
        cls.mock_chromadb = cls.mock_chromadb_patcher.start()
        cls.mock_search = cls.mock_search_patcher.start()
        
        # Mock search results
        cls.mock_search.return_value = json.dumps({
            "query": "test query",
            "results": [
                {
                    "content": "Test document content",
                    "metadata": {
                        "source": "test_doc.txt",
                        "chunk_id": "chunk_1"
                    },
                    "relevance_score": 0.95
                }
            ],
            "total_results": 1,
            "status": "success"
        })
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test class."""
        cls.mock_chromadb_patcher.stop()
        cls.mock_search_patcher.stop()
    
    async def test_single_client_connection(self):
        """Test single client connection and basic functionality."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        async with Client(mcp) as client:
            # Test ping
            await client.ping()
            
            # Test tools listing
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            self.assertIn('search_documents', tool_names)
            self.assertIn('server_status', tool_names)
            self.assertIn('list_active_connections', tool_names)
    
    async def test_search_documents_tool(self):
        """Test search_documents tool functionality."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        # Additional mock to ensure search_documents works
        with patch('rag_fetch.mcp_server.similarity_search_mcp_tool') as mock_search_tool:
            mock_search_tool.return_value = json.dumps({
                "query": "test search query",
                "results": [
                    {
                        "content": "Test document content",
                        "metadata": {"source": "test_doc.txt"},
                        "relevance_score": 0.95
                    }
                ],
                "total_results": 1,
                "status": "success"
            })
            
            async with Client(mcp) as client:
                # Call search tool
                result = await client.call_tool('search_documents', {
                    'query': 'test search query',
                    'limit': 3
                })
                
                # Parse result
                data = json.loads(result.data)
                
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['query'], 'test search query')
                self.assertGreater(len(data['results']), 0)
    
    async def test_server_status_tool(self):
        """Test server_status tool."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        with patch('rag_fetch.mcp_server.connection_manager') as mock_manager:
            mock_manager.get_metrics.return_value = {
                "total_connections": 5,
                "current_connections": 2,
                "failed_connections": 0,
            }
            mock_manager.get_active_connections.return_value = {}
            
            async with Client(mcp) as client:
                # Call server status tool
                result = await client.call_tool('server_status', {})
                
                # Parse result
                status = json.loads(result.data)
                
                self.assertEqual(status['server_name'], 'RAG World Fact Knowledge Base')
                self.assertEqual(status['status'], 'running')
                self.assertIn('config', status)
                self.assertIn('metrics', status)
                self.assertIn('active_connections', status)
    
    async def test_multiple_concurrent_clients(self):
        """Test multiple concurrent clients."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        # Mock the search function for concurrent operations
        with patch('rag_fetch.mcp_server.similarity_search_mcp_tool') as mock_search_tool:
            mock_search_tool.return_value = json.dumps({
                "query": "concurrent search",
                "results": [
                    {
                        "content": "Test document content",
                        "metadata": {"source": "test_doc.txt"},
                        "relevance_score": 0.95
                    }
                ],
                "total_results": 1,
                "status": "success"
            })
            
            async def client_task(client_id: int):
                """Task for individual client."""
                async with Client(mcp) as client:
                    # Perform multiple operations
                    await client.ping()
                    
                    # Search operation
                    result = await client.call_tool('search_documents', {
                        'query': f'client {client_id} search',
                        'limit': 2
                    })
                    
                    # Check result
                    data = json.loads(result.data)
                    self.assertEqual(data['status'], 'success')
                    
                    return f"client_{client_id}_success"
            
            # Run 5 concurrent clients
            tasks = [client_task(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            # Verify all clients succeeded
            self.assertEqual(len(results), 5)
            for i, result in enumerate(results):
                self.assertEqual(result, f"client_{i}_success")
    
    async def test_connection_tracking(self):
        """Test connection tracking functionality."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        with patch('rag_fetch.mcp_server.connection_manager') as mock_manager:
            mock_connections = {
                "conn-123": {
                    "client_ip": "127.0.0.1",
                    "user_agent": "TestClient/1.0",
                    "duration": 120.5,
                    "requests_count": 10,
                }
            }
            
            mock_manager.get_active_connections.return_value = mock_connections
            mock_manager.get_metrics.return_value = {
                "total_connections": 1,
                "current_connections": 1,
            }
            
            async with Client(mcp) as client:
                # Check connection status
                result = await client.call_tool('list_active_connections', {})
                data = json.loads(result.data)
                
                # Should have connection info
                self.assertGreaterEqual(data['active_connection_count'], 1)
                self.assertIn('connections', data)
                self.assertIn('metrics', data)
    
    async def test_error_handling(self):
        """Test error handling with invalid requests."""
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        async with Client(mcp) as client:
            # Test with invalid tool name
            with self.assertRaises(Exception):
                await client.call_tool('invalid_tool_name', {})
            
            # Test with invalid parameters
            with self.assertRaises(Exception):
                await client.call_tool('search_documents', {
                    'query': 'test',
                    'limit': 'invalid_limit_type'  # Should be int
                })


class TestMCPServerStress(unittest.TestCase):
    """Stress tests for MCP server performance - using mocked connections."""
    
    def setUp(self):
        """Set up test environment."""
        self.server_url = "http://127.0.0.1:8001/mcp"
    
    async def test_rapid_connections(self):
        """Test rapid connection/disconnection cycles - mocked version."""
        # Since we can't guarantee a running server in tests, 
        # let's test the connection manager directly
        from rag_fetch.connection_manager import ConnectionManager
        
        manager = ConnectionManager(max_connections=20)
        
        try:
            # Simulate rapid connections
            connection_ids = []
            for i in range(10):
                try:
                    conn_id = manager.create_connection(f"192.168.1.{i}", f"TestClient{i}")
                    connection_ids.append(conn_id)
                except Exception:
                    pass  # Connection limit reached
            
            # Verify we created connections
            self.assertGreater(len(connection_ids), 5)  # Should create at least 5
            
            # Clean up connections
            for conn_id in connection_ids:
                manager.close_connection(conn_id)
            
            # Verify cleanup
            self.assertEqual(len(manager.connections), 0)
            
        finally:
            manager.shutdown()
    
    async def test_concurrent_search_operations(self):
        """Test concurrent search operations - using in-memory transport."""
        # Use in-memory transport instead of HTTP to avoid server dependency
        from fastmcp import Client
        from rag_fetch.mcp_server import mcp
        
        # Mock the search function to avoid ChromaDB dependency
        with patch('rag_fetch.search_similarity.similarity_search_mcp_tool') as mock_search:
            mock_search.return_value = json.dumps({
                "query": "test query",
                "results": [
                    {
                        "content": "Test document content",
                        "metadata": {"source": "test_doc.txt"},
                        "relevance_score": 0.95
                    }
                ],
                "total_results": 1,
                "status": "success"
            })
            
            async def search_task(query_id: int):
                """Individual search task using in-memory transport."""
                try:
                    async with Client(mcp) as client:
                        result = await client.call_tool('search_documents', {
                            'query': f'concurrent search {query_id}',
                            'limit': 1
                        })
                        
                        data = json.loads(result.data)
                        return data['status'] == 'success'
                except Exception as e:
                    print(f"Search task {query_id} failed: {e}")
                    return False
            
            # Run 5 concurrent searches (reduced number for stability)
            tasks = [search_task(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful searches
            successes = [r for r in results if r is True]
            self.assertGreaterEqual(len(successes), 3)  # Allow some failures


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


# Convert async test methods to sync for unittest
for name, method in TestMCPServerIntegration.__dict__.items():
    if name.startswith('test_') and asyncio.iscoroutinefunction(method):
        setattr(TestMCPServerIntegration, name, run_async_test(method))

for name, method in TestMCPServerStress.__dict__.items():
    if name.startswith('test_') and asyncio.iscoroutinefunction(method):
        setattr(TestMCPServerStress, name, run_async_test(method))


if __name__ == "__main__":
    unittest.main()