#!/usr/bin/env python3
"""
Store only Word documents to test end-to-end functionality
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "rag_store"))

from store_embeddings import main as store_main
from document_processor import DocumentRegistry

def store_word_documents_only():
    """Store only Word documents for testing."""
    
    # Override the data source directory to include only Word files
    data_source_dir = Path(__file__).parent / "src" / "rag_store" / "data_source"
    
    # Find Word documents only
    word_files = []
    for pattern in ["*.doc", "*.docx", "*.DOC", "*.DOCX"]:
        word_files.extend(data_source_dir.glob(pattern))
    
    # Filter out temp files
    word_files = [f for f in word_files if not f.name.startswith("~$")]
    
    print(f"📄 Found {len(word_files)} Word documents:")
    for f in word_files:
        print(f"   - {f.name} ({f.stat().st_size} bytes)")
    
    if not word_files:
        print("❌ No Word documents found!")
        return False
    
    # Create a temporary test by copying just one Word file
    test_dir = Path(__file__).parent / "temp_word_test"
    test_dir.mkdir(exist_ok=True)
    
    # Copy one Word file for testing
    import shutil
    test_file = test_dir / word_files[0].name
    shutil.copy(word_files[0], test_file)
    
    print(f"\n🔄 Processing Word document: {test_file.name}")
    
    # Temporarily override data source directory
    import os
    original_cwd = os.getcwd()
    
    try:
        # Change to the rag_store directory
        os.chdir(Path(__file__).parent / "src" / "rag_store")
        
        # Override data source path temporarily
        import store_embeddings
        store_embeddings.DATA_SOURCE_DIR = test_dir
        
        # Run the store process
        store_main()
        
        return True
        
    except Exception as e:
        print(f"❌ Error storing Word documents: {e}")
        return False
        
    finally:
        os.chdir(original_cwd)
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    success = store_word_documents_only()
    sys.exit(0 if success else 1)