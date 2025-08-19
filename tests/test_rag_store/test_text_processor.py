"""
Unit tests for Text document processor.

This test suite covers the TextProcessor class functionality
including document processing, encoding handling, and error scenarios.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_store.text_processor import TextProcessor
from langchain.schema import Document


class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = TextProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
        
    def test_processor_initialization(self):
        """Test TextProcessor initialization."""
        processor = TextProcessor()
        self.assertIsInstance(processor, TextProcessor)
        self.assertEqual(processor.supported_extensions, {'.txt', '.md', '.text'})
        self.assertEqual(processor.default_chunk_size, 300)
        self.assertEqual(processor.default_chunk_overlap, 50)
        self.assertEqual(processor.processor_name, "TextProcessor")
        
    def test_file_type_description(self):
        """Test file type description."""
        description = self.processor.file_type_description
        self.assertEqual(description, "Text documents (.txt, .md, .text)")
        
    def test_is_supported_file_valid_extensions(self):
        """Test is_supported_file with valid extensions."""
        txt_file = self.temp_dir_path / "test.txt"
        md_file = self.temp_dir_path / "test.md"
        text_file = self.temp_dir_path / "test.text"
        
        txt_file.touch()
        md_file.touch()
        text_file.touch()
        
        self.assertTrue(self.processor.is_supported_file(txt_file))
        self.assertTrue(self.processor.is_supported_file(md_file))
        self.assertTrue(self.processor.is_supported_file(text_file))
        
    def test_is_supported_file_case_insensitive(self):
        """Test is_supported_file is case insensitive."""
        txt_file = self.temp_dir_path / "test.TXT"
        md_file = self.temp_dir_path / "test.MD"
        
        txt_file.touch()
        md_file.touch()
        
        self.assertTrue(self.processor.is_supported_file(txt_file))
        self.assertTrue(self.processor.is_supported_file(md_file))
        
    def test_is_supported_file_invalid_extension(self):
        """Test is_supported_file with invalid extension."""
        docx_file = self.temp_dir_path / "test.docx"
        docx_file.touch()
        self.assertFalse(self.processor.is_supported_file(docx_file))
        
    def test_get_metadata_template(self):
        """Test metadata template generation."""
        txt_file = self.temp_dir_path / "test_document.txt"
        txt_file.write_text("test content")
        
        metadata = self.processor.get_metadata_template(txt_file)
        
        self.assertEqual(metadata["source"], "test_document.txt")
        self.assertEqual(metadata["file_type"], ".txt")
        self.assertEqual(metadata["processor"], "TextProcessor")
        self.assertIn("file_path", metadata)
        self.assertIn("file_size", metadata)
        self.assertGreater(metadata["file_size"], 0)
        
    def test_get_processing_params_default(self):
        """Test get_processing_params with default values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params()
        self.assertEqual(chunk_size, 300)
        self.assertEqual(chunk_overlap, 50)
        
    def test_get_processing_params_custom(self):
        """Test get_processing_params with custom values."""
        chunk_size, chunk_overlap = self.processor.get_processing_params(1000, 200)
        self.assertEqual(chunk_size, 1000)
        self.assertEqual(chunk_overlap, 200)
        
    def test_validate_file_not_found(self):
        """Test validate_file with non-existent file."""
        non_existent_file = self.temp_dir_path / "nonexistent.txt"
        
        with self.assertRaises(FileNotFoundError):
            self.processor.validate_file(non_existent_file)
            
    def test_validate_file_unsupported(self):
        """Test validate_file with unsupported file type."""
        pdf_file = self.temp_dir_path / "test.pdf"
        pdf_file.touch()
        
        with self.assertRaises(ValueError) as context:
            self.processor.validate_file(pdf_file)
            
        self.assertIn("Unsupported file type", str(context.exception))


