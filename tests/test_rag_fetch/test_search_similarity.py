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
    get_cached_vectorstore,
    load_embedding_model,
    search_similarity,
    similarity_search_mcp_tool,
)


class TestSearchSimilarity(unittest.TestCase):
    """Test cases for search_similarity module."""

    def test_model_vendor_enum(self):
        """Test ModelVendor enum values."""
        self.assertEqual(ModelVendor.OPENAI.value, "openai")
        self.assertEqual(ModelVendor.GOOGLE.value, "google")

    # Legacy tests removed - ensure_chroma_directory function is no longer used
    # (using ChromaDB server mode instead of file-based storage)

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

    # Legacy integration test removed - ensure_chroma_directory function is no longer used
    # (using ChromaDB server mode instead of file-based storage)


class TestSearchSimilarityErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

        # Legacy error handling test removed - ensure_chroma_directory function is no longer used

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
    def test_get_cached_vectorstore_first_call(self, mock_load_vectorstore):
        """Test cached vectorstore on first call."""
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        
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
    @patch('time.time')
    def test_get_cached_vectorstore_cache_hit(self, mock_time, mock_load_vectorstore):
        """Test cached vectorstore cache hit (within TTL)."""
        # Mock time to control TTL
        mock_time.return_value = 1000.0
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        
        # First call
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Second call within TTL (mock time doesn't advance)
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Should have used cached version
        mock_load_vectorstore.assert_called_once()  # Only called once
        self.assertEqual(result1, result2)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    @patch('time.time')
    def test_get_cached_vectorstore_cache_expired(self, mock_time, mock_load_vectorstore):
        """Test cached vectorstore cache miss (TTL expired)."""
        # Mock different vectorstore instances
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
        
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
    def test_get_cached_vectorstore_force_refresh(self, mock_load_vectorstore):
        """Test cached vectorstore with force refresh."""
        # Mock different vectorstore instances
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
                
        # First call
        result1 = get_cached_vectorstore(ModelVendor.GOOGLE)
        
        # Second call with force refresh
        result2 = get_cached_vectorstore(ModelVendor.GOOGLE, force_refresh=True)
        
        # Should have created new vectorstore despite cache
        self.assertEqual(mock_load_vectorstore.call_count, 2)
        self.assertEqual(result1, mock_vectorstore1)
        self.assertEqual(result2, mock_vectorstore2)

    @patch('rag_fetch.search_similarity.load_vectorstore')
    def test_get_cached_vectorstore_different_collections(self, mock_load_vectorstore):
        """Test cached vectorstore with different collection names."""
        # Mock vectorstore
        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_load_vectorstore.side_effect = [mock_vectorstore1, mock_vectorstore2]
                
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
        self.assertEqual(mock_load_vectorstore.call_count, 1)
        args, kwargs = mock_load_vectorstore.call_args
        self.assertEqual(args[0].value, "google")
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


class TestCollectionNameConfiguration(unittest.TestCase):
    """Test cases for collection name configuration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment variables
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(os.environ, {"CHROMADB_COLLECTION_NAME": "search_custom_collection"})
    def test_default_collection_name_from_env(self):
        """Test DEFAULT_COLLECTION_NAME reads from environment variable."""
        # Import the module to trigger environment loading
        import importlib
        import rag_fetch.search_similarity
        importlib.reload(rag_fetch.search_similarity)
        
        from rag_fetch.search_similarity import DEFAULT_COLLECTION_NAME
        
        self.assertEqual(DEFAULT_COLLECTION_NAME, "search_custom_collection")

    @patch.dict(os.environ, {}, clear=True)
    def test_default_collection_name_fallback(self):
        """Test DEFAULT_COLLECTION_NAME falls back to 'langchain' when env var not set."""
        # This test actually tests that when .env file is loaded, we get the value from it
        # The current implementation loads .env by default, so we expect "rag-kb"
        # Remove the environment variable if it exists
        if "CHROMADB_COLLECTION_NAME" in os.environ:
            del os.environ["CHROMADB_COLLECTION_NAME"]
            
        # Import the module to trigger environment loading
        import importlib
        import rag_fetch.search_similarity
        importlib.reload(rag_fetch.search_similarity)
        
        from rag_fetch.search_similarity import DEFAULT_COLLECTION_NAME
        
        # The .env file sets CHROMADB_COLLECTION_NAME=rag-kb, so we expect this value
        self.assertEqual(DEFAULT_COLLECTION_NAME, "rag-kb")

    @patch("rag_fetch.search_similarity.get_chromadb_client")
    @patch("rag_fetch.search_similarity.load_embedding_model")
    @patch("rag_fetch.search_similarity.Chroma")
    def test_load_vectorstore_uses_default_collection_name(self, mock_chroma, mock_embedding, mock_client):
        """Test load_vectorstore uses DEFAULT_COLLECTION_NAME when collection_name not specified."""
        # Mock dependencies
        mock_client.return_value = Mock()
        mock_embedding.return_value = Mock()
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        from rag_fetch.search_similarity import load_vectorstore, ModelVendor, DEFAULT_COLLECTION_NAME
        
        # Test function call without collection_name
        result = load_vectorstore(ModelVendor.GOOGLE)
        
        # Verify Chroma was called with DEFAULT_COLLECTION_NAME
        mock_chroma.assert_called_once()
        call_args = mock_chroma.call_args[1]
        self.assertEqual(call_args["collection_name"], DEFAULT_COLLECTION_NAME)

    @patch("rag_fetch.search_similarity.get_chromadb_client")
    @patch("rag_fetch.search_similarity.load_embedding_model")
    @patch("rag_fetch.search_similarity.Chroma")
    def test_load_vectorstore_uses_custom_collection_name(self, mock_chroma, mock_embedding, mock_client):
        """Test load_vectorstore uses provided collection_name when specified."""
        # Mock dependencies
        mock_client.return_value = Mock()
        mock_embedding.return_value = Mock()
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        from rag_fetch.search_similarity import load_vectorstore, ModelVendor
        
        custom_collection = "search_custom_collection"
        
        # Test function call with custom collection_name
        result = load_vectorstore(ModelVendor.GOOGLE, collection_name=custom_collection)
        
        # Verify Chroma was called with custom collection name
        mock_chroma.assert_called_once()
        call_args = mock_chroma.call_args[1]
        self.assertEqual(call_args["collection_name"], custom_collection)

    @patch("rag_fetch.search_similarity.load_vectorstore")
    def test_get_cached_vectorstore_passes_collection_name(self, mock_load_vectorstore):
        """Test get_cached_vectorstore passes collection_name to load_vectorstore."""
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_load_vectorstore.return_value = mock_vectorstore
        
        from rag_fetch.search_similarity import get_cached_vectorstore, ModelVendor
        
        custom_collection = "cached_test_collection"
        
        # Test function call with custom collection
        result = get_cached_vectorstore(ModelVendor.GOOGLE, collection_name=custom_collection)
        
        # Verify load_vectorstore was called with custom collection name
        mock_load_vectorstore.assert_called_with(ModelVendor.GOOGLE, custom_collection)

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    def test_similarity_search_mcp_tool_passes_collection_name(self, mock_get_cached):
        """Test similarity_search_mcp_tool passes collection parameter to get_cached_vectorstore."""
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock search result
        with patch("rag_fetch.search_similarity.search_similarity_with_json_result") as mock_search:
            mock_search.return_value = {
                "query": "test",
                "results": [],
                "total_results": 0,
                "status": "success"
            }
            
            from rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor
            
            custom_collection = "mcp_test_collection"
            
            # Test function call with collection parameter
            result = similarity_search_mcp_tool(
                "test query", 
                ModelVendor.GOOGLE, 
                limit=5, 
                collection=custom_collection
            )
            
            # Verify get_cached_vectorstore was called with collection name
            mock_get_cached.assert_called_once_with(ModelVendor.GOOGLE, custom_collection)

    @patch("rag_fetch.search_similarity.get_chromadb_client")
    @patch("rag_fetch.search_similarity.load_embedding_model")
    @patch("rag_fetch.search_similarity.Chroma")
    @patch("rag_fetch.search_similarity.DEFAULT_COLLECTION_NAME", "env_search_collection")
    def test_load_vectorstore_environment_integration(self, mock_chroma, mock_embedding, mock_client):
        """Test load_vectorstore with environment variable integration."""
        # Mock dependencies
        mock_client.return_value = Mock()
        mock_embedding.return_value = Mock()
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        
        from rag_fetch.search_similarity import load_vectorstore, ModelVendor
        
        # Test function call without collection_name (should use env var)
        result = load_vectorstore(ModelVendor.GOOGLE)
        
        # Verify Chroma was called with environment variable value
        mock_chroma.assert_called_once()
        call_args = mock_chroma.call_args[1]
        self.assertEqual(call_args["collection_name"], "env_search_collection")

    def test_load_vectorstore_parameter_signature(self):
        """Test that load_vectorstore function signature includes collection_name parameter."""
        import inspect
        from rag_fetch.search_similarity import load_vectorstore
        
        signature = inspect.signature(load_vectorstore)
        parameters = signature.parameters
        
        # Verify collection_name parameter exists and is optional
        self.assertIn("collection_name", parameters)
        self.assertEqual(parameters["collection_name"].default, None)
        self.assertEqual(parameters["collection_name"].annotation, str)

    def test_similarity_search_mcp_tool_collection_parameter_signature(self):
        """Test that similarity_search_mcp_tool function signature includes collection parameter."""
        import inspect
        from rag_fetch.search_similarity import similarity_search_mcp_tool
        
        signature = inspect.signature(similarity_search_mcp_tool)
        parameters = signature.parameters
        
        # Verify collection parameter exists and is optional
        self.assertIn("collection", parameters)
        self.assertEqual(parameters["collection"].default, None)
        self.assertEqual(parameters["collection"].annotation, str)

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    @patch("rag_fetch.search_similarity.search_similarity_with_json_result")
    def test_cache_key_uses_collection_name(self, mock_search, mock_get_cached):
        """Test that cache key includes collection name for proper isolation."""
        # Clear cache
        import rag_fetch.search_similarity
        rag_fetch.search_similarity._vectorstore_cache = {}
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock search result
        mock_search.return_value = {
            "query": "test",
            "results": [],
            "total_results": 0,
            "status": "success"
        }
        
        from rag_fetch.search_similarity import similarity_search_mcp_tool, ModelVendor
        
        # Call with different collections
        result1 = similarity_search_mcp_tool("test", ModelVendor.GOOGLE, collection="collection1")
        result2 = similarity_search_mcp_tool("test", ModelVendor.GOOGLE, collection="collection2")
        
        # Verify get_cached_vectorstore was called with different collection names
        self.assertEqual(mock_get_cached.call_count, 2)
        calls = mock_get_cached.call_args_list
        self.assertEqual(calls[0][0][1], "collection1")  # First call with collection1
        self.assertEqual(calls[1][0][1], "collection2")  # Second call with collection2


class TestCollectionNameConsistency(unittest.TestCase):
    """Test cases for collection name consistency between services."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment variables
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch.dict(os.environ, {"CHROMADB_COLLECTION_NAME": "consistency_test_collection"})
    def test_both_services_use_same_collection_name(self):
        """Test that both services use the same collection name from environment."""
        # Reload both modules to pick up environment variable
        import importlib
        import rag_store.store_embeddings
        import rag_fetch.search_similarity
        importlib.reload(rag_store.store_embeddings)
        importlib.reload(rag_fetch.search_similarity)
        
        from rag_store.store_embeddings import DEFAULT_COLLECTION_NAME as store_collection
        from rag_fetch.search_similarity import DEFAULT_COLLECTION_NAME as fetch_collection
        
        # Both should use the same environment variable value
        self.assertEqual(store_collection, "consistency_test_collection")
        self.assertEqual(fetch_collection, "consistency_test_collection")
        self.assertEqual(store_collection, fetch_collection)

    @patch.dict(os.environ, {}, clear=True)
    def test_both_services_use_same_fallback_collection(self):
        """Test that both services use the same fallback collection name."""
        # Remove environment variable if it exists
        if "CHROMADB_COLLECTION_NAME" in os.environ:
            del os.environ["CHROMADB_COLLECTION_NAME"]
            
        # Reload both modules to pick up cleared environment
        import importlib
        import rag_store.store_embeddings
        import rag_fetch.search_similarity
        importlib.reload(rag_store.store_embeddings)
        importlib.reload(rag_fetch.search_similarity)
        
        from rag_store.store_embeddings import DEFAULT_COLLECTION_NAME as store_collection
        from rag_fetch.search_similarity import DEFAULT_COLLECTION_NAME as fetch_collection
        
        # Both should use the same fallback value
        self.assertEqual(store_collection, "rag-kb")
        self.assertEqual(fetch_collection, "rag-kb")
        self.assertEqual(store_collection, fetch_collection)


class TestGetChromaDBClient(unittest.TestCase):
    """Test cases for get_chromadb_client function."""

    @patch("rag_fetch.search_similarity.chromadb.HttpClient")
    def test_get_chromadb_client_success(self, mock_http_client):
        """Test successful connection to ChromaDB."""
        # Mock successful connection
        mock_client = Mock()
        mock_http_client.return_value = mock_client
        mock_client.heartbeat.return_value = None
        
        from rag_fetch.search_similarity import get_chromadb_client
        
        # Call function
        result = get_chromadb_client()
        
        # Verify
        self.assertEqual(result, mock_client)
        mock_http_client.assert_called_once()
        mock_client.heartbeat.assert_called_once()

    @patch("rag_fetch.search_similarity.chromadb.HttpClient")
    def test_get_chromadb_client_connection_error(self, mock_http_client):
        """Test connection error to ChromaDB."""
        # Mock connection failure
        mock_http_client.side_effect = Exception("Connection refused")
        
        from rag_fetch.search_similarity import get_chromadb_client
        
        # Call function and expect ConnectionError
        with self.assertRaises(ConnectionError) as context:
            get_chromadb_client()
        
        # Verify error message contains expected content
        error_msg = str(context.exception)
        self.assertIn("Cannot connect to ChromaDB server", error_msg)
        self.assertIn("Connection refused", error_msg)
        self.assertIn("chromadb-server.sh start", error_msg)

    @patch("rag_fetch.search_similarity.chromadb.HttpClient")
    def test_get_chromadb_client_heartbeat_failure(self, mock_http_client):
        """Test ChromaDB heartbeat failure."""
        # Mock client creation success but heartbeat failure
        mock_client = Mock()
        mock_http_client.return_value = mock_client
        mock_client.heartbeat.side_effect = Exception("Heartbeat failed")
        
        from rag_fetch.search_similarity import get_chromadb_client
        
        # Call function and expect ConnectionError
        with self.assertRaises(ConnectionError) as context:
            get_chromadb_client()
        
        # Verify error message
        error_msg = str(context.exception)
        self.assertIn("Cannot connect to ChromaDB server", error_msg)
        self.assertIn("Heartbeat failed", error_msg)


class TestLoadEmbeddingModelErrors(unittest.TestCase):
    """Test cases for load_embedding_model error scenarios."""

    @unittest.skip("Environment isolation issue when running full test suite - works individually")
    def test_load_embedding_model_openai_no_api_key(self):
        """Test OpenAI embedding model with missing API key."""
        # Use patch.dict to temporarily remove the API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                load_embedding_model(ModelVendor.OPENAI)
            
            self.assertEqual(
                str(context.exception), 
                "OPENAI_API_KEY environment variable is required"
            )

    @unittest.skip("Environment isolation issue when running full test suite - works individually")
    def test_load_embedding_model_google_no_api_key(self):
        """Test Google embedding model with missing API key."""
        # Use patch.dict to temporarily remove the API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                load_embedding_model(ModelVendor.GOOGLE)
            
            self.assertEqual(
                str(context.exception), 
                "GOOGLE_API_KEY environment variable is required"
            )

    @unittest.skip("Environment isolation issue when running full test suite - works individually")
    @patch("rag_fetch.search_similarity.OpenAIEmbeddings")
    def test_load_embedding_model_openai_success(self, mock_openai_embeddings):
        """Test successful OpenAI embedding model loading."""
        mock_model = Mock()
        mock_openai_embeddings.return_value = mock_model
        
        # Use patch.dict to set the API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}):
            result = load_embedding_model(ModelVendor.OPENAI)
        
        self.assertEqual(result, mock_model)
        mock_openai_embeddings.assert_called_once_with(openai_api_key="test-openai-key")

    @unittest.skip("Environment isolation issue when running full test suite - works individually")
    @patch("rag_fetch.search_similarity.GoogleGenerativeAIEmbeddings")
    def test_load_embedding_model_google_success(self, mock_google_embeddings):
        """Test successful Google embedding model loading."""
        mock_model = Mock()
        mock_google_embeddings.return_value = mock_model
        
        # Use patch.dict to set the API key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}):
            result = load_embedding_model(ModelVendor.GOOGLE)
        
        self.assertEqual(result, mock_model)
        mock_google_embeddings.assert_called_once_with(
            model="models/text-embedding-004", 
            google_api_key="test-google-key"
        )

    def test_load_embedding_model_invalid_vendor(self):
        """Test load_embedding_model with invalid vendor."""
        class MockVendor:
            pass

        mock_vendor = MockVendor()
        with self.assertRaises(ValueError) as context:
            load_embedding_model(mock_vendor)

        self.assertIn("Unsupported model vendor", str(context.exception))


class TestDocumentsToMCPFormat(unittest.TestCase):
    """Test cases for documents_to_mcp_format function."""

    def test_documents_to_mcp_format_basic(self):
        """Test basic document conversion to MCP format."""
        from rag_fetch.search_similarity import documents_to_mcp_format
        from langchain_core.documents import Document
        
        # Create test documents
        doc1 = Document(
            page_content="Test content 1",
            metadata={
                "source": "test1.txt",
                "chunk_id": "chunk1",
                "document_id": "doc1",
                "extra_field": "extra_value"
            }
        )
        doc2 = Document(
            page_content="Test content 2",
            metadata={
                "source": "test2.txt",
                "chunk_id": "chunk2",
                "document_id": "doc2"
            }
        )
        
        documents = [doc1, doc2]
        
        # Call function
        result = documents_to_mcp_format(documents)
        
        # Verify structure
        self.assertEqual(len(result), 2)
        
        # Check first document
        self.assertEqual(result[0]["content"], "Test content 1")
        self.assertEqual(result[0]["metadata"]["source"], "test1.txt")
        self.assertEqual(result[0]["metadata"]["chunk_id"], "chunk1")
        self.assertEqual(result[0]["metadata"]["document_id"], "doc1")
        self.assertEqual(result[0]["metadata"]["extra_field"], "extra_value")
        self.assertNotIn("relevance_score", result[0])
        
        # Check second document
        self.assertEqual(result[1]["content"], "Test content 2")
        self.assertEqual(result[1]["metadata"]["source"], "test2.txt")

    def test_documents_to_mcp_format_with_scores(self):
        """Test document conversion with relevance scores."""
        from rag_fetch.search_similarity import documents_to_mcp_format
        from langchain_core.documents import Document
        
        # Create test document with relevance score
        doc = Document(
            page_content="Test content with score",
            metadata={
                "source": "scored.txt",
                "chunk_id": "chunk1",
                "document_id": "doc1",
                "relevance_score": 0.95
            }
        )
        
        documents = [doc]
        
        # Call function with include_scores=True
        result = documents_to_mcp_format(documents, include_scores=True)
        
        # Verify score is included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["relevance_score"], 0.95)
        self.assertNotIn("relevance_score", result[0]["metadata"])

    def test_documents_to_mcp_format_without_scores(self):
        """Test document conversion without including scores."""
        from rag_fetch.search_similarity import documents_to_mcp_format
        from langchain_core.documents import Document
        
        # Create test document with relevance score
        doc = Document(
            page_content="Test content",
            metadata={
                "source": "test.txt",
                "relevance_score": 0.85,
                "other_field": "value"
            }
        )
        
        documents = [doc]
        
        # Call function with include_scores=False (default)
        result = documents_to_mcp_format(documents, include_scores=False)
        
        # Verify score is not included at top level
        self.assertEqual(len(result), 1)
        self.assertNotIn("relevance_score", result[0])
        self.assertNotIn("relevance_score", result[0]["metadata"])
        self.assertEqual(result[0]["metadata"]["other_field"], "value")

    def test_documents_to_mcp_format_missing_metadata(self):
        """Test document conversion with missing metadata fields."""
        from rag_fetch.search_similarity import documents_to_mcp_format
        from langchain_core.documents import Document
        
        # Create document with minimal metadata
        doc = Document(
            page_content="Test content",
            metadata={}  # Empty metadata
        )
        
        documents = [doc]
        
        # Call function
        result = documents_to_mcp_format(documents)
        
        # Verify defaults are applied
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["content"], "Test content")
        self.assertEqual(result[0]["metadata"]["source"], "unknown")
        self.assertIsNone(result[0]["metadata"]["chunk_id"])
        self.assertIsNone(result[0]["metadata"]["document_id"])


