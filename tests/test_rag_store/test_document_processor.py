"""
Unit tests for document processor interface and implementations.

This test suite covers the universal document processor interface and
the PDF and Text processor implementations.
"""

import shutil

# Import the modules to test
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from rag_store.document_processor import DocumentProcessor, ProcessorRegistry
from rag_store.pdf_processor import PDFProcessor
from rag_store.text_processor import TextProcessor


class TestDocumentProcessorInterface(unittest.TestCase):
    """Test cases for the DocumentProcessor abstract interface."""

    def test_processor_registry_initialization(self):
        """Test ProcessorRegistry initialization."""
        registry = ProcessorRegistry()
        self.assertIsInstance(registry, ProcessorRegistry)
        self.assertEqual(len(registry.get_all_processors()), 0)
        self.assertEqual(len(registry.get_supported_extensions()), 0)

    def test_processor_registration(self):
        """Test registering processors in the registry."""
        registry = ProcessorRegistry()
        pdf_processor = PDFProcessor()
        text_processor = TextProcessor()

        registry.register_processor(pdf_processor)
        registry.register_processor(text_processor)

        processors = registry.get_all_processors()
        self.assertEqual(len(processors), 2)
        self.assertIn("PDFProcessor", processors)
        self.assertIn("TextProcessor", processors)

        extensions = registry.get_supported_extensions()
        expected_extensions = {".pdf", ".txt", ".md", ".text"}
        self.assertEqual(extensions, expected_extensions)

    def test_processor_lookup_by_file(self):
        """Test finding processors by file extension."""
        registry = ProcessorRegistry()
        pdf_processor = PDFProcessor()
        text_processor = TextProcessor()

        registry.register_processor(pdf_processor)
        registry.register_processor(text_processor)

        # Test PDF file
        pdf_file = Path("test.pdf")
        processor = registry.get_processor_for_file(pdf_file)
        self.assertIsInstance(processor, PDFProcessor)

        # Test text file
        txt_file = Path("test.txt")
        processor = registry.get_processor_for_file(txt_file)
        self.assertIsInstance(processor, TextProcessor)

        # Test unsupported file
        unsupported_file = Path("test.xyz")
        processor = registry.get_processor_for_file(unsupported_file)
        self.assertIsNone(processor)


class TestPDFProcessorInterface(unittest.TestCase):
    """Test cases for PDFProcessor interface implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()

    def test_pdf_processor_initialization(self):
        """Test PDFProcessor initialization."""
        self.assertIsInstance(self.processor, DocumentProcessor)
        self.assertEqual(self.processor.supported_extensions, {".pdf"})
        self.assertEqual(self.processor.default_chunk_size, 1800)
        self.assertEqual(self.processor.default_chunk_overlap, 270)

    def test_pdf_processor_file_type_description(self):
        """Test file type description."""
        description = self.processor.file_type_description
        self.assertEqual(description, "PDF documents (.pdf)")

    def test_pdf_processor_file_support(self):
        """Test file support checking."""
        pdf_file = Path("test.pdf")
        txt_file = Path("test.txt")

        self.assertTrue(self.processor.is_supported_file(pdf_file))
        self.assertFalse(self.processor.is_supported_file(txt_file))

    def test_pdf_processor_legacy_compatibility(self):
        """Test legacy method compatibility."""
        pdf_file = Path("test.pdf")
        self.assertTrue(self.processor.is_pdf_file(pdf_file))

    def test_pdf_processor_validation(self):
        """Test file validation."""
        nonexistent_file = Path("nonexistent.pdf")

        with self.assertRaises(FileNotFoundError):
            self.processor.validate_file(nonexistent_file)

        # Create temporary file for unsupported type test
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)

        try:
            with self.assertRaises(ValueError):
                self.processor.validate_file(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)


class TestTextProcessorInterface(unittest.TestCase):
    """Test cases for TextProcessor interface implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()

    def test_text_processor_initialization(self):
        """Test TextProcessor initialization."""
        self.assertIsInstance(self.processor, DocumentProcessor)
        self.assertEqual(self.processor.supported_extensions, {".txt", ".md", ".text"})
        self.assertEqual(self.processor.default_chunk_size, 300)
        self.assertEqual(self.processor.default_chunk_overlap, 50)

    def test_text_processor_file_type_description(self):
        """Test file type description."""
        description = self.processor.file_type_description
        self.assertEqual(description, "Text documents (.txt, .md, .text)")

    def test_text_processor_file_support(self):
        """Test file support checking."""
        txt_file = Path("test.txt")
        md_file = Path("test.md")
        pdf_file = Path("test.pdf")

        self.assertTrue(self.processor.is_supported_file(txt_file))
        self.assertTrue(self.processor.is_supported_file(md_file))
        self.assertFalse(self.processor.is_supported_file(pdf_file))


class TestProcessorRegistryIntegration(unittest.TestCase):
    """Integration tests for the complete processor registry system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_registry_workflow(self):
        """Test the complete workflow from registry to processing."""
        # Create registry and register processors
        registry = ProcessorRegistry()
        registry.register_processor(PDFProcessor())
        registry.register_processor(TextProcessor())

        # Create test files
        txt_file = self.temp_dir_path / "test.txt"
        txt_file.write_text("This is a test document for text processing.")

        # Test processing via registry
        with patch("rag_store.text_processor.TextLoader") as mock_loader:
            mock_doc = Mock()
            mock_doc.page_content = "Test content"
            mock_doc.metadata = {}
            mock_loader.return_value.load_and_split.return_value = [mock_doc]

            documents = registry.process_document(txt_file)
            self.assertGreater(len(documents), 0)

    def test_registry_error_handling(self):
        """Test registry error handling for unsupported files."""
        registry = ProcessorRegistry()
        registry.register_processor(PDFProcessor())

        unsupported_file = self.temp_dir_path / "test.xyz"
        unsupported_file.write_text("Unsupported content")

        with self.assertRaises(ValueError) as context:
            registry.process_document(unsupported_file)

        self.assertIn("No processor found", str(context.exception))

    def test_processor_metadata_enhancement(self):
        """Test that processors properly enhance metadata."""
        processor = TextProcessor()

        # Test metadata template generation
        test_file = self.temp_dir_path / "test.txt"
        test_file.write_text("Test content")

        metadata = processor.get_metadata_template(test_file)

        expected_keys = {"source", "file_path", "file_type", "processor", "file_size"}
        self.assertEqual(set(metadata.keys()), expected_keys)
        self.assertEqual(metadata["file_type"], ".txt")
        self.assertEqual(metadata["processor"], "TextProcessor")


if __name__ == "__main__":
    unittest.main(verbosity=2)
