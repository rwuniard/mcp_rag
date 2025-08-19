"""
PDF Processing Module for RAG System

This module provides functionality to extract text from PDF files and convert
them into LangChain Document objects for embedding storage.
"""

from pathlib import Path
from typing import List, Optional
import time

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from .document_processor import DocumentProcessor
    from .logging_config import (
        get_logger, 
        log_document_processing_start,
        log_document_processing_complete,
        log_processing_error
    )
except ImportError:
    from document_processor import DocumentProcessor
    from logging_config import (
        get_logger, 
        log_document_processing_start,
        log_document_processing_complete,
        log_processing_error
    )

logger = get_logger("pdf_processor")


class PDFProcessor(DocumentProcessor):
    """Process PDF files and extract text content for RAG storage."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.pdf'}
        # Optimized chunking parameters based on industry best practices (2024)
        self.default_chunk_size = 1800  # Technical content benefits from larger context
        self.default_chunk_overlap = 270  # 15% overlap ratio
        
    @property
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""
        return "PDF documents (.pdf)"
        
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if the file is a supported PDF file."""
        return file_path.suffix.lower() in self.supported_extensions
        
    # Legacy method for backward compatibility
    def is_pdf_file(self, file_path: Path) -> bool:
        """Check if the file is a supported PDF file."""
        return self.is_supported_file(file_path)
    
    
    def process_document(
        self, 
        file_path: Path, 
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        **kwargs
    ) -> List[Document]:
        """
        Process a PDF document and return LangChain Document objects.
        
        Args:
            file_path: Path to the PDF file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional processing parameters
            
        Returns:
            List of LangChain Document objects with content and metadata
        """
        self.validate_file(file_path)
        return self._process_pdf_internal(file_path, chunk_size, chunk_overlap)
        
    def _process_pdf_internal(self, pdf_path: Path, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> List[Document]:
        """Internal PDF processing method."""
        start_time = time.time()
        chunk_size, chunk_overlap = self.get_processing_params(chunk_size, chunk_overlap)
        
        # Log processing start
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
        context = log_document_processing_start(
            processor_name=self.processor_name,
            file_path=str(pdf_path),
            file_size=file_size,
            file_type=pdf_path.suffix
        )
        
        try:
            # Use PyPDFLoader for better LangChain integration
            loader = PyPDFLoader(str(pdf_path))
            
            # Load PDF pages
            pages = loader.load()
            
            if not pages:
                log_document_processing_complete(
                    context=context,
                    chunks_created=0,
                    processing_time_seconds=time.time() - start_time,
                    status="success_empty"
                )
                return []
            
            # Initialize the text splitter with optimized parameters
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Split documents and enhance metadata
            documents = text_splitter.split_documents(pages)
            
            # Enhance metadata with processing information
            base_metadata = self.get_metadata_template(pdf_path)
            for i, doc in enumerate(documents):
                # Preserve original page metadata and add our enhancements
                doc.metadata.update(base_metadata)
                doc.metadata.update({
                    "chunk_id": f"chunk_{i}",
                    "document_id": f"{pdf_path.stem}_pdf",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "splitting_method": "RecursiveCharacterTextSplitter"
                })
            
            # Log successful completion
            processing_time = time.time() - start_time
            log_document_processing_complete(
                context=context,
                chunks_created=len(documents),
                processing_time_seconds=processing_time,
                status="success"
            )
                
            return documents
            
        except Exception as e:
            # Log error
            log_processing_error(
                context=context,
                error=e,
                error_type="pdf_processing_error"
            )
            raise Exception(f"Error processing PDF {pdf_path}: {str(e)}")
    
    # Legacy method for backward compatibility
    def pdf_to_documents_recursive(self, pdf_path: Path, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        """
        Convert PDF file to LangChain Document objects using RecursiveCharacterTextSplitter.
        This approach provides better text splitting at natural boundaries.
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Maximum size of each text chunk (defaults to optimized PDF chunk size)
            chunk_overlap: Number of characters to overlap between chunks (defaults to optimized overlap)
            
        Returns:
            List of LangChain Document objects
        """
        # Delegate to the new interface method
        return self.process_document(pdf_path, chunk_size, chunk_overlap)
