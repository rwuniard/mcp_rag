"""
Unit tests for search_similarity module.

This test suite covers the document search and similarity functionality.
"""

import json
import os
import time

# Import the module to test
import sys
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_fetch.search_similarity import (
    ModelVendor,
    ensure_chroma_directory,
    get_cached_vectorstore,
    load_embedding_model,
    refresh_vectorstore_data,
    search_similarity,
    similarity_search_mcp_tool,
)


class TestSearchSimilarity(unittest.TestCase):
    """Test cases for search_similarity module."""

    def test_model_vendor_enum(self):
        """Test ModelVendor enum values."""
        self.assertEqual(ModelVendor.OPENAI.value, "openai")
        self.assertEqual(ModelVendor.GOOGLE.value, "google")

    def test_ensure_chroma_directory_google(self):
        """Test ensuring Chroma directory for Google model."""
        result = ensure_chroma_directory(ModelVendor.GOOGLE)

        self.assertIsInstance(result, Path)
        self.assertTrue("chroma_db_google" in str(result))

    def test_ensure_chroma_directory_openai(self):
        """Test ensuring Chroma directory for OpenAI model."""
        result = ensure_chroma_directory(ModelVendor.OPENAI)

        self.assertIsInstance(result, Path)
        self.assertTrue("chroma_db_openai" in str(result))

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    @patch("rag_fetch.search_similarity.search_similarity_with_json_result")
    def test_similarity_search_mcp_tool_success(
        self, mock_json_result, mock_get_cached
    ):
        """Test successful similarity search with MCP tool format."""
        # Mock cached vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore

        # Mock search results
        mock_json_result.return_value = {
            "query": "Python programming",
            "results": [
                {
                    "content": "Test content about Python programming",
                    "metadata": {"source": "test.txt", "chunk_id": 0},
                    "relevance_score": 0.85
                },
                {
                    "content": "More content about machine learning", 
                    "metadata": {"source": "test2.txt", "chunk_id": 1},
                    "relevance_score": 0.72
                }
            ],
            "total_results": 2,
            "status": "success"
        }

        # Test the function
        result = similarity_search_mcp_tool(
            "Python programming", ModelVendor.GOOGLE, limit=2
        )

        # Parse the JSON result
        result_data = json.loads(result)

        # Verify the structure
        self.assertEqual(result_data["status"], "success")
        self.assertEqual(result_data["query"], "Python programming")
        self.assertEqual(result_data["total_results"], 2)
        self.assertEqual(len(result_data["results"]), 2)

        # Verify first result
        first_result = result_data["results"][0]
        self.assertEqual(
            first_result["content"], "Test content about Python programming"
        )
        self.assertEqual(first_result["relevance_score"], 0.85)
        self.assertEqual(first_result["metadata"]["source"], "test.txt")

        # Verify second result
        second_result = result_data["results"][1]
        self.assertEqual(
            second_result["content"], "More content about machine learning"
        )
        self.assertEqual(second_result["relevance_score"], 0.72)

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    @patch("rag_fetch.search_similarity.search_similarity_with_json_result")
    def test_similarity_search_mcp_tool_no_results(
        self, mock_json_result, mock_get_cached
    ):
        """Test similarity search with no results."""
        # Mock cached vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore

        # Mock search results with no results
        mock_json_result.return_value = {
            "query": "nonexistent query",
            "results": [],
            "total_results": 0,
            "status": "success"
        }

        # Test the function
        result = similarity_search_mcp_tool(
            "nonexistent query", ModelVendor.GOOGLE, limit=5
        )

        # Parse the JSON result
        result_data = json.loads(result)

        # Verify the structure
        self.assertEqual(result_data["status"], "success")
        self.assertEqual(result_data["query"], "nonexistent query")
        self.assertEqual(result_data["total_results"], 0)
        self.assertEqual(len(result_data["results"]), 0)

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    def test_similarity_search_mcp_tool_error_handling(self, mock_get_cached):
        """Test similarity search error handling."""
        # Mock get_cached_vectorstore to raise an exception
        mock_get_cached.side_effect = Exception("Database directory not found")

        # Test the function
        result = similarity_search_mcp_tool("test query", ModelVendor.GOOGLE, limit=3)

        # Parse the JSON result
        result_data = json.loads(result)

        # Verify error response
        self.assertEqual(result_data["status"], "error")
        self.assertEqual(result_data["query"], "test query")
        self.assertIn("error", result_data)
        self.assertIn("Database directory not found", result_data["error"])

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    @patch("rag_fetch.search_similarity.search_similarity_with_json_result")
    def test_similarity_search_default_parameters(self, mock_json_result, mock_get_cached):
        """Test that similarity search handles default parameters correctly."""
        # Mock cached vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock search results
        mock_json_result.return_value = {
            "query": "test",
            "results": [],
            "total_results": 0,
            "status": "success"
        }

        # Test with default limit (should be handled gracefully)
        result = similarity_search_mcp_tool("test", ModelVendor.GOOGLE)
        result_data = json.loads(result)

        self.assertEqual(result_data["status"], "success")


