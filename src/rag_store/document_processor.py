"""
Document Processor Interface and Base Classes

This module provides a universal interface for document processing that can be
extended to support various file types (PDF, TXT, DOCX, XLSX, etc.).
"""

import time

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from langchain.schema import Document

try:
    from .logging_config import get_logger, log_registry_operation
except ImportError:
    # Fallback for direct execution
    from logging_config import get_logger, log_registry_operation

logger = get_logger("document_processor")


class DocumentProcessor(ABC):
    """
    Abstract base class for document processors.

    This interface ensures all document processors have consistent behavior
    and can be used interchangeably in the RAG system.
    """

    def __init__(self):
        """Initialize the document processor."""
        self.supported_extensions: set[str] = set()
        self.default_chunk_size: int = 1000
        self.default_chunk_overlap: int = 100
        self.processor_name: str = self.__class__.__name__

    @property
    @abstractmethod
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""

    @abstractmethod
    def is_supported_file(self, file_path: Path) -> bool:
        """
        Check if the file type is supported by this processor.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file is supported, False otherwise
        """

    @abstractmethod
    def process_document(
        self,
        file_path: Path,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        **kwargs,
    ) -> list[Document]:
        """
        Process a document and return LangChain Document objects.

        Args:
            file_path: Path to the document file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional processor-specific parameters

        Returns:
            List of LangChain Document objects with content and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
            Exception: For other processing errors
        """

    def get_metadata_template(self, file_path: Path) -> dict[str, Any]:
        """
        Generate common metadata template for documents.

        Args:
            file_path: Path to the source file

        Returns:
            Dictionary with common metadata fields
        """
        return {
            "source": str(file_path.name),
            "file_path": str(file_path),
            "file_type": file_path.suffix.lower(),
            "processor": self.processor_name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
        }

    def validate_file(self, file_path: Path) -> None:
        """
        Validate that the file exists and is supported.

        Args:
            file_path: Path to the file to validate

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.is_supported_file(file_path):
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported types: {self.supported_extensions}"
            )

    def get_processing_params(
        self, chunk_size: int | None = None, chunk_overlap: int | None = None
    ) -> tuple[int, int]:
        """
        Get processing parameters with fallback to defaults.

        Args:
            chunk_size: Requested chunk size
            chunk_overlap: Requested chunk overlap

        Returns:
            Tuple of (chunk_size, chunk_overlap)
        """
        final_chunk_size = (
            chunk_size if chunk_size is not None else self.default_chunk_size
        )
        final_chunk_overlap = (
            chunk_overlap if chunk_overlap is not None else self.default_chunk_overlap
        )

        return final_chunk_size, final_chunk_overlap


class ProcessorRegistry:
    """
    Registry for managing document processors.

    Allows dynamic registration and lookup of processors by file extension.
    """

    def __init__(self):
        self._processors: dict[str, DocumentProcessor] = {}
        self._extension_map: dict[str, str] = {}

    def register_processor(self, processor: DocumentProcessor) -> None:
        """
        Register a document processor.

        Args:
            processor: DocumentProcessor instance to register
        """
        processor_name = processor.__class__.__name__
        self._processors[processor_name] = processor

        # Map file extensions to processor
        for extension in processor.supported_extensions:
            self._extension_map[extension.lower()] = processor_name

        log_registry_operation(
            "register_processor",
            processor_name=processor_name,
            supported_extensions=list(processor.supported_extensions),
            total_processors=len(self._processors),
        )

    def get_processor_for_file(self, file_path: Path) -> DocumentProcessor | None:
        """
        Get the appropriate processor for a file.

        Args:
            file_path: Path to the file

        Returns:
            DocumentProcessor instance or None if no processor found
        """
        extension = file_path.suffix.lower()
        processor_name = self._extension_map.get(extension)

        if processor_name:
            return self._processors.get(processor_name)

        return None

    def get_supported_extensions(self) -> set[str]:
        """Get all supported file extensions."""
        return set(self._extension_map.keys())

    def get_all_processors(self) -> dict[str, DocumentProcessor]:
        """Get all registered processors."""
        return self._processors.copy()

    def process_document(
        self,
        file_path: Path,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        **kwargs,
    ) -> list[Document]:
        """
        Process a document using the appropriate processor.

        Args:
            file_path: Path to the document file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional processor-specific parameters

        Returns:
            List of LangChain Document objects

        Raises:
            ValueError: If no processor found for file type
        """
        start_time = time.time()
        processor = self.get_processor_for_file(file_path)

        if not processor:
            log_registry_operation(
                "processor_lookup_failed",
                file_path=str(file_path),
                file_extension=file_path.suffix,
                supported_extensions=list(self.get_supported_extensions()),
            )
            raise ValueError(
                f"No processor found for file type: {file_path.suffix}. "
                f"Supported extensions: {self.get_supported_extensions()}"
            )

        log_registry_operation(
            "processor_lookup_success",
            file_path=str(file_path),
            processor_name=processor.__class__.__name__,
            file_extension=file_path.suffix,
        )

        documents = processor.process_document(
            file_path, chunk_size, chunk_overlap, **kwargs
        )

        processing_time = time.time() - start_time
        log_registry_operation(
            "document_processed",
            file_path=str(file_path),
            processor_name=processor.__class__.__name__,
            chunks_created=len(documents),
            processing_time_seconds=processing_time,
        )

        return documents
