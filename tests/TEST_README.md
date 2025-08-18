# Testing Guide

This document describes how to run tests for the MCP RAG project.

## Running Tests

### Option 1: Using the test runner script
```bash
python run_tests.py
```

### Option 2: Using unittest directly
```bash
python -m unittest test_pdf_processor.py -v
```

### Option 3: Running a specific test
```bash
python -m unittest test_pdf_processor.TestPDFProcessor.test_is_pdf_file_valid_pdf -v
```

## Test Coverage

The `test_pdf_processor.py` file provides comprehensive unit tests for the `PDFProcessor` class:

### Unit Tests (`TestPDFProcessor`)
- ✅ **Initialization**: Tests default values and configuration
- ✅ **File validation**: Tests PDF file extension detection
- ✅ **Document processing**: Tests the main `pdf_to_documents_recursive` method
- ✅ **Parameter handling**: Tests default and custom chunk size/overlap parameters
- ✅ **Error handling**: Tests exception propagation and edge cases
- ✅ **Metadata generation**: Tests document metadata creation and formatting
- ✅ **Chunk numbering**: Tests sequential chunk ID assignment

### Integration Tests (`TestPDFProcessorIntegration`)
- ✅ **Real PDF processing**: Tests with actual PDF file if available (`thinkpython.pdf`)
- ✅ **End-to-end validation**: Validates complete processing pipeline

## Test Structure

```
mcp_rag/
├── test_pdf_processor.py          # Main unit tests
├── run_tests.py                   # Test runner script
├── rag_store/
│   ├── pdf_processor.py           # Code under test
│   └── experimental_chunking_comparison.py  # Experimental comparison tool
└── TEST_README.md                 # This file
```

## Adding New Tests

When adding new functionality to `PDFProcessor`, follow these guidelines:

1. **Unit Tests**: Mock external dependencies (PyPDFLoader, file system)
2. **Integration Tests**: Test with real files when available
3. **Edge Cases**: Test error conditions and boundary cases
4. **Naming Convention**: Use descriptive test method names starting with `test_`

### Example Test Method
```python
def test_new_functionality(self):
    """Test description explaining what this test validates."""
    # Arrange
    processor = PDFProcessor()
    
    # Act
    result = processor.new_method()
    
    # Assert
    self.assertEqual(result, expected_value)
```

## Test Results

When all tests pass, you should see:
```
✅ All tests passed!

----------------------------------------------------------------------
Ran 11 tests in X.XXXs

OK
```

The integration test will also show:
```
Running integration test with thinkpython.pdf
✓ Successfully processed XXX chunks from thinkpython.pdf
```