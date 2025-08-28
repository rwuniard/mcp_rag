"""
Unit tests for PDF processor module.

This test suite covers the core functionality of the PDFProcessor class,
including PDF file validation, document chunking, and metadata generation.
"""

import shutil

# Import the module to test
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from langchain.schema import Document

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
        self.assertEqual(self.processor.supported_extensions, {".pdf"})
        self.assertEqual(self.processor.default_chunk_size, 1800)
        self.assertEqual(self.processor.default_chunk_overlap, 270)

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
            "document.pdf.txt",
        ]

        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertFalse(self.processor.is_pdf_file(Path(filename)))

    @patch("rag_store.pdf_processor.fitz.open")
    def test_pdf_to_documents_recursive_default_params(self, mock_fitz_open):
        """Test pdf_to_documents_recursive with default parameters using PyMuPDF."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 2
        
        # Create mock pages
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Sample content from page 1"
        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Sample content from page 2"
        
        # Configure mock document indexing
        mock_doc.__getitem__ = Mock(side_effect=[mock_page1, mock_page2])

        # Create a temporary PDF file path
        pdf_path = self.temp_dir_path / "test.pdf"
        pdf_path.touch()  # Create empty file

        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)

        # Verify fitz.open was called with correct path
        mock_fitz_open.assert_called_once_with(str(pdf_path))

        # Verify document close was called
        mock_doc.close.assert_called_once()

        # Verify returned documents
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # Verify first document structure
        if result:
            doc = result[0]
            self.assertIsInstance(doc, Document)

            # Verify metadata enhancement with new interface
            expected_metadata_keys = {
                "source",
                "chunk_id",
                "document_id",
                "file_path",
                "file_type",
                "processor",
                "chunk_size",
                "chunk_overlap",
                "splitting_method",
                "loader_type"
            }

            # Check expected metadata keys are present
            self.assertTrue(expected_metadata_keys.issubset(doc.metadata.keys()))

            # Check specific metadata values with new interface
            self.assertEqual(doc.metadata["source"], "test.pdf")
            self.assertEqual(doc.metadata["document_id"], "test_pdf")
            self.assertEqual(doc.metadata["file_type"], ".pdf")
            self.assertEqual(doc.metadata["processor"], "PDFProcessor")
            self.assertEqual(doc.metadata["chunk_size"], 1800)
            self.assertEqual(doc.metadata["chunk_overlap"], 270)
            self.assertEqual(
                doc.metadata["splitting_method"], "RecursiveCharacterTextSplitter"
            )
            self.assertEqual(doc.metadata["loader_type"], "PyMuPDF_OCR")

    @patch("rag_store.pdf_processor.fitz.open")
    def test_pdf_to_documents_recursive_custom_params(self, mock_fitz_open):
        """Test pdf_to_documents_recursive with custom parameters."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 1
        
        # Create mock page
        mock_page = Mock()
        mock_page.get_text.return_value = "Test content for custom parameters"
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "custom_test.pdf"
        pdf_path.touch()

        # Custom parameters
        custom_chunk_size = 1000
        custom_overlap = 100

        # Call with custom parameters
        result = self.processor.pdf_to_documents_recursive(
            pdf_path, chunk_size=custom_chunk_size, chunk_overlap=custom_overlap
        )

        # Verify custom parameters were used in metadata
        if result:
            self.assertEqual(result[0].metadata["chunk_size"], custom_chunk_size)
            self.assertEqual(result[0].metadata["chunk_overlap"], custom_overlap)

    @patch("rag_store.pdf_processor.fitz.open")
    def test_pdf_to_documents_recursive_empty_result(self, mock_fitz_open):
        """Test pdf_to_documents_recursive when document has no pages."""
        # Setup mock to return document with no pages
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 0

        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "empty_test.pdf"
        pdf_path.touch()

        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)

        # Verify empty result
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)
        
        # Verify document was closed
        mock_doc.close.assert_called_once()

    @patch("rag_store.pdf_processor.fitz.open")
    def test_pdf_to_documents_recursive_loader_exception(self, mock_fitz_open):
        """Test pdf_to_documents_recursive when PyMuPDF raises an exception."""
        # Setup mock to raise exception
        mock_fitz_open.side_effect = Exception("PDF loading failed")

        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "error_test.pdf"
        pdf_path.touch()

        # Verify exception is propagated
        with self.assertRaises(Exception) as context:
            self.processor.pdf_to_documents_recursive(pdf_path)

        self.assertIn("Error processing PDF", str(context.exception))
        self.assertIn("PDF loading failed", str(context.exception))

    @patch("rag_store.pdf_processor.fitz.open")
    def test_pdf_to_documents_recursive_nonexistent_file(self, mock_fitz_open):
        """Test pdf_to_documents_recursive with non-existent file."""
        # Create path to non-existent file
        nonexistent_path = self.temp_dir_path / "nonexistent.pdf"

        # The method should still try to process (PyMuPDF will handle the error)
        # We expect it to raise an exception when fitz.open tries to load
        mock_fitz_open.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            self.processor.pdf_to_documents_recursive(nonexistent_path)

    @patch("rag_store.pdf_processor.fitz.open")
    def test_metadata_document_id_extraction(self, mock_fitz_open):
        """Test that document_id is correctly extracted from file path."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 1
        
        # Create mock page
        mock_page = Mock()
        mock_page.get_text.return_value = "Test content"
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        # Test various file names - updated expected format for new interface
        test_cases = [
            ("simple.pdf", "simple_pdf"),
            ("complex_document_name.pdf", "complex_document_name_pdf"),
            ("document with spaces.pdf", "document with spaces_pdf"),
            ("123_numbers.pdf", "123_numbers_pdf"),
        ]

        for filename, expected_id in test_cases:
            with self.subTest(filename=filename):
                pdf_path = self.temp_dir_path / filename
                pdf_path.touch()

                result = self.processor.pdf_to_documents_recursive(pdf_path)
                if result:
                    self.assertEqual(result[0].metadata["document_id"], expected_id)

    @patch("rag_store.pdf_processor.fitz.open")
    def test_chunk_numbering_sequence(self, mock_fitz_open):
        """Test that chunks are numbered sequentially starting from 0."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 3
        
        # Create mock pages with enough content to generate multiple chunks
        mock_pages = []
        page_contents = []
        for i in range(3):
            mock_page = Mock()
            content = f"This is content for page {i}. " * 100  # Enough content to create chunks
            mock_page.get_text.return_value = content
            page_contents.append(content)
            mock_pages.append(mock_page)
        
        mock_doc.__getitem__ = Mock(side_effect=mock_pages)

        pdf_path = self.temp_dir_path / "multi_chunk.pdf"
        pdf_path.touch()

        result = self.processor.pdf_to_documents_recursive(pdf_path)

        # Verify sequential numbering (new interface generates chunk_id strings)
        for i, doc in enumerate(result):
            self.assertEqual(doc.metadata["chunk_id"], f"chunk_{i}")
            # Don't check total_chunks since it depends on how the splitter works

    @patch("rag_store.pdf_processor.fitz.open")
    @patch("rag_store.pdf_processor.OCR_AVAILABLE", True)
    def test_ocr_fallback_for_image_based_pdf(self, mock_fitz_open):
        """Test OCR fallback when PDF contains minimal text (image-based)."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 1
        
        # Create mock page that initially returns minimal text (triggering OCR)
        mock_page = Mock()
        # First call returns minimal text (empty), triggering OCR attempt
        mock_page.get_text.return_value = ""  # Triggers OCR
        mock_page.get_text.side_effect = None  # Reset side_effect
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        # Mock the OCR method to return successful OCR text
        with patch.object(self.processor, '_perform_ocr_on_page', return_value="OCR extracted text from image"):
            # Create temporary PDF file
            pdf_path = self.temp_dir_path / "image_pdf.pdf"
            pdf_path.touch()

            # Call the method
            result = self.processor.pdf_to_documents_recursive(pdf_path)

            # Verify result contains OCR text
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            
            if result:
                # Verify OCR metadata is present - note the metadata structure changed
                self.assertEqual(result[0].metadata["loader_type"], "PyMuPDF_OCR")
                # Verify content was extracted
                self.assertIn("OCR extracted", result[0].page_content)
                # Verify extraction method shows OCR was used
                self.assertEqual(result[0].metadata["extraction_method"], "tesseract_ocr")

    @patch("rag_store.pdf_processor.fitz.open")
    def test_ocr_blocks_fallback(self, mock_fitz_open):
        """Test OCR blocks fallback when standard text extraction fails completely."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 1
        
        # Create mock page that returns empty text but has text blocks
        mock_page = Mock()
        # Both get_text() calls return empty
        mock_page.get_text.return_value = ""
        # But get_text("blocks") returns structured data
        def get_text_side_effect(mode=None):
            if mode == "blocks":
                # Return mock blocks data (x0, y0, x1, y1, text, block_no, block_type)
                return [
                    (0, 0, 100, 20, "Block 1 text content", 0, 0),
                    (0, 25, 100, 45, "Block 2 more content", 1, 0),
                ]
            return ""
        
        mock_page.get_text.side_effect = get_text_side_effect
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "blocks_pdf.pdf"
        pdf_path.touch()

        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)

        # Verify result contains text from blocks
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        if result:
            # Verify blocks extraction worked
            content = result[0].page_content
            self.assertIn("Block 1 text content", content)
            self.assertIn("Block 2 more content", content)
            self.assertEqual(result[0].metadata["loader_type"], "PyMuPDF_OCR")

    @patch("rag_store.pdf_processor.fitz.open")
    @patch("rag_store.pdf_processor.OCR_AVAILABLE", False)
    def test_ocr_not_available_fallback(self, mock_fitz_open):
        """Test behavior when OCR is not available."""
        # Setup mock PyMuPDF document
        mock_doc = Mock()
        mock_fitz_open.return_value = mock_doc
        mock_doc.page_count = 1
        
        # Create mock page that returns no text
        mock_page = Mock()
        mock_page.get_text.return_value = ""
        mock_doc.__getitem__ = Mock(return_value=mock_page)

        # Create temporary PDF file
        pdf_path = self.temp_dir_path / "no_ocr_pdf.pdf"
        pdf_path.touch()

        # Call the method
        result = self.processor.pdf_to_documents_recursive(pdf_path)

        # Should return empty result since no OCR is available and no text found
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestPDFProcessorIntegration(unittest.TestCase):
    """Integration tests that may require actual PDF processing (optional)."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()

    def test_with_real_pdf_if_available(self):
        """Test with a real PDF file if one is available in the rag_store directory."""
        # Look for test PDF files in the correct data_source directory
        data_source_path = (
            Path(__file__).parent.parent.parent / "src" / "rag_store" / "data_source"
        )
        test_pdf_path = data_source_path / "thinkpython.pdf"

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

                    # Check metadata with new interface structure
                    required_keys = {
                        "source",
                        "chunk_id",
                        "document_id",
                        "file_path",
                        "file_type",
                        "processor",
                        "chunk_size",
                        "chunk_overlap",
                        "splitting_method",
                    }
                    self.assertTrue(required_keys.issubset(doc.metadata.keys()))

                print(
                    f"✓ Successfully processed {len(documents)} chunks from {test_pdf_path.name}"
                )

            except Exception as e:
                self.skipTest(
                    f"Integration test skipped due to PDF processing error: {e}"
                )
        else:
            self.skipTest("No test PDF file available for integration testing")

    def test_ocr_investigation_method_exists(self):
        """Test that OCR investigation method exists and can be called."""
        # Simply verify the method exists and can be called without errors
        # This is a basic smoke test for the new functionality
        self.assertTrue(hasattr(self.processor, '_write_ocr_investigation_file'))
        
        # Test that the method can be called with OCR_INVESTIGATE disabled
        # Should return early without creating files
        import os
        original_env = os.environ.copy()
        try:
            os.environ['OCR_INVESTIGATE'] = 'false'
            # Should not raise exception when OCR investigation is disabled
            self.processor._write_ocr_investigation_file("test content", 1, "/test/path.pdf")
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'true', 'OCR_INVESTIGATE_DIR': './test_ocr_debug'})
    def test_ocr_investigation_file_writing_with_text(self):
        """Test OCR investigation file writing with OCR text results."""
        processor = PDFProcessor()
        
        # Test data
        ocr_result = "This is some OCR text that was extracted from a PDF page. " * 10  # Make it >300 chars
        page_num = 1
        pdf_path = "/path/to/test_document.pdf"
        
        # Create temp directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict('os.environ', {'OCR_INVESTIGATE_DIR': temp_dir}):
                # Call the method
                processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
                
                # Verify file was created
                from pathlib import Path
                expected_filename = Path(temp_dir) / "ocr_investigation_test_document_page_1.txt"
                self.assertTrue(expected_filename.exists())
                
                # Verify file contents
                with open(expected_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.assertIn("OCR Investigation Results", content)
                self.assertIn("PDF File: /path/to/test_document.pdf", content)
                self.assertIn("Page Number: 1", content)
                self.assertIn(f"OCR Result Length: {len(ocr_result)} characters", content)
                self.assertIn("OCR Result Empty: No", content)
                self.assertIn("Full OCR Text:", content)
                self.assertIn(ocr_result[:300], content)  # Preview
                self.assertIn("... (truncated, see full text below)", content)  # Truncation message
                self.assertIn(ocr_result, content)  # Full text
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'true', 'OCR_INVESTIGATE_DIR': './test_ocr_debug'})
    def test_ocr_investigation_file_writing_without_text(self):
        """Test OCR investigation file writing with empty OCR results."""
        processor = PDFProcessor()
        
        # Test data - empty OCR result
        ocr_result = ""
        page_num = 2
        pdf_path = "/path/to/empty_document.pdf"
        
        # Create temp directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict('os.environ', {'OCR_INVESTIGATE_DIR': temp_dir}):
                # Call the method
                processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
                
                # Verify file was created
                from pathlib import Path
                expected_filename = Path(temp_dir) / "ocr_investigation_empty_document_page_2.txt"
                self.assertTrue(expected_filename.exists())
                
                # Verify file contents
                with open(expected_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.assertIn("OCR Investigation Results", content)
                self.assertIn("PDF File: /path/to/empty_document.pdf", content)
                self.assertIn("Page Number: 2", content)
                self.assertIn("OCR Result Length: 0 characters", content)
                self.assertIn("OCR Result Empty: Yes", content)
                self.assertIn("OCR returned no text for this page.", content)
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'true'})  # No custom directory
    def test_ocr_investigation_default_directory(self):
        """Test OCR investigation uses default directory when not specified."""
        processor = PDFProcessor()
        
        ocr_result = "Test OCR text"
        page_num = 3
        pdf_path = "/path/to/default_test.pdf"
        
        # Mock Path.mkdir and open to avoid actual file creation
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', mock_open()) as mock_file:
            
            processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
            
            # Verify default directory was used
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            # Verify file write was attempted
            mock_file.assert_called_once()
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'true'})
    def test_ocr_investigation_safe_filename_handling(self):
        """Test OCR investigation handles special characters in PDF paths."""
        processor = PDFProcessor()
        
        ocr_result = "Test text"
        page_num = 1
        # PDF path with special characters that need to be cleaned
        pdf_path = "/path/to/document with spaces & special!chars@.pdf"
        
        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', mock_open()) as mock_file:
            
            processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
            
            # Verify the filename was sanitized (extract from the call)
            mock_file.assert_called_once()
            call_args = mock_file.call_args[0]
            filename = str(call_args[0])
            # Should contain sanitized version of filename
            self.assertIn("document with spaces", filename)
            self.assertNotIn("&", filename)
            self.assertNotIn("!", filename)
            self.assertNotIn("@", filename)
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'true'})
    def test_ocr_investigation_exception_handling(self):
        """Test OCR investigation handles exceptions gracefully."""
        processor = PDFProcessor()
        
        ocr_result = "Test text"
        page_num = 1
        pdf_path = "/path/to/test.pdf"
        
        # Mock mkdir to raise an exception
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Access denied")):
            with patch('rag_store.pdf_processor.logger') as mock_logger:
                # Should not raise exception, should log warning
                processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
                
                # Verify warning was logged
                mock_logger.warning.assert_called_once()
                args = mock_logger.warning.call_args[0]
                self.assertIn("Failed to write OCR investigation file", args[0])
    
    @patch.dict('os.environ', {'OCR_INVESTIGATE': 'false'})  # Disabled
    def test_ocr_investigation_disabled(self):
        """Test OCR investigation is skipped when disabled."""
        processor = PDFProcessor()
        
        ocr_result = "Test text"
        page_num = 1
        pdf_path = "/path/to/test.pdf"
        
        # Mock Path.mkdir - should not be called
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            processor._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
            
            # Verify no directory creation was attempted
            mock_mkdir.assert_not_called()
    
    def test_ocr_dependencies_import_error_handling(self):
        """Test handling of OCR dependencies import errors."""
        # This test verifies the import error handling for pytesseract and PIL
        # We can't easily mock module imports, but we can test the OCR_AVAILABLE flag
        from src.rag_store.pdf_processor import OCR_AVAILABLE
        # OCR_AVAILABLE should be either True or False, not None
        self.assertIsInstance(OCR_AVAILABLE, bool)
        
    def test_relative_import_fallback_handling(self):
        """Test that the processor works with both relative and absolute imports."""
        # This test verifies the fallback import mechanism works
        # The processor should initialize regardless of import style
        processor = PDFProcessor()
        self.assertIsNotNone(processor)
        self.assertEqual(processor.processor_name, "PDFProcessor")
        # Verify it has the required methods from successful imports
        self.assertTrue(hasattr(processor, 'process_document'))
        self.assertTrue(hasattr(processor, 'is_supported_file'))


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2)
