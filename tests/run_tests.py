#!/usr/bin/env python3
"""
Test runner script for the MCP RAG project.

This script runs all unit tests using the proper Python package structure.
"""

import sys
import unittest
from pathlib import Path

def run_tests():
    """Discover and run all tests."""
    # Add the src directory to the Python path for imports
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Discover and run tests from the tests directory
    loader = unittest.TestLoader()
    tests_dir = Path(__file__).parent  # tests directory
    suite = loader.discover(str(tests_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)
    
    print("\n✅ All tests passed!")

if __name__ == '__main__':
    run_tests()