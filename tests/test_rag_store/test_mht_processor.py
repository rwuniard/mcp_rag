"""
Unit tests for MHT document processor.

This test suite covers the MHTProcessor class functionality
including document processing, MHT file handling, and error scenarios.
"""

import shutil

# Import the modules to test
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from langchain.schema import Document

from rag_store.mht_processor import MHTProcessor


class TestMHTProcessor(unittest.TestCase):
    """Test cases for MHTProcessor class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = MHTProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_processor_initialization(self):
        """Test MHTProcessor initialization."""
        processor = MHTProcessor()
        self.assertIsInstance(processor, MHTProcessor)
        self.assertEqual(processor.supported_extensions, {".mht", ".mhtml"})
        self.assertEqual(processor.default_chunk_size, 1200)
        self.assertEqual(processor.default_chunk_overlap, 180)
        self.assertEqual(processor.processor_name, "MHTProcessor")

    def test_file_type_description(self):
        """Test file type description."""
        description = self.processor.file_type_description
        self.assertEqual(description, "MHT/MHTML web archive files (.mht, .mhtml)")

    def test_is_supported_file_valid_extensions(self):
        """Test is_supported_file with valid extensions."""
        mht_file = self.temp_dir_path / "test.mht"
        mhtml_file = self.temp_dir_path / "test.mhtml"

        mht_file.touch()
        mhtml_file.touch()

        self.assertTrue(self.processor.is_supported_file(mht_file))
        self.assertTrue(self.processor.is_supported_file(mhtml_file))

    def test_is_supported_file_case_insensitive(self):
        """Test is_supported_file is case insensitive."""
        mht_file = self.temp_dir_path / "test.MHT"
        mhtml_file = self.temp_dir_path / "test.MHTML"

        mht_file.touch()
        mhtml_file.touch()

        self.assertTrue(self.processor.is_supported_file(mht_file))
        self.assertTrue(self.processor.is_supported_file(mhtml_file))

    def test_is_supported_file_invalid_extension(self):
        """Test is_supported_file with invalid extension."""
        pdf_file = self.temp_dir_path / "test.pdf"
        txt_file = self.temp_dir_path / "test.txt"
        
        pdf_file.touch()
        txt_file.touch()
        
        self.assertFalse(self.processor.is_supported_file(pdf_file))
        self.assertFalse(self.processor.is_supported_file(txt_file))

    def test_get_metadata_template(self):
        """Test metadata template generation."""
        mht_file = self.temp_dir_path / "test_document.mht"
        mht_file.write_text("test mht content")

        metadata = self.processor.get_metadata_template(mht_file)

        self.assertEqual(metadata["source"], "test_document.mht")
        self.assertEqual(metadata["file_type"], ".mht")
        self.assertEqual(metadata["processor"], "MHTProcessor")
        self.assertIn("file_path", metadata)
        self.assertIn("file_size", metadata)
        self.assertGreater(metadata["file_size"], 0)

    def test_get_processing_params_default(self):
        """Test get_processing_params with default values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params()
        self.assertEqual(chunk_size, 1200)
        self.assertEqual(chunk_overlap, 180)

    def test_get_processing_params_custom(self):
        """Test get_processing_params with custom values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params(2000, 300)
        self.assertEqual(chunk_size, 2000)
        self.assertEqual(chunk_overlap, 300)

    def test_validate_file_not_found(self):
        """Test validate_file with non-existent file."""
        non_existent_file = self.temp_dir_path / "nonexistent.mht"

        with self.assertRaises(FileNotFoundError):
            self.processor.validate_file(non_existent_file)

    def test_validate_file_unsupported(self):
        """Test validate_file with unsupported file type."""
        pdf_file = self.temp_dir_path / "test.pdf"
        pdf_file.touch()

        with self.assertRaises(ValueError) as context:
            self.processor.validate_file(pdf_file)

        self.assertIn("Unsupported file type", str(context.exception))


class TestMHTProcessorIntegration(unittest.TestCase):
    """Integration tests for MHTProcessor with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MHTProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    @patch("rag_store.mht_processor.UnstructuredLoader")
    @patch("rag_store.mht_processor.RecursiveCharacterTextSplitter")
    @patch("rag_store.mht_processor.log_document_processing_start")
    @patch("rag_store.mht_processor.log_document_processing_complete")
    def test_process_document_success(self, mock_log_complete, mock_log_start, 
                                    mock_splitter_class, mock_loader_class):
        """Test successful document processing."""
        # Create test file
        mht_file = self.temp_dir_path / "test.mht"
        mht_content = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="----=_NextPart_000_0000_01D12345.12345678"

This is a multi-part message in MIME format.

------=_NextPart_000_0000_01D12345.12345678
Content-Type: text/html;
Content-Transfer-Encoding: quoted-printable
Content-Location: http://example.com/