class TestSearchSimilarityIntegration(unittest.TestCase):
    """Integration tests for search_similarity functionality."""

    def test_model_vendor_paths(self):
        """Test that ModelVendor creates correct directory paths."""
        google_path = ensure_chroma_directory(ModelVendor.GOOGLE)
        openai_path = ensure_chroma_directory(ModelVendor.OPENAI)

        self.assertNotEqual(google_path, openai_path)
        self.assertIn("google", str(google_path).lower())
        self.assertIn("openai", str(openai_path).lower())


class TestSearchSimilarityErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def test_ensure_chroma_directory_invalid_vendor(self):
        """Test ensure_chroma_directory with invalid vendor."""
        # Create a mock vendor that's not in the enum
        class MockVendor:
            pass
        
        mock_vendor = MockVendor()
        with self.assertRaises(ValueError) as context:
            ensure_chroma_directory(mock_vendor)
        
        self.assertIn("Unsupported model vendor", str(context.exception))

    @patch.dict(os.environ, {}, clear=True)
    def test_load_embedding_model_missing_openai_key(self):
        """Test load_embedding_model with missing OPENAI_API_KEY."""
        with self.assertRaises(ValueError) as context:
            load_embedding_model(ModelVendor.OPENAI)
        
        self.assertIn("OPENAI_API_KEY environment variable is required", str(context.exception))

    @patch.dict(os.environ, {}, clear=True) 
    def test_load_embedding_model_missing_google_key(self):
        """Test load_embedding_model with missing GOOGLE_API_KEY."""
        with self.assertRaises(ValueError) as context:
            load_embedding_model(ModelVendor.GOOGLE)
        
        self.assertIn("GOOGLE_API_KEY environment variable is required", str(context.exception))

    def test_load_embedding_model_invalid_vendor(self):
        """Test load_embedding_model with invalid vendor."""
        class MockVendor:
            pass
        
        mock_vendor = MockVendor()
        with self.assertRaises(ValueError) as context:
            load_embedding_model(mock_vendor)
        
        self.assertIn("Unsupported model vendor", str(context.exception))

    def test_search_similarity_exception_handling(self):
        """Test search_similarity exception handling."""
        # Mock vectorstore that raises an exception
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.side_effect = Exception("Search failed")
        
        # Test the function
        results = search_similarity("test query", mock_vectorstore)
        
        # Should return empty list on exception
        self.assertEqual(results, [])

    @patch('rag_fetch.search_similarity.load_vectorstore')
    def test_search_similarity_with_json_result_exception(self, mock_load_vectorstore):
        """Test search_similarity_with_json_result exception handling."""
        # Mock vectorstore that raises an exception  
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search_with_relevance_scores.side_effect = Exception("Database error")
        mock_load_vectorstore.return_value = mock_vectorstore
        
        from rag_fetch.search_similarity import search_similarity_with_json_result
        
        # Test the function
        result = search_similarity_with_json_result("test query", mock_vectorstore)
        
        # Should return error response
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["query"], "test query")
        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["results"], [])
        self.assertIn("Database error", result["error"])


