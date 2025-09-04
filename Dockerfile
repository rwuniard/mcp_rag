# Multi-stage build for RAG Fetch MCP Server
FROM python:3.12-slim as base

# Build arguments for version information
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_BRANCH=main
ARG VERSION

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Labels for container metadata and version tracking
LABEL maintainer="RAG Fetch Team" \
      description="RAG Fetch MCP Server - Semantic document search with ChromaDB" \
      version="${VERSION}" \
      git.commit="${GIT_COMMIT}" \
      git.branch="${GIT_BRANCH}" \
      build.date="${BUILD_DATE}" \
      org.opencontainers.image.title="rag-fetch-mcp-server" \
      org.opencontainers.image.description="RAG Fetch MCP Server for semantic document search" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.source="https://github.com/your-org/mcp_rag"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r ragfetch && useradd -r -g ragfetch -s /bin/bash ragfetch

# ====================================================================
# Build stage - Install dependencies and build the package
# ====================================================================
FROM base as builder

WORKDIR /app

# Copy package configuration
COPY pyproject.toml ./
COPY README.md ./

# Copy source code
COPY src/ ./src/

# Install build dependencies and package in development mode
RUN pip install --no-cache-dir -e .[dev] \
    && pip install --no-cache-dir build wheel

# Build wheel for production
RUN python -m build --wheel

# ====================================================================
# Production stage - Minimal runtime image
# ====================================================================
FROM base as production

WORKDIR /app

# Copy built wheel from builder stage
COPY --from=builder /app/dist/*.whl /tmp/

# Install the package and runtime dependencies only
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl /root/.cache/pip

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs \
    && chown -R ragfetch:ragfetch /app

# Copy environment template
COPY src/rag_fetch/.env_template /app/.env_template

# Switch to non-root user
USER ragfetch

# Expose the default MCP server port
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Default environment variables (can be overridden)
ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=8080 \
    MCP_TRANSPORT=http \
    CHROMADB_HOST=chromadb \
    CHROMADB_PORT=8000

# Entry point script (supports both CLI and server modes)
CMD ["rag-mcp-server"]

# ====================================================================
# Development stage - For development with hot reload
# ====================================================================
FROM base as development

WORKDIR /app

# Install development dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[dev]

# Copy source code (will be mounted as volume in dev)
COPY src/ ./src/

# Switch to non-root user
USER ragfetch

# Development command with hot reload
CMD ["python", "-m", "rag_fetch.mcp_server"]