<html>
<head><title>Test Document</title></head>
<body><h1>Test Content</h1><p>This is test HTML content in an MHT file.</p></body>
</html>

------=_NextPart_000_0000_01D12345.12345678--
"""
        mht_file.write_text(mht_content)

        # Mock UnstructuredLoader
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        
        # Create mock documents
        mock_doc = Document(
            page_content="Test Content\n\nThis is test HTML content in an MHT file.",
            metadata={"source": str(mht_file)}
        )
        mock_loader.load.return_value = [mock_doc]

        # Mock text splitter
        mock_splitter = Mock()
        mock_splitter_class.return_value = mock_splitter
        
        # Create mock split documents
        mock_split_doc1 = Document(
            page_content="Test Content",
            metadata={"source": str(mht_file)}
        )
        mock_split_doc2 = Document(
            page_content="This is test HTML content in an MHT file.",
            metadata={"source": str(mht_file)}
        )
        mock_splitter.split_documents.return_value = [mock_split_doc1, mock_split_doc2]

        # Mock logging
        mock_context = {"file_path": str(mht_file), "processor": "MHTProcessor"}
        mock_log_start.return_value = mock_context

        # Process the document
        result = self.processor.process_document(mht_file)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Document)
        self.assertIsInstance(result[1], Document)

        # Verify loader was called correctly
        mock_loader_class.assert_called_once()
        call_args = mock_loader_class.call_args
        self.assertEqual(call_args[1]["file_path"], str(mht_file))
        self.assertEqual(call_args[1]["mode"], "elements")
        self.assertEqual(call_args[1]["strategy"], "fast")

        # Verify text splitter was called
        mock_splitter_class.assert_called_once()
        splitter_args = mock_splitter_class.call_args[1]
        self.assertEqual(splitter_args["chunk_size"], 1200)
        self.assertEqual(splitter_args["chunk_overlap"], 180)
        
        # Verify metadata enhancement
        for i, doc in enumerate(result):
            self.assertIn("chunk_id", doc.metadata)
            self.assertIn("document_id", doc.metadata)
            self.assertIn("chunk_size", doc.metadata)
            self.assertIn("chunk_overlap", doc.metadata)
            self.assertIn("splitting_method", doc.metadata)
            self.assertIn("source_format", doc.metadata)
            self.assertIn("extraction_method", doc.metadata)
            self.assertEqual(doc.metadata["chunk_size"], 1200)
            self.assertEqual(doc.metadata["chunk_overlap"], 180)
            self.assertEqual(doc.metadata["source_format"], "mht/mhtml")
            self.assertEqual(doc.metadata["extraction_method"], "unstructured_elements")

        # Verify logging calls
        mock_log_start.assert_called_once()
        mock_log_complete.assert_called_once()

    @patch("rag_store.mht_processor.UnstructuredLoader")
    @patch("rag_store.mht_processor.log_document_processing_start")
    @patch("rag_store.mht_processor.log_document_processing_complete")
    def test_process_document_empty_result(self, mock_log_complete, mock_log_start, mock_loader_class):
        """Test processing document that returns empty result."""
        # Create test file
        mht_file = self.temp_dir_path / "empty.mht"
        mht_file.write_text("Empty MHT file")

        # Mock UnstructuredLoader to return empty list
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load.return_value = []

        # Mock logging
        mock_context = {"file_path": str(mht_file), "processor": "MHTProcessor"}
        mock_log_start.return_value = mock_context

        # Process the document
        result = self.processor.process_document(mht_file)

        # Assertions
        self.assertEqual(len(result), 0)

        # Verify logging
        mock_log_complete.assert_called_once()
        complete_call_args = mock_log_complete.call_args[1]
        self.assertEqual(complete_call_args["chunks_created"], 0)
        self.assertEqual(complete_call_args["status"], "success_empty")

    @patch("rag_store.mht_processor.UnstructuredLoader")
    @patch("rag_store.mht_processor.log_document_processing_start")
    @patch("rag_store.mht_processor.log_document_processing_complete")
    def test_process_document_processing_error_with_fallback(self, mock_log_complete, mock_log_start, mock_loader_class):
        """Test document processing with loader error but successful fallback."""
        # Create test file with valid MHT content
        mht_file = self.temp_dir_path / "error.mht"
        mht_content = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="----=_NextPart_000_0000_01D12345.12345678"

------=_NextPart_000_0000_01D12345.12345678
Content-Type: text/html;

<html><head><title>Test</title></head><body><h1>Test Content</h1></body></html>

------=_NextPart_000_0000_01D12345.12345678--"""
        mht_file.write_text(mht_content)

        # Mock UnstructuredLoader to raise exception (triggering fallback)
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load.side_effect = Exception("UnstructuredLoader error")

        # Mock logging
        mock_context = {"file_path": str(mht_file), "processor": "MHTProcessor"}
        mock_log_start.return_value = mock_context

        # Process the document - should succeed via fallback
        documents = self.processor.process_document(mht_file)

        # Should succeed with fallback parser
        self.assertGreater(len(documents), 0)
        self.assertEqual(documents[0].metadata.get("extraction_method"), "manual_mht_parser")

        # Verify logging
        mock_log_complete.assert_called_once()

    def test_process_document_custom_params(self):
        """Test process_document with custom parameters."""
        mht_file = self.temp_dir_path / "test.mht"
        mht_file.write_text("Test MHT content")

        with patch("rag_store.mht_processor.UnstructuredLoader") as mock_loader_class, \
             patch("rag_store.mht_processor.RecursiveCharacterTextSplitter") as mock_splitter_class:
            
            # Mock setup
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load.return_value = [Document(page_content="Test", metadata={})]
            
            mock_splitter = Mock()
            mock_splitter_class.return_value = mock_splitter
            mock_splitter.split_documents.return_value = [Document(page_content="Test", metadata={})]

            # Call with custom parameters
            self.processor.process_document(mht_file, chunk_size=2000, chunk_overlap=300)

            # Verify splitter was called with custom parameters
            splitter_args = mock_splitter_class.call_args[1]
            self.assertEqual(splitter_args["chunk_size"], 2000)
            self.assertEqual(splitter_args["chunk_overlap"], 300)

    def test_process_mht_file_legacy_method(self):
        """Test legacy process_mht_file method."""
        mht_file = self.temp_dir_path / "test.mht"
        mht_file.write_text("Test MHT content")

        with patch.object(self.processor, 'process_document') as mock_process:
            mock_process.return_value = [Document(page_content="Test", metadata={})]
            
            result = self.processor.process_mht_file(mht_file)
            
            # Verify it calls process_document
            mock_process.assert_called_once_with(mht_file)
            self.assertEqual(len(result), 1)


