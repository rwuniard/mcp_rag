"""
Centralized logging configuration for RAG Store service.

Provides structured logging with JSON output and basic metrics collection.
"""

import structlog
import logging
import sys
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge

# Configure standard library logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Configure structlog for structured JSON logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Get logger instance
logger = structlog.get_logger("rag_store")

# Prometheus Metrics for Document Processing
METRICS = {
    # Counters
    'documents_processed_total': Counter(
        'rag_documents_processed_total',
        'Total number of documents processed',
        ['processor_type', 'file_type', 'status']
    ),
    'chunks_created_total': Counter(
        'rag_chunks_created_total', 
        'Total number of chunks created',
        ['processor_type', 'file_type']
    ),
    'processing_errors_total': Counter(
        'rag_processing_errors_total',
        'Total number of processing errors',
        ['processor_type', 'error_type']
    ),
    
    # Histograms
    'document_processing_duration_seconds': Histogram(
        'rag_document_processing_duration_seconds',
        'Time spent processing documents',
        ['processor_type', 'file_type'],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    ),
    'document_size_bytes': Histogram(
        'rag_document_size_bytes',
        'Size of processed documents in bytes',
        ['processor_type', 'file_type'],
        buckets=[1000, 10000, 100000, 1000000, 10000000, 100000000]
    ),
    
    # Gauges
    'active_processors': Gauge(
        'rag_active_processors',
        'Number of active document processors',
        ['processor_type']
    )
}

def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (defaults to rag_store)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name or "rag_store")

def log_document_processing_start(
    processor_name: str,
    file_path: str,
    file_size: int,
    file_type: str
) -> Dict[str, Any]:
    """
    Log the start of document processing and return context for completion logging.
    
    Args:
        processor_name: Name of the processor
        file_path: Path to the file being processed
        file_size: Size of the file in bytes
        file_type: File extension
        
    Returns:
        Context dictionary for completion logging
    """
    context = {
        'processor_name': processor_name,
        'file_path': file_path,
        'file_size': file_size,
        'file_type': file_type,
        'operation': 'document_processing'
    }
    
    logger.info(
        "Document processing started",
        **context
    )
    
    # Update metrics
    METRICS['active_processors'].labels(processor_type=processor_name).inc()
    
    return context

def log_document_processing_complete(
    context: Dict[str, Any],
    chunks_created: int,
    processing_time_seconds: float,
    status: str = "success"
):
    """
    Log the completion of document processing.
    
    Args:
        context: Context from log_document_processing_start
        chunks_created: Number of chunks created
        processing_time_seconds: Processing time in seconds
        status: Processing status (success/error)
    """
    processor_name = context['processor_name']
    file_type = context['file_type']
    file_size = context['file_size']
    
    logger.info(
        "Document processing completed",
        chunks_created=chunks_created,
        processing_time_seconds=processing_time_seconds,
        status=status,
        **context
    )
    
    # Update metrics
    METRICS['documents_processed_total'].labels(
        processor_type=processor_name,
        file_type=file_type,
        status=status
    ).inc()
    
    METRICS['chunks_created_total'].labels(
        processor_type=processor_name,
        file_type=file_type
    ).inc(chunks_created)
    
    METRICS['document_processing_duration_seconds'].labels(
        processor_type=processor_name,
        file_type=file_type
    ).observe(processing_time_seconds)
    
    METRICS['document_size_bytes'].labels(
        processor_type=processor_name,
        file_type=file_type
    ).observe(file_size)
    
    METRICS['active_processors'].labels(processor_type=processor_name).dec()

def log_processing_error(
    context: Dict[str, Any],
    error: Exception,
    error_type: str = "unknown"
):
    """
    Log a processing error.
    
    Args:
        context: Context from log_document_processing_start
        error: The exception that occurred
        error_type: Type of error for metrics
    """
    processor_name = context['processor_name']
    
    logger.error(
        "Document processing failed",
        error=str(error),
        error_type=error_type,
        **context
    )
    
    # Update metrics
    METRICS['processing_errors_total'].labels(
        processor_type=processor_name,
        error_type=error_type
    ).inc()
    
    METRICS['active_processors'].labels(processor_type=processor_name).dec()

def log_registry_operation(operation: str, **kwargs):
    """
    Log registry operations.
    
    Args:
        operation: Type of operation (register, lookup, process)
        **kwargs: Additional context
    """
    logger.info(
        f"Registry operation: {operation}",
        operation=operation,
        **kwargs
    )

def get_metrics_registry():
    """
    Get the metrics registry for Prometheus integration.
    
    Returns:
        Dictionary of Prometheus metrics
    """
    return METRICS