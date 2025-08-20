#!/usr/bin/env python3
"""
Check if Word documents are stored in ChromaDB
"""

import sys

from pathlib import Path

import chromadb

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "rag_fetch"))

from search_similarity import ModelVendor, ensure_chroma_directory


def check_word_documents():
    """Check for Word documents in the database."""

    # Get database path
    db_path = ensure_chroma_directory(ModelVendor.GOOGLE)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=str(db_path))

    # Get the collection (try both possible names)
    try:
        collection = client.get_collection(name="knowledge_base")
    except:
        try:
            collection = client.get_collection(name="documents")
        except:
            collections = client.list_collections()
            if collections:
                collection = collections[0]
                print(f"Using collection: {collection.name}")
            else:
                print("No collections found!")
                return False

    # Get all documents
    all_docs = collection.get()

    print(f"📊 Total documents in database: {len(all_docs['ids'])}")

    # Count by file type
    doc_types = {}
    word_docs = []

    for i, metadata in enumerate(all_docs["metadatas"]):
        source = metadata.get("source", "unknown")
        file_type = metadata.get("file_type", "unknown")

        if file_type not in doc_types:
            doc_types[file_type] = 0
        doc_types[file_type] += 1

        # Track Word documents
        if file_type.lower() in [".doc", ".docx"] or source.lower().endswith(
            (".doc", ".docx")
        ):
            word_docs.append(
                {"source": source, "file_type": file_type, "id": all_docs["ids"][i]}
            )

    print("\n📁 Documents by file type:")
    for file_type, count in sorted(doc_types.items()):
        print(f"   {file_type}: {count} chunks")

    print(f"\n📄 Word documents found: {len(word_docs)}")
    for doc in word_docs:
        print(f"   - {doc['source']} ({doc['file_type']})")

    return len(word_docs) > 0


if __name__ == "__main__":
    has_word_docs = check_word_documents()
    if has_word_docs:
        print("\n✅ Word documents are present in the database!")
    else:
        print("\n❌ No Word documents found in the database.")

    sys.exit(0 if has_word_docs else 1)
