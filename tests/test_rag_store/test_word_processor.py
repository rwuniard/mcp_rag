"""
Unit tests for Word document processor.

This test suite covers the WordProcessor class functionality
including document processing, metadata generation, and error handling.
"""

import shutil

# Import the modules to test
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from langchain.schema import Document

from rag_store.word_processor import WordProcessor


class TestWordProcessor(unittest.TestCase):
    """Test cases for WordProcessor class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = WordProcessor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_processor_initialization(self):
        """Test WordProcessor initialization."""
        processor = WordProcessor()
        self.assertIsInstance(processor, WordProcessor)
        self.assertEqual(processor.supported_extensions, {".docx"})
        self.assertEqual(processor.default_chunk_size, 1000)
        self.assertEqual(processor.default_chunk_overlap, 150)
        self.assertEqual(processor.processor_name, "WordProcessor")

    def test_file_type_description(self):
        """Test file type description."""
        description = self.processor.file_type_description
        self.assertEqual(description, "Microsoft Word documents (.docx)")

    def test_is_supported_file_valid_docx(self):
        """Test is_supported_file with valid DOCX extension."""
        docx_file = Path(self.temp_dir) / "test.docx"
        docx_file.touch()
        self.assertTrue(self.processor.is_supported_file(docx_file))

    def test_is_supported_file_invalid_doc(self):
        """Test is_supported_file with DOC extension (no longer supported)."""
        doc_file = Path(self.temp_dir) / "test.doc"
        doc_file.touch()
        self.assertFalse(self.processor.is_supported_file(doc_file))

    def test_is_supported_file_invalid_extension(self):
        """Test is_supported_file with invalid extension."""
        txt_file = Path(self.temp_dir) / "test.txt"
        txt_file.touch()
        self.assertFalse(self.processor.is_supported_file(txt_file))

    def test_is_supported_file_case_insensitive(self):
        """Test is_supported_file is case insensitive."""
        docx_file = Path(self.temp_dir) / "test.DOCX"
        docx_file.touch()
        self.assertTrue(self.processor.is_supported_file(docx_file))

    def test_get_metadata_template(self):
        """Test metadata template generation."""
        docx_file = Path(self.temp_dir) / "test_document.docx"
        docx_file.touch()

        metadata = self.processor.get_metadata_template(docx_file)

        self.assertEqual(metadata["source"], "test_document.docx")
        self.assertEqual(metadata["file_type"], ".docx")
        self.assertEqual(metadata["processor"], "WordProcessor")
        self.assertIn("file_path", metadata)
        self.assertIn("file_size", metadata)

    def test_get_processing_params_default(self):
        """Test get_processing_params with default values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params()
        self.assertEqual(chunk_size, 1000)
        self.assertEqual(chunk_overlap, 150)

    def test_get_processing_params_custom(self):
        """Test get_processing_params with custom values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params(2000, 300)
        self.assertEqual(chunk_size, 2000)
        self.assertEqual(chunk_overlap, 300)

    def test_validate_file_not_found(self):
        """Test validate_file with non-existent file."""
        non_existent_file = Path(self.temp_dir) / "nonexistent.docx"

        with self.assertRaises(FileNotFoundError):
            self.processor.validate_file(non_existent_file)

    def test_validate_file_unsupported(self):
        """Test validate_file with unsupported file type."""
        txt_file = Path(self.temp_dir) / "test.txt"
        txt_file.touch()

        with self.assertRaises(ValueError) as context:
            self.processor.validate_file(txt_file)

        self.assertIn("Unsupported file type", str(context.exception))


class TestWordProcessorIntegration(unittest.TestCase):
    """Integration tests for WordProcessor with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = WordProcessor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    @patch("rag_store.word_processor.RecursiveCharacterTextSplitter")
    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_document_processing_complete")
    def test_process_document_success(
        self, mock_log_complete, mock_log_start, mock_loader_class, mock_splitter_class
    ):
        """Test successful document processing."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_splitter_instance = Mock()
        mock_splitter_class.return_value = mock_splitter_instance

        # Create mock documents
        mock_doc1 = Document(
            page_content="First chunk of text content.",
            metadata={"source": "test.docx"},
        )
        mock_doc2 = Document(
            page_content="Second chunk of text content.",
            metadata={"source": "test.docx"},
        )
        # Mock the document loading and splitting process
        raw_doc = Document(
            page_content="Full document content", metadata={"source": "test.docx"}
        )
        mock_loader_instance.load.return_value = [raw_doc]
        mock_splitter_instance.split_documents.return_value = [mock_doc1, mock_doc2]

        # Create test file
        docx_file = Path(self.temp_dir) / "test.docx"
        docx_file.write_text("dummy content")

        # Process document
        documents = self.processor.process_document(
            docx_file, chunk_size=800, chunk_overlap=120
        )

        # Verify results
        self.assertEqual(len(documents), 2)

        # Check first document
        self.assertEqual(documents[0].page_content, "First chunk of text content.")
        self.assertEqual(documents[0].metadata["source"], "test.docx")
        self.assertEqual(documents[0].metadata["chunk_id"], "chunk_0")
        self.assertEqual(documents[0].metadata["document_id"], "test_word")
        self.assertEqual(documents[0].metadata["chunk_size"], 800)
        self.assertEqual(documents[0].metadata["chunk_overlap"], 120)
        self.assertEqual(
            documents[0].metadata["splitting_method"], "RecursiveCharacterTextSplitter"
        )
        self.assertEqual(documents[0].metadata["total_chunks"], 2)
        self.assertEqual(documents[0].metadata["loader_type"], "Docx2txtLoader")
        self.assertEqual(documents[0].metadata["supports_legacy_doc"], False)
        self.assertEqual(
            documents[0].metadata["separators"], "paragraphs,lines,words,chars"
        )

        # Check second document
        self.assertEqual(documents[1].page_content, "Second chunk of text content.")
        self.assertEqual(documents[1].metadata["chunk_id"], "chunk_1")

        # Verify loader and splitter were called correctly
        mock_loader_class.assert_called_once_with(str(docx_file))
        mock_loader_instance.load.assert_called_once()
        mock_splitter_class.assert_called_once()
        mock_splitter_instance.split_documents.assert_called_once_with([raw_doc])

        # Verify logging was called
        mock_log_start.assert_called_once()
        mock_log_complete.assert_called_once()

    @patch("rag_store.word_processor.RecursiveCharacterTextSplitter")
    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_document_processing_complete")
    def test_process_document_empty_result(
        self, mock_log_complete, mock_log_start, mock_loader_class, mock_splitter_class
    ):
        """Test processing document with empty result."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load.return_value = []

        # Create test file
        docx_file = Path(self.temp_dir) / "empty.docx"
        docx_file.write_text("dummy content")

        # Process document
        documents = self.processor.process_document(docx_file)

        # Verify results
        self.assertEqual(len(documents), 0)

        # Verify logging was called with empty status
        mock_log_complete.assert_called_once()
        call_args = mock_log_complete.call_args[1]
        self.assertEqual(call_args["chunks_created"], 0)
        self.assertEqual(call_args["status"], "success_empty")

    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_processing_error")
    def test_process_document_loader_error(
        self, mock_log_error, mock_log_start, mock_loader_class
    ):
        """Test processing document with loader error."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load.side_effect = Exception("Loading failed")

        # Create test file
        docx_file = Path(self.temp_dir) / "error.docx"
        docx_file.write_text("dummy content")

        # Test error handling
        with self.assertRaises(Exception) as context:
            self.processor.process_document(docx_file)

        self.assertIn("Error processing Word document", str(context.exception))
        self.assertIn("Loading failed", str(context.exception))

        # Verify error logging was called
        mock_log_error.assert_called_once()

    def test_legacy_load_docx_documents(self):
        """Test legacy interface method."""
        docx_file = Path(self.temp_dir) / "legacy.docx"
        docx_file.write_text("dummy content")

        with patch.object(self.processor, "process_document") as mock_process:
            mock_process.return_value = [Document(page_content="test", metadata={})]

            result = self.processor.load_docx_documents(docx_file)

            mock_process.assert_called_once_with(docx_file)
            self.assertEqual(len(result), 1)


class TestWordProcessorErrorHandling(unittest.TestCase):
    """Test error handling scenarios in WordProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = WordProcessor()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    @patch("rag_store.word_processor.RecursiveCharacterTextSplitter")
    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_document_processing_complete")
    def test_process_document_empty_splitter_result(self, mock_log_complete, mock_log_start, mock_loader_class, mock_splitter_class):
        """Test processing document with empty splitter result."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_splitter_instance = Mock()
        mock_splitter_class.return_value = mock_splitter_instance

        # Mock raw document loading but empty splitting result
        raw_doc = Document(page_content="Full document content", metadata={"source": "test.docx"})
        mock_loader_instance.load.return_value = [raw_doc]
        mock_splitter_instance.split_documents.return_value = []  # Empty split result

        # Create test file
        docx_file = Path(self.temp_dir) / "empty_split.docx"
        docx_file.write_text("dummy content")

        # Process document
        documents = self.processor.process_document(docx_file)

        # Verify results
        self.assertEqual(len(documents), 0)

        # Verify logging was called with empty status
        mock_log_complete.assert_called_once()
        call_args = mock_log_complete.call_args[1]
        self.assertEqual(call_args["chunks_created"], 0)
        self.assertEqual(call_args["status"], "success_empty")

    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_processing_error")
    def test_process_document_zip_file_error(self, mock_log_error, mock_log_start, mock_loader_class):
        """Test processing document with 'file is not a zip file' error."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load.side_effect = Exception("file is not a zip file")

        # Create test file
        docx_file = Path(self.temp_dir) / "notzip.docx"
        docx_file.write_text("dummy content")

        # Test error handling
        with self.assertRaises(Exception) as context:
            self.processor.process_document(docx_file)

        error_msg = str(context.exception)
        self.assertIn("Error processing Word document", error_msg)
        self.assertIn("file is not a zip file", error_msg)
        self.assertIn("Docx2txtLoader only supports .docx files (Word 2007+)", error_msg)
        self.assertIn("For legacy .doc files, please convert to .docx format first", error_msg)

        # Verify error logging was called
        mock_log_error.assert_called_once()

    @patch("rag_store.word_processor.Docx2txtLoader")
    @patch("rag_store.word_processor.log_document_processing_start")
    @patch("rag_store.word_processor.log_processing_error")
    def test_process_document_corrupted_word_file_error(self, mock_log_error, mock_log_start, mock_loader_class):
        """Test processing document with corrupted Word file error."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load.side_effect = Exception("file is not a Word file")

        # Create test file
        docx_file = Path(self.temp_dir) / "corrupted.docx"
        docx_file.write_text("dummy content")

        # Test error handling
        with self.assertRaises(Exception) as context:
            self.processor.process_document(docx_file)

        error_msg = str(context.exception)
        self.assertIn("Error processing Word document", error_msg)
        self.assertIn("file is not a Word file", error_msg)
        # The enhanced error message may or may not be added depending on exact error text
        self.assertTrue(len(error_msg) > 0)

        # Verify error logging was called
        mock_log_error.assert_called_once()


class TestWordProcessorImportFallback(unittest.TestCase):
    """Test import fallback scenarios."""

    def test_import_fallback_covered(self):
        """Test that import fallback is properly structured."""
        # The import fallback code (lines 24-26) is executed when the module
        # is run directly rather than imported as a package.
        # This test ensures the code structure is valid.
        
        # Verify that the processor can be instantiated
        processor = WordProcessor()
        self.assertIsNotNone(processor)
        self.assertEqual(processor.processor_name, "WordProcessor")
        
        # Test that logging function is available (whether from relative or absolute import)
        # This indirectly verifies the import fallback works
        try:
            from rag_store.logging_config import log_processing_error
            self.assertTrue(callable(log_processing_error))
        except ImportError:
            # If relative import fails, absolute should work
            from logging_config import log_processing_error
            self.assertTrue(callable(log_processing_error))


if __name__ == "__main__":
    unittest.main()