class TestTextProcessorIntegration(unittest.TestCase):
    """Integration tests for TextProcessor with mocked dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
        
    @patch('rag_store.text_processor.TextLoader')
    @patch('rag_store.text_processor.log_document_processing_start')
    @patch('rag_store.text_processor.log_document_processing_complete')
    def test_process_document_success(self, mock_log_complete, mock_log_start, mock_loader_class):
        """Test successful document processing."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        
        # Create mock documents
        mock_doc1 = Document(
            page_content="First paragraph of text content.",
            metadata={"source": "test.txt"}
        )
        mock_doc2 = Document(
            page_content="Second paragraph of text content.", 
            metadata={"source": "test.txt"}
        )
        mock_loader_instance.load_and_split.return_value = [mock_doc1, mock_doc2]
        
        # Create test file
        txt_file = self.temp_dir_path / "test.txt"
        txt_file.write_text("Test content with multiple paragraphs")
        
        # Process document
        documents = self.processor.process_document(txt_file, chunk_size=200, chunk_overlap=40, separator="\n")
        
        # Verify results
        self.assertEqual(len(documents), 2)
        
        # Check first document metadata
        self.assertEqual(documents[0].page_content, "First paragraph of text content.")
        self.assertEqual(documents[0].metadata["source"], "test.txt")
        self.assertEqual(documents[0].metadata["chunk_id"], "chunk_0")
        self.assertEqual(documents[0].metadata["document_id"], "test_text")
        self.assertEqual(documents[0].metadata["chunk_size"], 200)
        self.assertEqual(documents[0].metadata["chunk_overlap"], 40)
        self.assertEqual(documents[0].metadata["separator"], "\n")
        self.assertEqual(documents[0].metadata["splitting_method"], "CharacterTextSplitter")
        self.assertEqual(documents[0].metadata["total_chunks"], 2)
        
        # Check second document metadata
        self.assertEqual(documents[1].metadata["chunk_id"], "chunk_1")
        
        # Verify loader was called correctly
        mock_loader_class.assert_called_once_with(str(txt_file), encoding='utf-8')
        mock_loader_instance.load_and_split.assert_called_once()
        
        # Verify logging was called
        mock_log_start.assert_called_once()
        mock_log_complete.assert_called_once()
        
    @patch('rag_store.text_processor.TextLoader')
    @patch('rag_store.text_processor.log_document_processing_start')
    @patch('rag_store.text_processor.log_document_processing_complete')
    def test_process_document_empty_result(self, mock_log_complete, mock_log_start, mock_loader_class):
        """Test processing document with empty result."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_and_split.return_value = []
        
        # Create test file
        txt_file = self.temp_dir_path / "empty.txt"
        txt_file.write_text("")
        
        # Process document
        documents = self.processor.process_document(txt_file)
        
        # Verify results
        self.assertEqual(len(documents), 0)
        
        # Verify logging was called with empty status
        mock_log_complete.assert_called_once()
        call_args = mock_log_complete.call_args[1]
        self.assertEqual(call_args["chunks_created"], 0)
        self.assertEqual(call_args["status"], "success_empty")
        
    @patch('rag_store.text_processor.TextLoader')
    @patch('rag_store.text_processor.log_document_processing_start')
    @patch('rag_store.text_processor.log_processing_error')
    def test_process_document_unicode_error_with_fallback_success(self, mock_log_error, mock_log_start, mock_loader_class):
        """Test processing document with Unicode error that succeeds with fallback encoding."""
        # Setup mocks - first call fails with UnicodeDecodeError, second succeeds
        mock_log_start.return_value = {"context": "test"}
        
        def loader_side_effect(*args, **kwargs):
            if kwargs.get('encoding') == 'utf-8':
                # First call with UTF-8 fails
                mock_loader = Mock()
                mock_loader.load_and_split.side_effect = UnicodeDecodeError(
                    'utf-8', b'', 0, 1, 'invalid start byte'
                )
                return mock_loader
            elif kwargs.get('encoding') == 'latin-1':
                # Second call with latin-1 succeeds
                mock_loader = Mock()
                mock_doc = Document(
                    page_content="Text with special characters",
                    metadata={"source": "test.txt"}
                )
                mock_loader.load_and_split.return_value = [mock_doc]
                return mock_loader
        
        mock_loader_class.side_effect = loader_side_effect
        
        # Create test file
        txt_file = self.temp_dir_path / "special_chars.txt"
        txt_file.write_text("Test content")
        
        # Process document
        documents = self.processor.process_document(txt_file)
        
        # Verify results
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content, "Text with special characters")
        self.assertEqual(documents[0].metadata["encoding"], "latin-1")
        self.assertEqual(documents[0].metadata["chunk_id"], "chunk_0")
        
        # Verify TextLoader was called twice (utf-8 then latin-1)
        self.assertEqual(mock_loader_class.call_count, 2)
        
    @patch('rag_store.text_processor.TextLoader')
    @patch('rag_store.text_processor.log_document_processing_start')
    @patch('rag_store.text_processor.log_processing_error')
    def test_process_document_unicode_error_all_encodings_fail(self, mock_log_error, mock_log_start, mock_loader_class):
        """Test processing document where all encoding attempts fail."""
        # Setup mocks - all encodings fail
        mock_log_start.return_value = {"context": "test"}
        
        def loader_side_effect(*args, **kwargs):
            mock_loader = Mock()
            mock_loader.load_and_split.side_effect = UnicodeDecodeError(
                kwargs.get('encoding', 'utf-8'), b'', 0, 1, 'invalid start byte'
            )
            return mock_loader
        
        mock_loader_class.side_effect = loader_side_effect
        
        # Create test file
        txt_file = self.temp_dir_path / "bad_encoding.txt"
        txt_file.write_text("Test content")
        
        # Test error handling
        with self.assertRaises(Exception) as context:
            self.processor.process_document(txt_file)
            
        self.assertIn("Could not decode text file", str(context.exception))
        
        # Verify all encodings were tried (utf-8 + 3 fallbacks)
        self.assertEqual(mock_loader_class.call_count, 4)
        
    @patch('rag_store.text_processor.TextLoader')
    @patch('rag_store.text_processor.log_document_processing_start')
    @patch('rag_store.text_processor.log_processing_error')
    def test_process_document_general_error(self, mock_log_error, mock_log_start, mock_loader_class):
        """Test processing document with general error."""
        # Setup mocks
        mock_log_start.return_value = {"context": "test"}
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_and_split.side_effect = RuntimeError("File is corrupted")
        
        # Create test file
        txt_file = self.temp_dir_path / "error.txt"
        txt_file.write_text("Test content")
        
        # Test error handling
        with self.assertRaises(Exception) as context:
            self.processor.process_document(txt_file)
            
        self.assertIn("Error processing text file", str(context.exception))
        self.assertIn("File is corrupted", str(context.exception))
        
    def test_legacy_load_txt_documents(self):
        """Test legacy interface method."""
        txt_file = self.temp_dir_path / "legacy.txt"
        txt_file.write_text("Test content")
        
        with patch.object(self.processor, 'process_document') as mock_process:
            mock_process.return_value = [Document(page_content="test", metadata={})]
            
            result = self.processor.load_txt_documents(txt_file, separator="\n")
            
            mock_process.assert_called_once_with(txt_file, separator="\n")
            self.assertEqual(len(result), 1)
            
    def test_legacy_load_txt_documents_custom_separator(self):
        """Test legacy interface method with custom separator."""
        txt_file = self.temp_dir_path / "legacy.txt"
        txt_file.write_text("Test content")
        
        with patch.object(self.processor, 'process_document') as mock_process:
            mock_process.return_value = [Document(page_content="test", metadata={})]
            
            result = self.processor.load_txt_documents(txt_file, separator="---")
            
            mock_process.assert_called_once_with(txt_file, separator="---")
            self.assertEqual(len(result), 1)

    @patch('rag_store.text_processor.TextLoader')
    def test_process_document_with_default_separator(self, mock_loader_class):
        """Test document processing with default separator parameter."""
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        
        mock_doc = Document(
            page_content="Test content",
            metadata={"source": "test.txt"}
        )
        mock_loader_instance.load_and_split.return_value = [mock_doc]
        
        txt_file = self.temp_dir_path / "test.txt"
        txt_file.write_text("Test content")
        
        # Call without separator parameter to test default
        documents = self.processor.process_document(txt_file)
        
        # Verify default separator was used
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["separator"], "\n\n")


class TestTextProcessorEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios for TextProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
        
    def test_process_document_file_validation_error(self):
        """Test that file validation errors are propagated."""
        non_existent_file = self.temp_dir_path / "nonexistent.txt"
        
        with self.assertRaises(FileNotFoundError):
            self.processor.process_document(non_existent_file)
            
    def test_process_document_unsupported_file_type(self):
        """Test processing unsupported file type."""
        pdf_file = self.temp_dir_path / "test.pdf"
        pdf_file.write_text("Not actually a PDF")
        
        with self.assertRaises(ValueError):
            self.processor.process_document(pdf_file)
            
    @patch('rag_store.text_processor.TextLoader')
    def test_process_document_with_kwargs(self, mock_loader_class):
        """Test process_document passes through kwargs correctly."""
        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_and_split.return_value = [
            Document(page_content="test", metadata={})
        ]
        
        txt_file = self.temp_dir_path / "test.txt"
        txt_file.write_text("Test content")
        
        # Call with additional kwargs
        documents = self.processor.process_document(
            txt_file, 
            chunk_size=100, 
            chunk_overlap=20,
            separator="|",
            custom_param="test_value"
        )
        
        # Verify processing worked and metadata includes separator
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["separator"], "|")


if __name__ == '__main__':
    unittest.main()