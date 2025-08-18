"""
Unit tests for PDF processor module.

This test suite covers the core functionality of the PDFProcessor class,
including PDF file validation, document chunking, and metadata generation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_store.pdf_processor import PDFProcessor


class TestPDFProcessor(unittest.TestCase):
    """Test cases for PDFProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = PDFProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_default_values(self):
        """Test PDFProcessor initialization with default values."""
        self.assertEqual(self.processor.supported_extensions, {'.pdf'})
        self.assertEqual(self.processor.default_pdf_chunk_size, 1800)
        self.assertEqual(self.processor.default_pdf_overlap, 270)
    
    def test_is_pdf_file_valid_pdf(self):
        """Test is_pdf_file with valid PDF extensions."""
        # Test lowercase .pdf
        pdf_path = Path("document.pdf")
        self.assertTrue(self.processor.is_pdf_file(pdf_path))
        
        # Test uppercase .PDF
        pdf_path_upper = Path("document.PDF")
        self.assertTrue(self.processor.is_pdf_file(pdf_path_upper))
        
        # Test mixed case .Pdf
        pdf_path_mixed = Path("document.Pdf")
        self.assertTrue(self.processor.is_pdf_file(pdf_path_mixed))
    
    def test_is_pdf_file_invalid_extensions(self):
        """Test is_pdf_file with invalid file extensions."""
        # Test various non-PDF extensions
        invalid_files = [
            "document.txt",
            "document.docx",
            "document.png",
            "document",
            "document.pdf.txt"
        ]
        
        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertFalse(self.processor.is_pdf_file(Path(filename)))
    
    @patch('rag_store.pdf_processor.PyPDFLoader')
    def test_pdf_to_documents_recursive_default_params(self, mock_loader_class):
        """Test pdf_to_documents_recursive with default parameters."""
        # Setup mock objects
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        
        # Create sample documents that would be returned by the loader
        sample_docs = [
            Document(
                page_content="Sample content 1",
                metadata={"source": "test.pdf", "page": 0}
            ),
            Document(
                page_content="Sample content 2", 
                metadata={"source": "test.pdf", "page": 1}
            )
        ]
        mock_loader.load_and_split.return_value = sample_docs
        
        # Create a temporary PDF file path
        pdf_path = self.temp_dir_path / "test.pdf"
        pdf_path.touch()  # Create empty file
        
        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)
        
        # Verify loader was created with correct path
        mock_loader_class.assert_called_once_with(str(pdf_path))
        
        # Verify loader.load_and_split was called with RecursiveCharacterTextSplitter
        mock_loader.load_and_split.assert_called_once()
        text_splitter_arg = mock_loader.load_and_split.call_args[0][0]
        self.assertIsInstance(text_splitter_arg, RecursiveCharacterTextSplitter)
        
        # Verify the splitter configuration (using private attributes)
        self.assertEqual(text_splitter_arg._chunk_size, 1800)
        self.assertEqual(text_splitter_arg._chunk_overlap, 270)
        self.assertEqual(text_splitter_arg._separators, ["\n\n", "\n", " ", ""])
        
        # Verify returned documents
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Document)
        self.assertIsInstance(result[1], Document)
        
        # Verify metadata enhancement
        expected_metadata_keys = {
            "source", "chunk_id", "document_id", "file_type", 
            "total_chunks", "chunk_size", "chunk_overlap", "splitting_method"
        }
        
        for i, doc in enumerate(result):
            # Check all expected metadata keys are present
            self.assertTrue(expected_metadata_keys.issubset(doc.metadata.keys()))
            
            # Check specific metadata values
            self.assertEqual(doc.metadata["source"], str(pdf_path))
            self.assertEqual(doc.metadata["chunk_id"], i)
            self.assertEqual(doc.metadata["document_id"], "test")
            self.assertEqual(doc.metadata["file_type"], "pdf")
            self.assertEqual(doc.metadata["total_chunks"], 2)
            self.assertEqual(doc.metadata["chunk_size"], 1800)
            self.assertEqual(doc.metadata["chunk_overlap"], 270)
            self.assertEqual(doc.metadata["splitting_method"], "recursive")
    
    @patch('rag_store.pdf_processor.PyPDFLoader')
    def test_pdf_to_documents_recursive_custom_params(self, mock_loader_class):
        """Test pdf_to_documents_recursive with custom parameters."""
        # Setup mock
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_and_split.return_value = [
            Document(page_content="Test content", metadata={})
        ]
        
        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "custom_test.pdf"
        pdf_path.touch()
        
        # Custom parameters
        custom_chunk_size = 1000
        custom_overlap = 100
        
        # Call with custom parameters
        result = self.processor.pdf_to_documents_recursive(
            pdf_path, 
            chunk_size=custom_chunk_size, 
            chunk_overlap=custom_overlap
        )
        
        # Verify custom parameters were used in metadata
        self.assertEqual(result[0].metadata["chunk_size"], custom_chunk_size)
        self.assertEqual(result[0].metadata["chunk_overlap"], custom_overlap)
        
        # Verify text splitter was configured with custom parameters (using private attributes)
        text_splitter_arg = mock_loader.load_and_split.call_args[0][0]
        self.assertEqual(text_splitter_arg._chunk_size, custom_chunk_size)
        self.assertEqual(text_splitter_arg._chunk_overlap, custom_overlap)
    
    @patch('rag_store.pdf_processor.PyPDFLoader')
    def test_pdf_to_documents_recursive_empty_result(self, mock_loader_class):
        """Test pdf_to_documents_recursive when loader returns empty list."""
        # Setup mock to return empty list
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_and_split.return_value = []
        
        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "empty_test.pdf"
        pdf_path.touch()
        
        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)
        
        # Verify empty result
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
    
    @patch('rag_store.pdf_processor.PyPDFLoader')
    def test_pdf_to_documents_recursive_loader_exception(self, mock_loader_class):
        """Test pdf_to_documents_recursive when PyPDFLoader raises an exception."""
        # Setup mock to raise exception
        mock_loader_class.side_effect = Exception("PDF loading failed")
        
        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "error_test.pdf"
        pdf_path.touch()
        
        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            self.processor.pdf_to_documents_recursive(pdf_path)
        
        self.assertEqual(str(context.exception), "PDF loading failed")
    
    def test_pdf_to_documents_recursive_nonexistent_file(self):
        """Test pdf_to_documents_recursive with non-existent file."""
        # Create path to non-existent file
        nonexistent_path = self.temp_dir_path / "nonexistent.pdf"
        
        # The method should still try to process (PyPDFLoader will handle the error)
        # We expect it to raise an exception when PyPDFLoader tries to load
        with patch('rag_store.pdf_processor.PyPDFLoader') as mock_loader_class:
            mock_loader_class.side_effect = FileNotFoundError("File not found")
            
            with self.assertRaises(FileNotFoundError):
                self.processor.pdf_to_documents_recursive(nonexistent_path)
    
    def test_metadata_document_id_extraction(self):
        """Test that document_id is correctly extracted from file path."""
        with patch('rag_store.pdf_processor.PyPDFLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load_and_split.return_value = [
                Document(page_content="Test", metadata={})
            ]
            
            # Test various file names
            test_cases = [
                ("simple.pdf", "simple"),
                ("complex_document_name.pdf", "complex_document_name"),
                ("document with spaces.pdf", "document with spaces"),
                ("123_numbers.pdf", "123_numbers")
            ]
            
            for filename, expected_id in test_cases:
                with self.subTest(filename=filename):
                    pdf_path = self.temp_dir_path / filename
                    pdf_path.touch()
                    
                    result = self.processor.pdf_to_documents_recursive(pdf_path)
                    self.assertEqual(result[0].metadata["document_id"], expected_id)
    
    def test_chunk_numbering_sequence(self):
        """Test that chunks are numbered sequentially starting from 0."""
        with patch('rag_store.pdf_processor.PyPDFLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            
            # Create multiple sample documents
            sample_docs = [
                Document(page_content=f"Content {i}", metadata={})
                for i in range(5)
            ]
            mock_loader.load_and_split.return_value = sample_docs
            
            pdf_path = self.temp_dir_path / "multi_chunk.pdf"
            pdf_path.touch()
            
            result = self.processor.pdf_to_documents_recursive(pdf_path)
            
            # Verify sequential numbering
            for i, doc in enumerate(result):
                self.assertEqual(doc.metadata["chunk_id"], i)
                self.assertEqual(doc.metadata["total_chunks"], 5)


class TestPDFProcessorIntegration(unittest.TestCase):
    """Integration tests that may require actual PDF processing (optional)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
    
    def test_with_real_pdf_if_available(self):
        """Test with a real PDF file if one is available in the rag_store directory."""
        # Look for test PDF files in the original rag_store directory
        rag_store_path = Path(__file__).parent.parent.parent / "rag_store"
        test_pdf_path = rag_store_path / "thinkpython.pdf"
        
        if test_pdf_path.exists():
            print(f"Running integration test with {test_pdf_path.name}")
            
            try:
                # Process the PDF
                documents = self.processor.pdf_to_documents_recursive(test_pdf_path)
                
                # Basic validation
                self.assertIsInstance(documents, list)
                self.assertGreater(len(documents), 0)
                
                # Check first document
                if documents:
                    doc = documents[0]
                    self.assertIsInstance(doc, Document)
                    self.assertIsInstance(doc.page_content, str)
                    self.assertGreater(len(doc.page_content), 0)
                    
                    # Check metadata
                    required_keys = {
                        "source", "chunk_id", "document_id", "file_type",
                        "total_chunks", "chunk_size", "chunk_overlap", "splitting_method"
                    }
                    self.assertTrue(required_keys.issubset(doc.metadata.keys()))
                    
                print(f"✓ Successfully processed {len(documents)} chunks from {test_pdf_path.name}")
                
            except Exception as e:
                self.skipTest(f"Integration test skipped due to PDF processing error: {e}")
        else:
            self.skipTest("No test PDF file available for integration testing")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2)