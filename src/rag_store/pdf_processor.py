"""
PDF Processing Module for RAG System

This module provides functionality to extract text from PDF files and convert
them into LangChain Document objects for embedding storage.
Uses PyMuPDF for OCR capabilities to handle image-based PDFs.
"""

import time
import fitz  # PyMuPDF
from io import BytesIO

from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# OCR dependencies (optional)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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

logger = get_logger("pdf_processor")


class PDFProcessor(DocumentProcessor):
    """Process PDF files and extract text content for RAG storage using PyMuPDF with OCR capabilities."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = {".pdf"}
        # Optimized chunking parameters based on industry best practices (2024)
        self.default_chunk_size = 1800  # Technical content benefits from larger context
        self.default_chunk_overlap = 270  # 15% overlap ratio

    @property
    def file_type_description(self) -> str:
        """Return a human-readable description of supported file types."""
        return "PDF documents (.pdf) with OCR support"

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
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        **kwargs,
    ) -> list[Document]:
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

    def _process_pdf_internal(
        self,
        pdf_path: Path,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[Document]:
        """Internal PDF processing method using PyMuPDF with OCR capabilities."""
        start_time = time.time()
        chunk_size, chunk_overlap = self.get_processing_params(
            chunk_size, chunk_overlap
        )

        # Log processing start
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
        context = log_document_processing_start(
            processor_name=self.processor_name,
            file_path=str(pdf_path),
            file_size=file_size,
            file_type=pdf_path.suffix,
        )

        try:
            # Use PyMuPDF for OCR-capable PDF processing
            doc = fitz.open(str(pdf_path))
            
            if doc.page_count == 0:
                doc.close()
                log_document_processing_complete(
                    context=context,
                    chunks_created=0,
                    processing_time_seconds=time.time() - start_time,
                    status="success_empty",
                )
                return []

            # Extract text from each page with OCR fallback
            pages = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Try to extract text normally first
                text = page.get_text()
                extraction_method = "pymupdf_text"
                
                # If no text found or very little text, try OCR
                if not text.strip() or len(text.strip()) < 50:
                    logger.info(f"Page {page_num + 1} has minimal text ({len(text.strip())} chars), attempting enhanced extraction")
                    
                    # Try different PyMuPDF extraction methods first
                    if not text.strip():
                        # Try extracting from text blocks
                        blocks = page.get_text("blocks")
                        text = "\n".join([block[4] for block in blocks if len(block) > 4])
                        if text.strip():
                            extraction_method = "pymupdf_blocks"
                    
                    # If still no text and OCR is available, perform true OCR
                    if (not text.strip() or len(text.strip()) < 50) and OCR_AVAILABLE:
                        logger.info(f"Performing Tesseract OCR on page {page_num + 1}")
                        ocr_text = self._perform_ocr_on_page(page, page_num + 1, str(pdf_path))
                        if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                            text = ocr_text
                            extraction_method = "tesseract_ocr"
                    
                    elif not text.strip() and not OCR_AVAILABLE:
                        logger.warning(f"Page {page_num + 1} has no text and OCR not available. Install pytesseract and Tesseract for image OCR.")
                
                if text.strip():
                    # Create Document object for this page
                    page_doc = Document(
                        page_content=text,
                        metadata={
                            "page": page_num + 1,
                            "source": str(pdf_path),
                            "extraction_method": extraction_method
                        }
                    )
                    pages.append(page_doc)
            
            doc.close()

            if not pages:
                log_document_processing_complete(
                    context=context,
                    chunks_created=0,
                    processing_time_seconds=time.time() - start_time,
                    status="success_empty",
                )
                return []

            # Initialize the text splitter with optimized parameters
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""],
            )

            # Split documents and enhance metadata
            documents = text_splitter.split_documents(pages)

            # Enhance metadata with processing information
            base_metadata = self.get_metadata_template(pdf_path)
            for i, doc in enumerate(documents):
                # Preserve original page metadata and add our enhancements
                doc.metadata.update(base_metadata)
                doc.metadata.update(
                    {
                        "chunk_id": f"chunk_{i}",
                        "document_id": f"{pdf_path.stem}_pdf",
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "splitting_method": "RecursiveCharacterTextSplitter",
                        "total_chunks": len(documents),
                        "loader_type": "PyMuPDF_OCR"
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
                context=context, error=e, error_type="pdf_processing_error"
            )
            raise Exception(f"Error processing PDF {pdf_path}: {e!s}")

    def _perform_ocr_on_page(self, page, page_num: int, pdf_path: str) -> str:
        """
        Perform Tesseract OCR on a PDF page.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-based)
            pdf_path: Path to the PDF file being processed
            
        Returns:
            str: OCR-extracted text
        """
        if not OCR_AVAILABLE:
            return ""
            
        try:
            # Convert page to image (300 DPI for good OCR quality)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x scaling = ~300 DPI
            img_data = pix.pil_tobytes(format="PNG")
            
            # Convert to PIL Image
            img = Image.open(BytesIO(img_data))
            
            # Perform OCR with Tesseract
            # Use optimal OCR settings for document text
            custom_config = r'--oem 3 --psm 6'
            ocr_text = pytesseract.image_to_string(img, config=custom_config)
            
            # Clean up
            pix = None
            
            ocr_result = ocr_text.strip()
            
            # Write OCR investigation files if enabled
            self._write_ocr_investigation_file(ocr_result, page_num, pdf_path)
            
            return ocr_result
            
        except Exception as e:
            logger.warning(f"OCR failed on page: {e}")
            return ""
    
    def _write_ocr_investigation_file(self, ocr_result: str, page_num: int, pdf_path: str) -> None:
        """
        Write OCR results to temporary files for investigation when OCR_INVESTIGATE=true.
        
        Args:
            ocr_result: Text extracted from OCR
            page_num: Page number (1-based)
            pdf_path: Path to the PDF file being processed
        """
        import os
        from pathlib import Path
        
        # Only write files if OCR_INVESTIGATE is enabled
        if os.getenv('OCR_INVESTIGATE', 'false').lower() != 'true':
            return
            
        try:
            # Get OCR investigation directory from environment variable
            ocr_dir = os.getenv('OCR_INVESTIGATE_DIR', './ocr_debug')
            
            # Create directory if it doesn't exist
            Path(ocr_dir).mkdir(parents=True, exist_ok=True)
            
            # Create a safe filename from PDF path
            pdf_name = Path(pdf_path).stem
            safe_pdf_name = "".join(c for c in pdf_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create investigation filename with full path
            debug_filename = Path(ocr_dir) / f"ocr_investigation_{safe_pdf_name}_page_{page_num}.txt"
            
            # Write OCR results to file
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(f"OCR Investigation Results\n")
                f.write(f"========================\n\n")
                f.write(f"PDF File: {pdf_path}\n")
                f.write(f"Page Number: {page_num}\n")
                f.write(f"OCR Result Length: {len(ocr_result)} characters\n")
                f.write(f"OCR Result Empty: {'Yes' if not ocr_result else 'No'}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if ocr_result:
                    f.write(f"OCR Text Preview (first 300 chars):\n")
                    f.write(f"{'=' * 40}\n")
                    f.write(f"{ocr_result[:300]}\n")
                    if len(ocr_result) > 300:
                        f.write(f"... (truncated, see full text below)\n")
                    
                    f.write(f"\n\nFull OCR Text:\n")
                    f.write(f"{'=' * 40}\n")
                    f.write(ocr_result)
                else:
                    f.write("OCR returned no text for this page.\n")
                    
            logger.info(f"OCR investigation file written: {debug_filename}")
            
        except Exception as e:
            logger.warning(f"Failed to write OCR investigation file for page {page_num}: {e}")

    # Legacy method for backward compatibility
    def pdf_to_documents_recursive(
        self, pdf_path: Path, chunk_size: int = None, chunk_overlap: int = None
    ) -> list[Document]:
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
