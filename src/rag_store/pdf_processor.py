"""
PDF Processing Module for RAG System

This module provides functionality to extract text from PDF files and convert
them into LangChain Document objects for embedding storage.
"""

from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFProcessor:
    """Process PDF files and extract text content for RAG storage."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf'}
        # Optimized chunking parameters based on industry best practices (2024)
        self.default_pdf_chunk_size = 1800  # Technical content benefits from larger context
        self.default_pdf_overlap = 270      # 15% overlap ratio
    
    def is_pdf_file(self, file_path: Path) -> bool:
        """Check if the file is a supported PDF file."""
        return file_path.suffix.lower() in self.supported_extensions
    
    
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
        # Use optimized defaults if not specified
        if chunk_size is None:
            chunk_size = self.default_pdf_chunk_size
        if chunk_overlap is None:
            chunk_overlap = self.default_pdf_overlap
            
        # Use PyPDFLoader for better LangChain integration
        loader = PyPDFLoader(str(pdf_path))
        
        # Use RecursiveCharacterTextSplitter for intelligent splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Split at paragraphs, then lines, then words
        )
        
        # Load and split the PDF
        documents = loader.load_and_split(text_splitter)
        
        # Enhance metadata with our comprehensive tracking
        for i, doc in enumerate(documents):
            doc.metadata.update({
                "source": str(pdf_path),
                "chunk_id": i,
                "document_id": pdf_path.stem,
                "file_type": "pdf",
                "total_chunks": len(documents),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "splitting_method": "recursive"
            })
        
        return documents
