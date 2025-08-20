"""
Unit tests for RAG Fetch CLI module.

This test suite covers the CLI interface functionality for the search
service.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rag_fetch.cli import main


class TestRAGFetchCLI(unittest.TestCase):
    """Test cases for RAG Fetch CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        pass  # No cleanup needed for this test

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_fetch.cli.similarity_search_mcp_tool')
    @patch('sys.argv', ['main.py', 'test', 'query'])
    def test_main_with_search_query(self, mock_search, mock_stdout):
        """Test main function with search query."""
        mock_search.return_value = "Mock search results"
        
        main()
        
        # Verify similarity_search_mcp_tool was called
        mock_search.assert_called_once()
        
        # Verify header was printed
        output = mock_stdout.getvalue()
        self.assertIn("🤖 MCP RAG - Retrieval Augmented Generation with MCP", output)
        self.assertIn("=" * 50, output)
        self.assertIn("Searching for: 'test query'", output)
        self.assertIn("Results:", output)
        self.assertIn("Mock search results", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_fetch.cli.similarity_search_mcp_tool')
    @patch('sys.argv', ['main.py', 'test'])
    def test_main_with_single_word_query(self, mock_search, mock_stdout):
        """Test main function with single word query."""
        mock_search.return_value = "Single word results"
        
        main()
        
        # Verify similarity_search_mcp_tool was called
        mock_search.assert_called_once()
        
        # Verify output
        output = mock_stdout.getvalue()
        self.assertIn("Searching for: 'test'", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_fetch.cli.similarity_search_mcp_tool')
    @patch('sys.argv', ['main.py'])
    def test_main_without_arguments(self, mock_search, mock_stdout):
        """Test main function without arguments shows usage."""
        main()
        
        # Verify similarity_search_mcp_tool was NOT called
        mock_search.assert_not_called()
        
        # Verify usage information was printed
        output = mock_stdout.getvalue()
        self.assertIn("🤖 MCP RAG - Retrieval Augmented Generation with MCP", output)
        self.assertIn("Usage:", output)
        self.assertIn("python main.py <search query>", output)
        self.assertIn("python mcp_server.py", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_fetch.cli.similarity_search_mcp_tool')
    @patch('sys.argv', ['main.py', 'failing', 'query'])
    def test_main_with_search_error(self, mock_search, mock_stdout):
        """Test main function with search error."""
        mock_search.side_effect = Exception("Search failed")
        
        main()
        
        # Verify error handling
        output = mock_stdout.getvalue()
        self.assertIn("Error: Search failed", output)
        self.assertIn("GOOGLE_API_KEY", output)
        self.assertIn("Documents stored in ChromaDB", output)


class TestRAGFetchCLIDirectExecution(unittest.TestCase):
    """Test direct execution of CLI module."""

    def test_callable_main_function(self):
        """Test that main function is callable."""
        from rag_fetch.cli import main
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()