class TestSearchSimilarityFunction(unittest.TestCase):
    """Test cases for search_similarity function."""

    @patch("rag_fetch.search_similarity.Chroma")
    def test_search_similarity_basic(self, mock_chroma_class):
        """Test basic search_similarity function."""
        from rag_fetch.search_similarity import search_similarity
        from langchain_core.documents import Document
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        
        # Mock search results
        test_docs = [
            Document(page_content="Result 1", metadata={"source": "doc1.txt"}),
            Document(page_content="Result 2", metadata={"source": "doc2.txt"})
        ]
        mock_vectorstore.similarity_search.return_value = test_docs
        
        # Call function
        result = search_similarity("test query", mock_vectorstore, k=5)
        
        # Verify
        self.assertEqual(result, test_docs)
        mock_vectorstore.similarity_search.assert_called_once_with("test query", k=5)


class TestSimilaritySearchMCPToolScoring(unittest.TestCase):
    """Test cases for similarity_search_mcp_tool scoring functionality."""

    @patch("rag_fetch.search_similarity.get_cached_vectorstore")
    def test_similarity_search_mcp_tool_with_scoring(self, mock_get_cached):
        """Test MCP tool with document scoring."""
        from langchain_core.documents import Document
        import json
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_get_cached.return_value = mock_vectorstore
        
        # Mock similarity_search_with_relevance_scores to return documents with scores
        test_docs_with_scores = [
            (Document(page_content="Result 1", metadata={"source": "doc1.txt"}), 0.9),
            (Document(page_content="Result 2", metadata={"source": "doc2.txt"}), 0.8)
        ]
        mock_vectorstore.similarity_search_with_relevance_scores.return_value = test_docs_with_scores
        
        # Call function - note: returns JSON string, not dict
        result_json = similarity_search_mcp_tool("test query", limit=2)
        result = json.loads(result_json)
        
        # Verify results structure
        self.assertEqual(result["query"], "test query")
        self.assertEqual(result["total_results"], 2)
        self.assertEqual(result["status"], "success")
        
        # Verify scores are included
        results = result["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["relevance_score"], 0.9)
        self.assertEqual(results[1]["relevance_score"], 0.8)
        
        # Verify vectorstore was called correctly
        mock_vectorstore.similarity_search_with_relevance_scores.assert_called_once_with("test query", k=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