class TestVectorstoreRefresh(unittest.TestCase):
    """Test cases for vectorstore refresh functionality."""

    def test_refresh_vectorstore_data_success(self):
        """Test successful vectorstore data refresh."""
        # Mock vectorstore with collection
        mock_vectorstore = Mock()
        mock_collection = Mock()
        mock_vectorstore._collection = mock_collection
        
        # Test refresh
        result = refresh_vectorstore_data(mock_vectorstore)
        
        # Verify refresh was called and returned True
        mock_collection.get.assert_called_once_with(limit=1)
        self.assertTrue(result)

    def test_refresh_vectorstore_data_no_collection(self):
        """Test vectorstore refresh when no collection exists."""
        # Mock vectorstore without collection
        mock_vectorstore = Mock()
        mock_vectorstore._collection = None
        
        # Test refresh
        result = refresh_vectorstore_data(mock_vectorstore)
        
        # Should return False when no collection
        self.assertFalse(result)

    def test_refresh_vectorstore_data_missing_attribute(self):
        """Test vectorstore refresh when _collection attribute doesn't exist."""
        # Mock vectorstore without _collection attribute
        mock_vectorstore = Mock(spec=[])  # Empty spec means no attributes
        
        # Test refresh
        result = refresh_vectorstore_data(mock_vectorstore)
        
        # Should return False when attribute doesn't exist
        self.assertFalse(result)

    @patch('builtins.print')
    def test_refresh_vectorstore_data_exception(self, mock_print):
        """Test vectorstore refresh exception handling."""
        # Mock vectorstore that raises exception
        mock_vectorstore = Mock()
        mock_collection = Mock()
        mock_collection.get.side_effect = Exception("Refresh failed")
        mock_vectorstore._collection = mock_collection
        
        # Test refresh
        result = refresh_vectorstore_data(mock_vectorstore)
        
        # Should return False on exception and print warning
        self.assertFalse(result)
        mock_print.assert_called_once_with("Warning: Failed to refresh vectorstore data: Refresh failed")


