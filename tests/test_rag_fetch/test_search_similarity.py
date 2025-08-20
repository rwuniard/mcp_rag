"""
Unit tests for search_similarity module.

This test suite covers the document search and similarity functionality.
"""

import json
import os

# Import the module to test
import sys
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_fetch.search_similarity import (
    ModelVendor,
    ensure_chroma_directory,
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

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    @patch("rag_fetch.search_similarity.Path.exists")
    @patch("rag_fetch.search_similarity.Chroma")
    @patch("rag_fetch.search_similarity.GoogleGenerativeAIEmbeddings")
    def test_similarity_search_mcp_tool_success(
        self, mock_embeddings, mock_chroma, mock_path_exists
    ):
        """Test successful similarity search with MCP tool format."""
        # Mock path exists check
        mock_path_exists.return_value = True

        # Mock the embedding model
        mock_embedding_model = Mock()
        mock_embeddings.return_value = mock_embedding_model

        # Mock the Chroma vectorstore
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore

        # Mock search results
        mock_doc1 = Mock()
        mock_doc1.page_content = "Test content about Python programming"
        mock_doc1.metadata = {"source": "test.txt", "chunk_id": 0}

        mock_doc2 = Mock()
        mock_doc2.page_content = "More content about machine learning"
        mock_doc2.metadata = {"source": "test2.txt", "chunk_id": 1}

        mock_vectorstore.similarity_search_with_relevance_scores.return_value = [
            (mock_doc1, 0.85),
            (mock_doc2, 0.72),
        ]

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

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    @patch("rag_fetch.search_similarity.Path.exists")
    @patch("rag_fetch.search_similarity.Chroma")
    @patch("rag_fetch.search_similarity.GoogleGenerativeAIEmbeddings")
    def test_similarity_search_mcp_tool_no_results(
        self, mock_embeddings, mock_chroma, mock_path_exists
    ):
        """Test similarity search with no results."""
        # Mock path exists check
        mock_path_exists.return_value = True

        # Mock the embedding model
        mock_embedding_model = Mock()
        mock_embeddings.return_value = mock_embedding_model

        # Mock the Chroma vectorstore with no results
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        mock_vectorstore.similarity_search_with_relevance_scores.return_value = []

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

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    @patch("rag_fetch.search_similarity.Path.exists")
    def test_similarity_search_mcp_tool_error_handling(self, mock_path_exists):
        """Test similarity search error handling."""
        # Mock the database directory to not exist, which will trigger an error
        mock_path_exists.return_value = False

        # Test the function
        result = similarity_search_mcp_tool("test query", ModelVendor.GOOGLE, limit=3)

        # Parse the JSON result
        result_data = json.loads(result)

        # Verify error response
        self.assertEqual(result_data["status"], "error")
        self.assertEqual(result_data["query"], "test query")
        self.assertIn("error", result_data)
        self.assertIn("Database directory not found", result_data["error"])

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    def test_similarity_search_default_parameters(self):
        """Test that similarity search handles default parameters correctly."""
        with (
            patch("rag_fetch.search_similarity.Chroma") as mock_chroma,
            patch(
                "rag_fetch.search_similarity.GoogleGenerativeAIEmbeddings"
            ) as mock_embeddings,
            patch("rag_fetch.search_similarity.Path.exists") as mock_path_exists,
        ):
            # Mock setup
            mock_path_exists.return_value = True
            mock_embedding_model = Mock()
            mock_embeddings.return_value = mock_embedding_model
            mock_vectorstore = Mock()
            mock_chroma.return_value = mock_vectorstore
            mock_vectorstore.similarity_search_with_relevance_scores.return_value = []

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
        mock_mcp_tool.assert_called_once()
        
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