class TestMHTProcessorErrorHandling(unittest.TestCase):
    """Test error handling scenarios for MHTProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MHTProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_process_nonexistent_file(self):
        """Test processing non-existent file."""
        nonexistent_file = self.temp_dir_path / "nonexistent.mht"

        with self.assertRaises(FileNotFoundError):
            self.processor.process_document(nonexistent_file)

    def test_process_invalid_file_type(self):
        """Test processing file with invalid extension."""
        txt_file = self.temp_dir_path / "test.txt"
        txt_file.write_text("Not an MHT file")

        with self.assertRaises(ValueError) as context:
            self.processor.process_document(txt_file)

        self.assertIn("Unsupported file type", str(context.exception))

    @patch("rag_store.mht_processor.UnstructuredLoader")
    def test_process_loader_initialization_error_with_fallback(self, mock_loader_class):
        """Test error during UnstructuredLoader initialization with successful fallback."""
        mht_file = self.temp_dir_path / "test.mht"
        # Create valid MHT content that can be parsed by fallback
        mht_content = """MIME-Version: 1.0
Content-Type: multipart/related; boundary="----=_NextPart_000_0000_01D12345.12345678"

------=_NextPart_000_0000_01D12345.12345678
Content-Type: text/html;

<html><head><title>Test</title></head><body><h1>Test Content</h1></body></html>

------=_NextPart_000_0000_01D12345.12345678--"""
        mht_file.write_text(mht_content)

        # Mock loader class to raise exception during initialization
        mock_loader_class.side_effect = Exception("Loader initialization failed")

        # Should succeed with fallback parser instead of raising exception
        documents = self.processor.process_document(mht_file)
        
        # Verify it used the fallback parser
        self.assertGreater(len(documents), 0)
        self.assertEqual(documents[0].metadata.get("extraction_method"), "manual_mht_parser")

    def test_process_both_loaders_fail(self):
        """Test when both UnstructuredLoader and manual parser fail."""
        mht_file = self.temp_dir_path / "invalid.mht"
        # Create invalid content that will fail both parsers
        mht_file.write_text("Invalid content that cannot be parsed")

        with patch("rag_store.mht_processor.UnstructuredLoader") as mock_loader_class, \
             patch.object(self.processor, '_parse_mht_manually') as mock_manual_parser:
            
            # Mock UnstructuredLoader to fail
            mock_loader_class.side_effect = Exception("Loader failed")
            
            # Mock manual parser to fail
            mock_manual_parser.side_effect = Exception("Manual parser failed")
            
            # This should now raise an exception since both parsers fail
            with self.assertRaises(Exception) as context:
                self.processor.process_document(mht_file)

            self.assertIn("Error processing MHT file", str(context.exception))
            self.assertIn("Manual parser failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()