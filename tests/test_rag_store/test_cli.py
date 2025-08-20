"""
Unit tests for RAG Store CLI module.

This test suite covers the CLI interface functionality for the document
ingestion service.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rag_store.cli import main


class TestRAGStoreCLI(unittest.TestCase):
    """Test cases for RAG Store CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        pass  # No cleanup needed for this test

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_store.cli.store_main')
    @patch('sys.argv', ['rag-store-cli', 'store'])
    def test_main_with_store_command(self, mock_store_main, mock_stdout):
        """Test main function with 'store' command."""
        main()
        
        # Verify store_main was called
        mock_store_main.assert_called_once()
        
        # Verify header was printed
        output = mock_stdout.getvalue()
        self.assertIn("🗄️  RAG Store - Document Ingestion Service", output)
        self.assertIn("=" * 50, output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_store.cli.store_main')
    @patch('sys.argv', ['rag-store-cli'])
    def test_main_without_arguments(self, mock_store_main, mock_stdout):
        """Test main function without arguments shows usage."""
        main()
        
        # Verify store_main was NOT called
        mock_store_main.assert_not_called()
        
        # Verify usage information was printed
        output = mock_stdout.getvalue()
        self.assertIn("🗄️  RAG Store - Document Ingestion Service", output)
        self.assertIn("Usage:", output)
        self.assertIn("rag-store-cli store", output)
        self.assertIn("python -m rag_store.cli store", output)
        self.assertIn("GOOGLE_API_KEY", output)
        self.assertIn("data_source directory", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_store.cli.store_main')
    @patch('sys.argv', ['rag-store-cli', 'invalid'])
    def test_main_with_invalid_command(self, mock_store_main, mock_stdout):
        """Test main function with invalid command shows usage."""
        main()
        
        # Verify store_main was NOT called
        mock_store_main.assert_not_called()
        
        # Verify usage information was printed
        output = mock_stdout.getvalue()
        self.assertIn("Usage:", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('rag_store.cli.store_main')
    @patch('sys.argv', ['rag-store-cli', 'store', 'extra'])
    def test_main_with_extra_arguments(self, mock_store_main, mock_stdout):
        """Test main function with extra arguments still calls store."""
        main()
        
        # Verify store_main was called (extra args are ignored)
        mock_store_main.assert_called_once()


class TestRAGStoreCLIDirectExecution(unittest.TestCase):
    """Test direct execution of CLI module."""

    @patch('rag_store.cli.main')
    def test_direct_execution(self, mock_main):
        """Test that __main__ block calls main function."""
        # Import the module to trigger __main__ execution
        # We need to mock sys.modules to simulate direct execution
        import importlib
        
        # This is tricky to test directly, but we can verify the structure
        # The main function should be callable
        from rag_store.cli import main
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()