class TestCachedVectorstore(unittest.TestCase):
    """Test cases for cached vectorstore functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear the cache before each test
        import rag_fetch.search_similarity
        rag_fetch.search_similarity._vectorstore_cache = {}

    def tearDown(self):
        """Clean up after each test."""
        # Clear the cache after each test
        import rag_fetch.search_similarity
        rag_fetch.search_similarity._vectorstore_cache = {}

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.refresh_vectorstore_data')
    def test_get_cached_vectorstore_first_call(self, mock_refresh, mock_load_vectorstore):
        """Test cached vectorstore on first call."""
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        mock_refresh.return_value = True
        
        # First call should create new vectorstore
        result = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Verify vectorstore was loaded and cached
        mock_load_vectorstore.assert_called_once_with(ModelVendor.GOOGLE, None)
        self.assertEqual(result, mock_vectorstore)
        
        # Verify cache was populated
        import rag_fetch.search_similarity
        cache_key = "google_default"
        self.assertIn(cache_key, rag_fetch.search_similarity._vectorstore_cache)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.refresh_vectorstore_data')
    @patch('time.time')
    def test_get_cached_vectorstore_cache_hit(self, mock_time, mock_refresh, mock_load_vectorstore):
        """Test cached vectorstore cache hit (within TTL)."""
        # Mock time to control TTL
        mock_time.return_value = 1000.0
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        mock_refresh.return_value = True
        
        # First call
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Second call within TTL (mock time doesn't advance)
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Should have used cached version
        mock_load_vectorstore.assert_called_once()  # Only called once
        self.assertEqual(result1, result2)
        
        # Refresh should only be called on cache hit (not on initial load)
        self.assertEqual(mock_refresh.call_count, 1)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.refresh_vectorstore_data')
    @patch('time.time')
    def test_get_cached_vectorstore_cache_expired(self, mock_time, mock_refresh, mock_load_vectorstore):
        """Test cached vectorstore cache miss (TTL expired)."""
        # Mock different vectorstore instances
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
        mock_refresh.return_value = True
        
        # First call at time 1000
        mock_time.return_value = 1000.0
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Second call at time 1040 (beyond 30s TTL)
        mock_time.return_value = 1040.0
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Should have created new vectorstore
        self.assertEqual(mock_load_vectorstore.call_count, 2)
        self.assertEqual(result1, mock_vectorstore1)
        self.assertEqual(result2, mock_vectorstore2)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.refresh_vectorstore_data')
    def test_get_cached_vectorstore_force_refresh(self, mock_refresh, mock_load_vectorstore):
        """Test cached vectorstore with force refresh."""
        # Mock different vectorstore instances
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
        mock_refresh.return_value = True
        
        # First call
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Second call with force refresh
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE, force_refresh=True)
        
        # Should have created new vectorstore despite cache
        self.assertEqual(mock_load_vectorstore.call_count, 2)
        self.assertEqual(result1, mock_vectorstore1)
        self.assertEqual(result2, mock_vectorstore2)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.refresh_vectorstore_data')
    def test_get_cached_vectorstore_different_collections(self, mock_refresh, mock_load_vectorstore):
        """Test cached vectorstore with different collection names."""
        # Mock vectorstore
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
        mock_refresh.return_value = True
        
        # Calls with different collections should create separate cache entries
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE, "collection1")
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE, "collection2")
        
        # Should have created separate vectorstores
        self.assertEqual(mock_load_vectorstore.call_count, 2)
        mock_load_vectorstore.assert_any_call(ModelVendor.GOOGLE, "collection1")
        mock_load_vectorstore.assert_any_call(ModelVendor.GOOGLE, "collection2")


class TestUpdatedMCPTool(unittest.TestCase):
    """Test cases for updated similarity_search_mcp_tool with refresh functionality."""

    @patch('rag_fetch.search_similarity.get_cached_vectorstore')
    @patch('rag_fetch.search_similarity.search_similarity_with_json_result')
    def test_similarity_search_mcp_tool_uses_cached_vectorstore(self, mock_json_result, mock_get_cached):
        """Test that MCP tool uses cached vectorstore."""
        # Mock cached vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock search result
        mock_json_result.return_value = {
            "query": "test query",
            "results": [],
            "total_results": 0,
            "status": "success"
        }
        
        # Call the function
        result = similarity_search_mcp_tool("test query", ModelVendor.GOOGLE, limit=5)
        
        # Verify cached vectorstore was used
        mock_get_cached.assert_called_once_with(ModelVendor.GOOGLE, None)
        mock_json_result.assert_called_once_with("test query", mock_vectorstore, 5)
        
        # Verify result
        result_data = json.loads(result)
        self.assertEqual(result_data["status"], "success")

    @patch('rag_fetch.search_similarity.get_cached_vectorstore')
    @patch('rag_fetch.search_similarity.search_similarity_with_json_result')
    def test_similarity_search_mcp_tool_with_collection(self, mock_json_result, mock_get_cached):
        """Test MCP tool with collection parameter."""
        # Mock cached vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock search result
        mock_json_result.return_value = {
            "query": "test query",
            "results": [],
            "total_results": 0,
            "status": "success"
        }
        
        # Call with collection
        result = similarity_search_mcp_tool("test query", ModelVendor.GOOGLE, limit=3, collection="test_collection")
        
        # Verify collection was passed through
        mock_get_cached.assert_called_once_with(ModelVendor.GOOGLE, "test_collection")


class TestMainFunction(unittest.TestCase):
    """Test the main function for coverage."""
    
    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('rag_fetch.search_similarity.search_similarity')
    @patch('rag_fetch.search_similarity.search_similarity_with_json_result')
    @patch('rag_fetch.search_similarity.similarity_search_mcp_tool')
    @patch('builtins.print')
    def test_main_function_success(self, mock_print, mock_mcp_tool, mock_json_result, mock_search, mock_load_vectorstore):
        """Test main function successful execution."""
        # Mock successful responses
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        
        mock_doc = Mock()
        mock_doc.page_content = "Test content about Python classes"
        mock_doc.metadata = {"source": "test.txt"}
        mock_search.return_value = [mock_doc, mock_doc]
        
        mock_json_result.return_value = {"query": "test", "results": [], "status": "success"}
        mock_mcp_tool.return_value = '{"status": "success", "results": []}'
        
        from rag_fetch.search_similarity import main
        
        # Call main function
        main()
        
        # Verify function calls
        mock_load_vectorstore.assert_called_once_with(ModelVendor.GOOGLE)
        mock_search.assert_called_once()
        mock_json_result.assert_called_once()
        # MCP tool is called twice in main function (steps 3 and 4)
        self.assertEqual(mock_mcp_tool.call_count, 2)
        
        # Verify print statements were called
        self.assertTrue(mock_print.called)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('builtins.print')
    def test_main_function_exception(self, mock_print, mock_load_vectorstore):
        """Test main function exception handling."""
        # Mock exception
        mock_load_vectorstore.side_effect = Exception("Database connection failed")
        
        from rag_fetch.search_similarity import main
        
        # Call main function
        main()
        
        # Verify error handling print statements
        mock_print.assert_any_call("Error during testing: Database connection failed")
        mock_print.assert_any_call("Make sure you have:")
        mock_print.assert_any_call("1. GOOGLE_API_KEY set in your .env file")
        mock_print.assert_any_call("2. Documents stored in the ChromaDB database")


if __name__ == "__main__":
    unittest.main(verbosity=2)
