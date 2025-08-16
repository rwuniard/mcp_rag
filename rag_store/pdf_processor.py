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
from pypdf import PdfReader


class PDFProcessor:
    """Process PDF files and extract text content for RAG storage."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf'}
        # Optimized chunking parameters based on industry best practices (2024)
        self.default_pdf_chunk_size = 1800  # Technical content benefits from larger context
        self.default_pdf_overlap = 270      # 15% overlap ratio
        self.default_text_chunk_size = 1200 # Mixed factual content
        self.default_text_overlap = 200     # ~17% overlap ratio
    
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
    
    def pdf_to_documents(self, pdf_path: Path, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        """
        Convert PDF file to LangChain Document objects with optimized chunking.
        
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
                    "total_chunks": len(chunks),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap
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
    
    def compare_splitting_methods(self, pdf_path: Path) -> dict:
        """
        Compare custom vs recursive text splitting methods.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with comparison results
        """
        print(f"Comparing splitting methods for {pdf_path.name}...")
        
        # Test custom method
        try:
            custom_docs = self.pdf_to_documents(pdf_path)
            custom_chunks = len(custom_docs)
            custom_avg_length = sum(len(doc.page_content) for doc in custom_docs) / len(custom_docs)
        except Exception as e:
            custom_chunks = 0
            custom_avg_length = 0
            print(f"Custom method failed: {e}")
        
        # Test recursive method
        try:
            recursive_docs = self.pdf_to_documents_recursive(pdf_path)
            recursive_chunks = len(recursive_docs)
            recursive_avg_length = sum(len(doc.page_content) for doc in recursive_docs) / len(recursive_docs)
        except Exception as e:
            recursive_chunks = 0
            recursive_avg_length = 0
            print(f"Recursive method failed: {e}")
        
        results = {
            "pdf_file": str(pdf_path),
            "custom_method": {
                "chunks": custom_chunks,
                "avg_chunk_length": round(custom_avg_length, 1),
                "method": "custom_chunking"
            },
            "recursive_method": {
                "chunks": recursive_chunks,
                "avg_chunk_length": round(recursive_avg_length, 1),
                "method": "recursive_text_splitter"
            },
            "recommendation": "recursive" if recursive_chunks > 0 else "custom"
        }
        
        print(f"Custom method: {custom_chunks} chunks, avg length: {custom_avg_length:.1f}")
        print(f"Recursive method: {recursive_chunks} chunks, avg length: {recursive_avg_length:.1f}")
        
        return results
    
    def process_pdf_directory(self, directory_path: Path, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        """
        Process all PDF files in a directory with optimized chunking.
        
        Args:
            directory_path: Path to directory containing PDF files
            chunk_size: Maximum size of each text chunk (defaults to optimized PDF chunk size)
            chunk_overlap: Number of characters to overlap between chunks (defaults to optimized overlap)
            
        Returns:
            List of all Document objects from all PDFs
        """
        # Use optimized defaults if not specified
        if chunk_size is None:
            chunk_size = self.default_pdf_chunk_size
        if chunk_overlap is None:
            chunk_overlap = self.default_pdf_overlap
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
    """Example usage and comparison of PDF processor methods."""
    processor = PDFProcessor()
    
    # Look for PDF files to test
    test_files = ["thinkpython.pdf", "sample.pdf"]
    pdf_found = False
    
    for filename in test_files:
        pdf_path = Path(filename)
        if pdf_path.exists():
            pdf_found = True
            print(f"\n{'='*60}")
            print(f"Testing with {pdf_path.name}")
            print(f"{'='*60}")
            
            try:
                # Compare both methods
                comparison = processor.compare_splitting_methods(pdf_path)
                
                print(f"\n📊 Comparison Results:")
                print(f"Custom Method: {comparison['custom_method']['chunks']} chunks")
                print(f"Recursive Method: {comparison['recursive_method']['chunks']} chunks")
                print(f"Recommended: {comparison['recommendation']} method")
                
                # Show sample chunks from each method
                print(f"\n📄 Sample chunks:")
                
                # Custom method sample
                custom_docs = processor.pdf_to_documents(pdf_path)
                if custom_docs:
                    print(f"\nCustom method - First chunk:")
                    print(f"Length: {len(custom_docs[0].page_content)} chars")
                    print(f"Content: {custom_docs[0].page_content[:300]}...")
                
                # Recursive method sample  
                recursive_docs = processor.pdf_to_documents_recursive(pdf_path)
                if recursive_docs:
                    print(f"\nRecursive method - First chunk:")
                    print(f"Length: {len(recursive_docs[0].page_content)} chars")
                    print(f"Content: {recursive_docs[0].page_content[:300]}...")
                
            except Exception as e:
                print(f"Error testing {pdf_path.name}: {e}")
    
    if not pdf_found:
        print("No test PDF files found. Place a PDF file (like thinkpython.pdf) in the current directory to test.")
        print("Available methods:")
        print("- pdf_to_documents(): Custom chunking with optimized parameters")
        print("- pdf_to_documents_recursive(): RecursiveCharacterTextSplitter with LangChain integration")


if __name__ == "__main__":
    main()