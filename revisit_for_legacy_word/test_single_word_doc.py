#!/usr/bin/env python3
"""
Test single Word document processing
"""

import sys

from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "rag_store"))

from word_processor import WordProcessor


def test_single_word_doc():
    """Test processing a single Word document."""

    # Initialize the processor
    processor = WordProcessor()

    # Find the first .DOC file in data_source
    data_source_dir = Path(__file__).parent / "src" / "rag_store" / "data_source"
    doc_files = [
        f for f in data_source_dir.glob("*.DOC") if not f.name.startswith("~$")
    ]

    if not doc_files:
        print("❌ No .DOC files found in data_source directory")
        return None

    # Test with the first .DOC file
    test_file = doc_files[0]
    print(f"🔄 Testing Word document processing with: {test_file.name}")
    print(f"📁 File size: {test_file.stat().st_size} bytes")

    try:
        # Process the document
        print("🔄 Starting document processing...")
        documents = processor.process_document(test_file)

        print(f"✅ Success! Processed {len(documents)} chunks from {test_file.name}")

        if documents:
            print("\n📄 Sample content from first chunk:")
            print(f"   Content preview: {documents[0].page_content[:200]}...")
            print(f"   Metadata: {documents[0].metadata}")

        return True

    except Exception as e:
        print(f"❌ Error processing {test_file.name}: {e!s}")
        return False


if __name__ == "__main__":
    success = test_single_word_doc()
    sys.exit(0 if success else 1)
