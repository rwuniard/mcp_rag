"""
MHT Processing Module for RAG System

This module provides functionality to extract text from MHT (MIME HTML) files
and convert them into LangChain Document objects for embedding storage.
MHT files are web page archive files that contain HTML content with embedded resources.
"""

import time

from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader

try:
    from .document_processor import DocumentProcessor
    from .logging_config import (
        get_logger,
        log_document_processing_complete,
        log_document_processing_start,
        log_processing_error,
    )
except ImportError:
    from document_processor import DocumentProcessor
    from logging_config import (
        get_logger,
        log_document_processing_complete,
        log_document_processing_start,
        log_processing_error,
    )

logger = get_logger("mht_processor")


class MHTProcessor(DocumentProcessor):
    """Process MHT (MIME HTML) files and extract content for RAG storage."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = {".mht", ".mhtml"}
        # Optimized chunking parameters for HTML content
        self.default_chunk_size = 1200  # Larger chunks for structured HTML content
        self.default_chunk_overlap = 180  # 15% overlap ratio

    @property
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""
        return "MHT/MHTML web archive files (.mht, .mhtml)"

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if the file is a supported MHT file."""
        return file_path.suffix.lower() in self.supported_extensions

    def process_document(
        self,
        file_path: Path,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        **kwargs,
    ) -> list[Document]:
        """
        Process an MHT document and return LangChain Document objects.

        Args:
            file_path: Path to the MHT file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional processing parameters

        Returns:
            List of LangChain Document objects with content and metadata
        """
        self.validate_file(file_path)
        return self._process_mht_internal(file_path, chunk_size, chunk_overlap)

    def _process_mht_internal(
        self,
        mht_path: Path,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[Document]:
        """Internal MHT processing method."""
        start_time = time.time()
        chunk_size, chunk_overlap = self.get_processing_params(
            chunk_size, chunk_overlap
        )

        # Log processing start
        file_size = mht_path.stat().st_size if mht_path.exists() else 0
        context = log_document_processing_start(
            processor_name=self.processor_name,
            file_path=str(mht_path),
            file_size=file_size,
            file_type=mht_path.suffix,
        )

        try:
            # First try UnstructuredLoader for MHT files
            try:
                # Configure it to extract text content from HTML structures
                loader = UnstructuredLoader(
                    file_path=str(mht_path),
                    mode="elements",  # Extract structured elements
                    strategy="fast",  # Use fast processing for better performance
                )

                # Load the MHT content
                elements = loader.load()
            except Exception as unstructured_error:
                # If UnstructuredLoader fails, try manual MHT parsing as fallback
                logger.info(
                    f"UnstructuredLoader failed for {mht_path}, attempting manual MHT parsing: {unstructured_error}"
                )
                elements = self._parse_mht_manually(mht_path)

            if not elements:
                log_document_processing_complete(
                    context=context,
                    chunks_created=0,
                    processing_time_seconds=time.time() - start_time,
                    status="success_empty",
                )
                return []

            # Initialize the text splitter with optimized parameters for HTML content
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""],  # HTML-friendly separators
            )

            # Split documents and enhance metadata
            documents = text_splitter.split_documents(elements)

            # Enhance metadata with processing information
            base_metadata = self.get_metadata_template(mht_path)
            
            # Determine extraction method based on first document's metadata
            extraction_method = "unstructured_elements"
            if documents and "extraction_method" in documents[0].metadata:
                extraction_method = documents[0].metadata["extraction_method"]
            
            for i, doc in enumerate(documents):
                # Preserve original extraction method if it exists
                original_extraction_method = doc.metadata.get("extraction_method", extraction_method)
                
                # Update with base metadata
                doc.metadata.update(base_metadata)
                doc.metadata.update(
                    {
                        "chunk_id": f"chunk_{i}",
                        "document_id": f"{mht_path.stem}_mht",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "splitting_method": "RecursiveCharacterTextSplitter",
                        "total_chunks": len(documents),
                        "source_format": "mht/mhtml",
                        "extraction_method": original_extraction_method,  # Preserve original method
                    }
                )

            # Log successful completion
            processing_time = time.time() - start_time
            log_document_processing_complete(
                context=context,
                chunks_created=len(documents),
                processing_time_seconds=processing_time,
                status="success",
            )

            return documents

        except Exception as e:
            # Log error
            log_processing_error(
                context=context, error=e, error_type="mht_processing_error"
            )
            raise Exception(f"Error processing MHT file {mht_path}: {e!s}")

    def _parse_mht_manually(self, mht_path: Path) -> list[Document]:
        """
        Manually parse MHT file when UnstructuredLoader fails.
        
        This method extracts HTML content from MIME-formatted MHT files
        by parsing the MIME structure and extracting HTML sections.
        
        Args:
            mht_path: Path to the MHT file
            
        Returns:
            List of Document objects with extracted HTML content
        """
        import email
        import email.policy
        import re
        from html import unescape
        
        try:
            # Read the MHT file as an email message
            with open(mht_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse as email message
            msg = email.message_from_string(content, policy=email.policy.default)
            
            # Extract HTML content from multipart message
            html_content = ""
            title = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/html':
                        html_body = part.get_content()
                        if html_body:
                            html_content += html_body
            else:
                # Single part message
                if msg.get_content_type() == 'text/html':
                    html_content = msg.get_content()
            
            if not html_content:
                logger.warning(f"No HTML content found in MHT file: {mht_path}")
                return []
            
            # Extract text from HTML
            text_content = self._extract_text_from_html(html_content)
            
            # Extract title if available
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = unescape(title_match.group(1).strip())
            
            # Create Document object
            if text_content.strip():
                doc = Document(
                    page_content=text_content,
                    metadata={
                        "source": str(mht_path),
                        "title": title,
                        "content_type": "text/html",
                        "extraction_method": "manual_mht_parser"
                    }
                )
                return [doc]
            else:
                logger.warning(f"No text content extracted from MHT file: {mht_path}")
                return []
                
        except Exception as e:
            logger.error(f"Manual MHT parsing failed for {mht_path}: {e}")
            raise Exception(f"Manual MHT parsing failed: {e}")

    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Plain text content
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # BeautifulSoup is already installed as part of unstructured dependencies
            logger.error("BeautifulSoup not available for HTML parsing")
            return self._simple_html_to_text(html_content)
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"BeautifulSoup parsing failed, using simple HTML parser: {e}")
            return self._simple_html_to_text(html_content)

    def _simple_html_to_text(self, html_content: str) -> str:
        """
        Simple HTML to text conversion using regex (fallback method).
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Plain text content
        """
        import re
        from html import unescape
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        text = unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    # Legacy method for backward compatibility
    def process_mht_file(self, file_path: Path) -> list[Document]:
        """
        Process MHT file using the legacy interface.

        Args:
            file_path: Path to the MHT file

        Returns:
            List of LangChain Document objects
        """
        return self.process_document(file_path)