"""
Unit tests for store_embeddings module.

This test suite covers the document storage and embedding functionality.
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_store.store_embeddings import (
    ModelVendor, 
    load_embedding_model, 
    process_pdf_files, 
    process_text_files
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
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    @patch('rag_store.store_embeddings.GoogleGenerativeAIEmbeddings')
    def test_load_embedding_model_google(self, mock_google):
        """Test loading Google embedding model."""
        mock_model = Mock()
        mock_google.return_value = mock_model
        
        result = load_embedding_model(ModelVendor.GOOGLE)
        
        mock_google.assert_called_once_with(model="models/text-embedding-004", google_api_key="test_key")
        self.assertEqual(result, mock_model)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('rag_store.store_embeddings.OpenAIEmbeddings')
    def test_load_embedding_model_openai(self, mock_openai):
        """Test loading OpenAI embedding model."""
        mock_model = Mock()
        mock_openai.return_value = mock_model
        
        result = load_embedding_model(ModelVendor.OPENAI)
        
        mock_openai.assert_called_once()
        self.assertEqual(result, mock_model)
    
    @patch('rag_store.store_embeddings.PDFProcessor')
    def test_process_pdf_files_empty_directory(self, mock_processor_class):
        """Test processing PDF files from empty directory."""
        # Create empty directory
        empty_dir = self.temp_dir_path / "empty"
        empty_dir.mkdir()
        
        result = process_pdf_files(empty_dir)
        
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
    
    @patch('rag_store.store_embeddings.PDFProcessor')
    def test_process_pdf_files_with_pdfs(self, mock_processor_class):
        """Test processing PDF files from directory with PDFs."""
        # Create mock PDF files
        pdf1 = self.temp_dir_path / "test1.pdf"
        pdf2 = self.temp_dir_path / "test2.pdf"
        pdf1.touch()
        pdf2.touch()
        
        # Mock processor
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.pdf_to_documents_recursive.return_value = [
            Mock(page_content="Test content", metadata={"source": "test1.pdf"})
        ]
        
        result = process_pdf_files(self.temp_dir_path)
        
        # Should process both PDF files
        self.assertEqual(mock_processor.pdf_to_documents_recursive.call_count, 2)
        self.assertEqual(len(result), 2)  # 2 PDFs × 1 document each
    
    def test_process_text_files_empty_directory(self):
        """Test processing text files from empty directory."""
        # Create empty directory
        empty_dir = self.temp_dir_path / "empty"
        empty_dir.mkdir()
        
        result = process_text_files(empty_dir)
        
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
    
    @patch('rag_store.store_embeddings.load_txt_documents')
    def test_process_text_files_with_texts(self, mock_load_txt):
        """Test processing text files from directory with text files."""
        # Create mock text files
        txt1 = self.temp_dir_path / "test1.txt"
        txt2 = self.temp_dir_path / "test2.txt"
        txt1.touch()
        txt2.touch()
        
        # Mock loader
        mock_load_txt.return_value = [
            Mock(page_content="Test content", metadata={"source": "test.txt"})
        ]
        
        result = process_text_files(self.temp_dir_path)
        
        # Should process both text files
        self.assertEqual(mock_load_txt.call_count, 2)
        self.assertEqual(len(result), 2)  # 2 text files × 1 document each


class TestStoreEmbeddingsIntegration(unittest.TestCase):
    """Integration tests for store_embeddings functionality."""
    
    def test_model_vendor_integration(self):
        """Test that ModelVendor enum works with actual functions."""
        # This test verifies the enum can be used with the functions
        vendors = [ModelVendor.GOOGLE, ModelVendor.OPENAI]
        
        for vendor in vendors:
            self.assertIn(vendor.value, ["google", "openai"])
            self.assertIsInstance(vendor, ModelVendor)


if __name__ == '__main__':
    unittest.main(verbosity=2)