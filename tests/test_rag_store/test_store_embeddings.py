"""
Unit tests for store_embeddings module.

This test suite covers the document storage and embedding functionality.
"""

import os
import shutil

# Import the module to test
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_store.store_embeddings import (
    ModelVendor,
    load_embedding_model,
    process_documents_from_directory,
    process_pdf_files,
    process_text_files,
)


class TestStoreEmbeddings(unittest.TestCase):
    """Test cases for store_embeddings module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_model_vendor_enum(self):
        """Test ModelVendor enum values."""
        self.assertEqual(ModelVendor.OPENAI.value, "openai")
        self.assertEqual(ModelVendor.GOOGLE.value, "google")

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    @patch("rag_store.store_embeddings.GoogleGenerativeAIEmbeddings")
    def test_load_embedding_model_google(self, mock_google):
        """Test loading Google embedding model."""
        mock_model = Mock()
        mock_google.return_value = mock_model

        result = load_embedding_model(ModelVendor.GOOGLE)

        mock_google.assert_called_once_with(
            model="models/text-embedding-004", google_api_key="test_key"
        )
        self.assertEqual(result, mock_model)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("rag_store.store_embeddings.OpenAIEmbeddings")
    def test_load_embedding_model_openai(self, mock_openai):
        """Test loading OpenAI embedding model."""
        mock_model = Mock()
        mock_openai.return_value = mock_model

        result = load_embedding_model(ModelVendor.OPENAI)

        mock_openai.assert_called_once()
        self.assertEqual(result, mock_model)

    def test_process_pdf_files_empty_directory(self):
        """Test processing PDF files from empty directory."""
        # Create empty directory
        empty_dir = self.temp_dir_path / "empty"
        empty_dir.mkdir()

        result = process_pdf_files(empty_dir)

        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)

    @patch("rag_store.store_embeddings.get_document_processor_registry")
    def test_process_pdf_files_with_pdfs(self, mock_registry_func):
        """Test processing PDF files from directory with PDFs."""
        # Create mock PDF files
        pdf1 = self.temp_dir_path / "test1.pdf"
        pdf2 = self.temp_dir_path / "test2.pdf"
        pdf1.touch()
        pdf2.touch()

        # Mock registry and processor
        mock_registry = Mock()
        mock_registry_func.return_value = mock_registry
        mock_registry.process_document.return_value = [
            Mock(page_content="Test content", metadata={"source": "test1.pdf"})
        ]

        result = process_pdf_files(self.temp_dir_path)

        # Should process both PDF files
        self.assertEqual(mock_registry.process_document.call_count, 2)
        self.assertEqual(len(result), 2)  # 2 PDFs × 1 document each

    def test_process_text_files_empty_directory(self):
        """Test processing text files from empty directory."""
        # Create empty directory
        empty_dir = self.temp_dir_path / "empty"
        empty_dir.mkdir()

        result = process_text_files(empty_dir)

        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)

    @patch("rag_store.store_embeddings.get_document_processor_registry")
    def test_process_text_files_with_texts(self, mock_registry_func):
        """Test processing text files from directory with text files."""
        # Create mock text files
        txt1 = self.temp_dir_path / "test1.txt"
        txt2 = self.temp_dir_path / "test2.txt"
        txt1.touch()
        txt2.touch()

        # Mock registry and processor
        mock_registry = Mock()
        mock_registry_func.return_value = mock_registry
        mock_registry.process_document.return_value = [
            Mock(page_content="Test content", metadata={"source": "test.txt"})
        ]

        result = process_text_files(self.temp_dir_path)

        # Should process both text files
        self.assertEqual(mock_registry.process_document.call_count, 2)
        self.assertEqual(len(result), 2)  # 2 text files × 1 document each

    @patch("rag_store.store_embeddings.get_document_processor_registry")
    def test_process_documents_from_directory_unified(self, mock_registry_func):
        """Test the new unified document processing function."""
        # Create mixed file types
        pdf_file = self.temp_dir_path / "test.pdf"
        txt_file = self.temp_dir_path / "test.txt"
        md_file = self.temp_dir_path / "test.md"
        unsupported_file = self.temp_dir_path / "test.xyz"

        pdf_file.touch()
        txt_file.touch()
        md_file.touch()
        unsupported_file.touch()

        # Mock registry
        mock_registry = Mock()
        mock_registry_func.return_value = mock_registry
        mock_registry.get_supported_extensions.return_value = {".pdf", ".txt", ".md"}

        # Mock processor selection
        def mock_get_processor(file_path):
            if file_path.suffix in {".pdf", ".txt", ".md"}:
                return Mock()  # Return a mock processor
            return None

        mock_registry.get_processor_for_file.side_effect = mock_get_processor
        mock_registry.process_document.return_value = [
            Mock(page_content="Test content", metadata={"source": "test.pdf"})
        ]

        result = process_documents_from_directory(self.temp_dir_path)

        # Should process 3 supported files (pdf, txt, md) but not xyz
        self.assertEqual(mock_registry.process_document.call_count, 3)
        self.assertEqual(len(result), 3)  # 3 supported files × 1 document each


class TestStoreEmbeddingsIntegration(unittest.TestCase):
    """Integration tests for store_embeddings functionality."""

    def test_model_vendor_integration(self):
        """Test that ModelVendor enum works with actual functions."""
        # This test verifies the enum can be used with the functions
        vendors = [ModelVendor.GOOGLE, ModelVendor.OPENAI]

        for vendor in vendors:
            self.assertIn(vendor.value, ["google", "openai"])
            self.assertIsInstance(vendor, ModelVendor)


if __name__ == "__main__":
    unittest.main(verbosity=2)
