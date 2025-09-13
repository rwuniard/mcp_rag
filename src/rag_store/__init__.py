"""
RAG Store - Document Ingestion Service

Independent service for processing and storing documents with embeddings.
Can be deployed separately from the search service.
"""

from .pdf_processor import PDFProcessor
from .store_embeddings import ModelVendor, load_embedding_model, store_to_chroma
from ._version import __version__

__all__ = ["ModelVendor", "PDFProcessor", "load_embedding_model", "store_to_chroma", "__version__"]
