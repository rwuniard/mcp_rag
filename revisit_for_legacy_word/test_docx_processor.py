#!/usr/bin/env python3
"""
Test Word processor with .docx files only
"""

from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "rag_store"))

from word_processor import WordProcessor

def test_docx_processor():
    """Test processing a .docx file."""
    
    # Initialize the processor
    processor = WordProcessor()
    
    print(f"Supported extensions: {processor.supported_extensions}")
    print(f"File type description: {processor.file_type_description}")
    
    # Find .docx files in data_source
    data_source_dir = Path(__file__).parent / "src" / "rag_store" / "data_source"
    docx_files = list(data_source_dir.glob("*.docx"))
    
    if not docx_files:
        print("❌ No .docx files found in data_source directory")
        return False
    
    # Test with the first .docx file
    test_file = docx_files[0]
    print(f"🔄 Testing Word document processing with: {test_file.name}")
    print(f"📁 File size: {test_file.stat().st_size} bytes")
    print(f"📄 Is supported: {processor.is_supported_file(test_file)}")
    
    try:
        # Process the document
        print("🔄 Starting document processing...")
        documents = processor.process_document(test_file)
        
        print(f"✅ Success! Processed {len(documents)} chunks from {test_file.name}")
        
        if documents:
            print(f"\n📄 Sample content from first chunk:")
            print(f"   Content preview: {documents[0].page_content[:200]}...")
            print(f"   Metadata keys: {list(documents[0].metadata.keys())}")
            print(f"   Loader type: {documents[0].metadata.get('loader_type', 'unknown')}")
            print(f"   Supports legacy DOC: {documents[0].metadata.get('supports_legacy_doc', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {test_file.name}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_docx_processor()
    sys.exit(0 if success else 1)