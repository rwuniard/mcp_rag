"""
PDF Processing Module for RAG System

This module provides functionality to extract text from PDF files and convert
them into LangChain Document objects for embedding storage.
"""

from pathlib import Path
from typing import List

from langchain.schema import Document
from pypdf import PdfReader


class PDFProcessor:
    """Process PDF files and extract text content for RAG storage."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf'}
    
    def is_pdf_file(self, file_path: Path) -> bool:
        """Check if the file is a supported PDF file."""
        return file_path.suffix.lower() in self.supported_extensions
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF processing fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = PdfReader(str(pdf_path))
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    # Add page marker for better organization
                    text_content.append(f"[Page {page_num}]\n{page_text}")
            
            if not text_content:
                raise Exception(f"No text content extracted from PDF: {pdf_path}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise Exception(f"Failed to process PDF {pdf_path}: {str(e)}")
    
    def pdf_to_documents(self, pdf_path: Path, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """
        Convert PDF file to LangChain Document objects with chunking.
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            
        Returns:
            List of LangChain Document objects
        """
        # Extract full text from PDF
        full_text = self.extract_text_from_pdf(pdf_path)
        
        # Simple text chunking (can be enhanced with LangChain's text splitters)
        chunks = self._chunk_text(full_text, chunk_size, chunk_overlap)
        
        # Create Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": str(pdf_path),
                    "chunk_id": i,
                    "document_id": pdf_path.stem,
                    "file_type": "pdf",
                    "total_chunks": len(chunks)
                }
            )
            documents.append(doc)
        
        return documents
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:  # Only if we find a reasonable break point
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap
            if start <= 0:
                start = end
        
        return chunks
    
    def process_pdf_directory(self, directory_path: Path, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
            
        Returns:
            List of all Document objects from all PDFs
        """
        all_documents = []
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        pdf_files = [f for f in directory_path.iterdir() if self.is_pdf_file(f)]
        
        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return all_documents
        
        print(f"Processing {len(pdf_files)} PDF files...")
        
        for pdf_file in pdf_files:
            try:
                print(f"Processing: {pdf_file.name}")
                documents = self.pdf_to_documents(pdf_file, chunk_size, chunk_overlap)
                all_documents.extend(documents)
                print(f"  ✓ Extracted {len(documents)} chunks")
            except Exception as e:
                print(f"  ✗ Error processing {pdf_file.name}: {e}")
        
        return all_documents


def main():
    """Example usage of PDF processor."""
    processor = PDFProcessor()
    
    # Example: Process a single PDF file
    pdf_path = Path("sample.pdf")
    if pdf_path.exists():
        try:
            documents = processor.pdf_to_documents(pdf_path)
            print(f"Processed {pdf_path.name}: {len(documents)} chunks")
            
            # Show first chunk as example
            if documents:
                print("\nFirst chunk preview:")
                print(f"Content: {documents[0].page_content[:200]}...")
                print(f"Metadata: {documents[0].metadata}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No sample.pdf found. Place a PDF file in the current directory to test.")


if __name__ == "__main__":
    main()