"""
RAG Store - Document Ingestion Service

Independent service for processing and storing documents with embeddings.
Can be deployed separately from the search service.
"""

from .pdf_processor import PDFProcessor
from .store_embeddings import store_to_chroma, load_embedding_model, ModelVendor

__version__ = "0.1.0"
__all__ = ["PDFProcessor", "store_to_chroma", "load_embedding_model", "ModelVendor"]