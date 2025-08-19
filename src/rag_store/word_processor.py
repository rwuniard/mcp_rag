"""
Word Processing Module for RAG System

This module provides functionality to extract text from Microsoft Word documents
and convert them into LangChain Document objects for embedding storage.
"""

from pathlib import Path
from typing import List, Optional
import time

from langchain.schema import Document
from langchain_community.document_loaders import Docx2txtLoader
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

logger = get_logger("word_processor")


class WordProcessor(DocumentProcessor):
    """Process Microsoft Word documents and extract content for RAG storage."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.docx', '.doc'}
        # Word documents often contain structured content, so we use parameters 
        # between PDF (1800/270) and text (300/50) for balanced chunking
        self.default_chunk_size = 1000   # Medium chunks for Word content
        self.default_chunk_overlap = 150 # 15% overlap ratio
        
    @property
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""
        return "Microsoft Word documents (.docx, .doc)"
        
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if the file is a supported Word document."""
        return file_path.suffix.lower() in self.supported_extensions
        
    def process_document(
        self, 
        file_path: Path, 
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        **kwargs
    ) -> List[Document]:
        """
        Process a Word document and return LangChain Document objects.
        
        Args:
            file_path: Path to the Word document
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional processing parameters
            
        Returns:
            List of LangChain Document objects with content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
            Exception: For other processing errors
        """
        self.validate_file(file_path)
        return self._process_word_internal(file_path, chunk_size, chunk_overlap)
        
    def _process_word_internal(
        self, 
        file_path: Path, 
        chunk_size: Optional[int] = None, 
        chunk_overlap: Optional[int] = None
    ) -> List[Document]:
        """Internal Word document processing method."""
        start_time = time.time()
        chunk_size, chunk_overlap = self.get_processing_params(chunk_size, chunk_overlap)
        
        # Log processing start
        file_size = file_path.stat().st_size if file_path.exists() else 0
        context = log_document_processing_start(
            processor_name=self.processor_name,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_path.suffix
        )
        
        try:
            # Use Docx2txtLoader for Word document loading
            loader = Docx2txtLoader(str(file_path))
            
            # Use RecursiveCharacterTextSplitter for better text boundary handling
            # This is better for Word documents which often contain structured content
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]  # Split on paragraphs, then lines, then words
            )
            
            # Load and split the document
            documents = loader.load_and_split(text_splitter)
            
            if not documents:
                log_document_processing_complete(
                    context=context,
                    chunks_created=0,
                    processing_time_seconds=time.time() - start_time,
                    status="success_empty"
                )
                return []
            
            # Enhance metadata with processing information
            base_metadata = self.get_metadata_template(file_path)
            for i, doc in enumerate(documents):
                # Preserve original metadata and add our enhancements
                doc.metadata.update(base_metadata)
                doc.metadata.update({
                    "chunk_id": f"chunk_{i}",
                    "document_id": f"{file_path.stem}_docx",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "splitting_method": "RecursiveCharacterTextSplitter",
                    "separators": ["\n\n", "\n", " ", ""],
                    "total_chunks": len(documents)
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
            # Log processing error
            log_processing_error(
                context=context,
                error=str(e),
                error_type="word_processing_error"
            )
            raise Exception(f"Error processing Word document {file_path}: {str(e)}")
            
    # Legacy method for backward compatibility
    def load_docx_documents(self, file_path: Path) -> List[Document]:
        """
        Load documents from Word files using the legacy interface.
        
        Args:
            file_path: Path to the Word document
            
        Returns:
            List of LangChain Document objects
        """
        return self.process_document(file_path)