"""
Text Processing Module for RAG System

This module provides functionality to extract text from text files and convert
them into LangChain Document objects for embedding storage.
"""

from pathlib import Path
from typing import List, Optional
import time

from langchain.schema import Document
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

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

logger = get_logger("text_processor")


class TextProcessor(DocumentProcessor):
    """Process text files and extract content for RAG storage."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.txt', '.md', '.text'}
        # Optimized chunking parameters for text files
        self.default_chunk_size = 300   # Smaller chunks for text content
        self.default_chunk_overlap = 50 # 16% overlap ratio
        
    @property
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""
        return "Text documents (.txt, .md, .text)"
        
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if the file is a supported text file."""
        return file_path.suffix.lower() in self.supported_extensions
        
    def process_document(
        self, 
        file_path: Path, 
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separator: str = "\n\n",
        **kwargs
    ) -> List[Document]:
        """
        Process a text document and return LangChain Document objects.
        
        Args:
            file_path: Path to the text file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            separator: Text separator for chunking (default: double newline)
            **kwargs: Additional processing parameters
            
        Returns:
            List of LangChain Document objects with content and metadata
        """
        self.validate_file(file_path)
        return self._process_text_internal(file_path, chunk_size, chunk_overlap, separator)
        
    def _process_text_internal(
        self, 
        file_path: Path, 
        chunk_size: Optional[int] = None, 
        chunk_overlap: Optional[int] = None,
        separator: str = "\n\n"
    ) -> List[Document]:
        """Internal text processing method."""
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
            # Use TextLoader for basic text loading
            loader = TextLoader(str(file_path), encoding='utf-8')
            
            # Initialize text splitter with specified parameters
            text_splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separator=separator
            )
            
            # Load and split the text
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
                    "document_id": f"{file_path.stem}_text",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "separator": separator,
                    "splitting_method": "CharacterTextSplitter",
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
            
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    loader = TextLoader(str(file_path), encoding=encoding)
                    documents = loader.load_and_split(text_splitter)
                    
                    # Add encoding info to metadata
                    base_metadata = self.get_metadata_template(file_path)
                    base_metadata["encoding"] = encoding
                    
                    for i, doc in enumerate(documents):
                        doc.metadata.update(base_metadata)
                        doc.metadata.update({
                            "chunk_id": f"chunk_{i}",
                            "document_id": f"{file_path.stem}_text",
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap,
                            "separator": separator,
                            "splitting_method": "CharacterTextSplitter",
                            "total_chunks": len(documents)
                        })
                    
                    return documents
                except UnicodeDecodeError:
                    continue
                    
            raise Exception(f"Could not decode text file {file_path} with any supported encoding")
            
        except Exception as e:
            raise Exception(f"Error processing text file {file_path}: {str(e)}")
            
    # Legacy method for backward compatibility
    def load_txt_documents(self, file_path: Path, separator: str = "\n\n") -> List[Document]:
        """
        Load documents from text files using the legacy interface.
        
        Args:
            file_path: Path to the text file
            separator: Text separator for chunking
            
        Returns:
            List of LangChain Document objects
        """
        return self.process_document(file_path, separator=separator)