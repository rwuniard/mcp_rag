# Testing Guide

This document describes how to run tests for the MCP RAG project.

## Running Tests

### Option 1: Run all tests (Recommended)
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html
```

### Option 2: Run specific test modules
```bash
# Run MCP server tests
uv run pytest tests/test_rag_fetch/test_mcp_server_http.py -v

# Run document processing tests  
uv run pytest tests/test_rag_store/test_pdf_processor.py -v

# Run integration tests
uv run pytest tests/test_rag_fetch/test_mcp_integration.py -v
```

### Option 3: Run specific test cases
```bash
# Run a specific test class
uv run pytest tests/test_rag_store/test_pdf_processor.py::TestPDFProcessor -v

# Run a specific test method
uv run pytest tests/test_rag_store/test_pdf_processor.py::TestPDFProcessor::test_is_pdf_file_valid_pdf -v
```

### Option 4: Advanced coverage runners
```bash
# Full coverage with HTML report and browser opening
python run_coverage.py --open

# HTML-only coverage report
python run_html_coverage.py --open
```

## Test Coverage

### RAG Store Tests (`tests/test_rag_store/`)
- **Document Processing**: PDF, Word, MHT, text file processors
- **Embedding Generation**: OpenAI and Google embedding models
- **CLI Interface**: Command-line argument parsing and execution
- **Storage Operations**: ChromaDB integration and document storage

### RAG Fetch Tests (`tests/test_rag_fetch/`)
- **MCP Server**: HTTP transport, connection management, tools
- **Configuration**: Environment variables, transport settings
- **Integration**: End-to-end client-server communication
- **Stress Testing**: Concurrent connections and operations

## Test Structure

```
mcp_rag/
├── tests/
│   ├── test_rag_store/           # Document processing tests
│   │   ├── test_pdf_processor.py
│   │   ├── test_word_processor.py
│   │   ├── test_cli.py
│   │   └── test_store_embeddings.py
│   └── test_rag_fetch/           # MCP server tests
│       ├── test_mcp_server_http.py
│       └── test_mcp_integration.py
├── run_coverage.py               # Advanced coverage runner
├── run_html_coverage.py          # HTML-only coverage runner
├── test_embedding_isolation.py  # Debug isolation testing
└── TEST_README.md               # This file
```

## Test Configuration

The project uses `pytest.ini` for test configuration:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --tb=short -v
filterwarnings = ignore::DeprecationWarning
```

## Adding New Tests

Follow these guidelines when adding new tests:

1. **Use pytest**: All new tests should use pytest fixtures and conventions
2. **Mock external dependencies**: Use `unittest.mock.patch` for external services
3. **Test structure**: Follow Arrange-Act-Assert pattern
4. **Naming convention**: Use descriptive test method names starting with `test_`
5. **Test categories**: Separate unit tests from integration tests

### Example Pytest Test Method
```python
import pytest
from unittest.mock import patch

def test_new_functionality():
    """Test description explaining what this test validates."""
    # Arrange
    processor = PDFProcessor()
    
    # Act
    result = processor.new_method()
    
    # Assert
    assert result == expected_value

@patch('module.external_dependency')
def test_with_mocking(mock_dependency):
    """Test with mocked external dependency."""
    mock_dependency.return_value = "mocked_value"
    # ... test implementation
```

## Test Results

When all tests pass, you should see:
```
======================== test session starts ========================
collected 20 items

tests/test_rag_fetch/test_mcp_integration.py::TestMCPServerIntegration::test_connection_tracking PASSED [ 12%]
tests/test_rag_fetch/test_mcp_integration.py::TestMCPServerIntegration::test_error_handling PASSED [ 25%]
...

======================== 20 passed in 2.29s =========================
```

For coverage reports:
```bash
---------- coverage: platform darwin, python 3.12.8-final-0 ----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/rag_fetch/config.py                   85      2    98%   142-143
src/rag_fetch/mcp_server.py              120      8    93%   45-47, 125-127
...
TOTAL                                     850     45    95%
```

## Debugging Test Issues

### Environment Isolation Issues
Some embedding tests may fail in the full test suite due to environment variable loading. Use the isolation test script:
```bash
python test_embedding_isolation.py
```

### MCP Server Testing
- Unit tests use in-memory FastMCP transport
- Integration tests mock ChromaDB dependencies  
- No real HTTP servers are started during testing

### Coverage Analysis
- View detailed HTML coverage reports in `htmlcov/index.html`
- Focus on files with <85% coverage for improvement
- Use coverage to identify untested code paths