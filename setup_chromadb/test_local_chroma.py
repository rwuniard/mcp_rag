#!/usr/bin/env python3
"""
Local ChromaDB Analysis Tool for MCP RAG Project

This script analyzes the persistent ChromaDB databases used by your MCP RAG project
to check for Word documents and other stored content.
"""

import sys

from collections import defaultdict
from pathlib import Path

import chromadb


def analyze_database(db_path: Path, db_name: str):
    """Analyze a specific ChromaDB database."""
    print(f"\n{'=' * 60}")
    print(f"🔍 Analyzing {db_name} Database")
    print(f"📁 Path: {db_path}")
    print(f"{'=' * 60}")

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return None

    try:
        # Connect to persistent ChromaDB
        client = chromadb.PersistentClient(path=str(db_path))

        # Get all collections
        collections = client.list_collections()

        if not collections:
            print("📭 No collections found in this database")
            return None

        print(f"📚 Found {len(collections)} collection(s):")

        total_docs = 0
        word_docs = 0
        file_types = defaultdict(int)

        for collection in collections:
            print(f"\n📁 Collection: {collection.name}")
            print(f"   🆔 ID: {collection.id}")

            count = collection.count()
            total_docs += count
            print(f"   📊 Documents: {count}")

            if count == 0:
                print("   📭 Empty collection")
                continue

            # Get all documents to analyze
            try:
                # Get documents in batches to avoid memory issues
                batch_size = 100
                all_documents = []
                offset = 0

                while offset < count:
                    current_batch = min(batch_size, count - offset)
                    batch = collection.get(
                        include=["documents", "metadatas"],
                        limit=current_batch,
                        offset=offset,
                    )

                    if batch["documents"]:
                        for i, doc in enumerate(batch["documents"]):
                            metadata = (
                                batch["metadatas"][i]
                                if batch["metadatas"] and i < len(batch["metadatas"])
                                else {}
                            )
                            all_documents.append({"content": doc, "metadata": metadata})

                    offset += current_batch

                # Analyze documents
                word_count = 0
                pdf_count = 0
                text_count = 0
                other_count = 0

                sources = set()
                processors = set()

                for doc_data in all_documents:
                    metadata = doc_data["metadata"] or {}

                    # Track file types
                    source = metadata.get("source", "")
                    if source:
                        sources.add(source)

                        # Determine file type
                        if source.lower().endswith((".docx", ".doc")):
                            word_count += 1
                            file_types["Word"] += 1
                        elif source.lower().endswith(".pdf"):
                            pdf_count += 1
                            file_types["PDF"] += 1
                        elif source.lower().endswith((".txt", ".md")):
                            text_count += 1
                            file_types["Text"] += 1
                        else:
                            other_count += 1
                            file_types["Other"] += 1

                    # Track processors used
                    proc_name = metadata.get("processor_name", "")
                    if proc_name:
                        processors.add(proc_name)

                # Report findings
                print("   📄 Document Types:")
                if word_count > 0:
                    print(f"      📝 Word documents: {word_count}")
                    word_docs += word_count
                if pdf_count > 0:
                    print(f"      📄 PDF documents: {pdf_count}")
                if text_count > 0:
                    print(f"      📃 Text documents: {text_count}")
                if other_count > 0:
                    print(f"      📋 Other documents: {other_count}")

                if sources:
                    print("   📂 Source files found:")
                    for source in sorted(sources):
                        file_ext = Path(source).suffix.lower()
                        if file_ext in [".docx", ".doc"]:
                            print(f"      📝 {source}")
                        elif file_ext == ".pdf":
                            print(f"      📄 {source}")
                        else:
                            print(f"      📃 {source}")

                if processors:
                    print(f"   🔧 Processors used: {', '.join(sorted(processors))}")

                # Show sample Word document if found
                if word_count > 0:
                    print("\n   📝 Sample Word Document Content:")
                    for doc_data in all_documents[:3]:  # Show first 3
                        metadata = doc_data["metadata"] or {}
                        source = metadata.get("source", "")
                        if source.lower().endswith((".docx", ".doc")):
                            content_preview = (
                                doc_data["content"][:200] + "..."
                                if len(doc_data["content"]) > 200
                                else doc_data["content"]
                            )
                            print(f"      Source: {source}")
                            print(f"      Content: {content_preview}")
                            print(f"      Metadata: {metadata}")
                            print()
                            break

            except Exception as e:
                print(f"   ❌ Error analyzing collection: {e}")

        # Summary
        print("\n📊 Database Summary:")
        print(f"   📚 Total collections: {len(collections)}")
        print(f"   📄 Total documents: {total_docs}")
        print(f"   📝 Word documents: {word_docs}")

        if file_types:
            print("   📋 File type breakdown:")
            for file_type, count in file_types.items():
                print(f"      {file_type}: {count}")

        return total_docs, word_docs, file_types

    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return 0, 0, {}


def analyze_database_safe(db_path: Path, db_name: str):
    """Safely analyze a database, handling missing databases."""
    if not db_path.exists():
        print(f"\n{'=' * 60}")
        print(f"🔍 Analyzing {db_name} Database")
        print(f"📁 Path: {db_path}")
        print(f"{'=' * 60}")
        print(f"❌ Database not found: {db_path}")
        return 0, 0, {}

    return analyze_database(db_path, db_name)


def check_data_directory():
    """Check what's in the data source directory."""
    print(f"\n{'=' * 60}")
    print("📂 Checking Data Source Directory")
    print(f"{'=' * 60}")

    # Check for documents in the data source directory
    project_root = Path(__file__).parent
    data_source_dir = project_root / "src" / "rag_store" / "data_source"

    print(f"📁 Data source directory: {data_source_dir}")

    if not data_source_dir.exists():
        print("❌ Data source directory not found")
        return None

    # List all files
    files = list(data_source_dir.glob("*"))
    if not files:
        print("📭 No files found in data source directory")
        return None

    print(f"📋 Files in data source directory ({len(files)} found):")

    word_files = []
    pdf_files = []
    text_files = []
    other_files = []

    for file_path in files:
        if file_path.is_file():
            ext = file_path.suffix.lower()
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)

            if ext in [".docx", ".doc"]:
                word_files.append((file_path.name, size_mb))
                print(f"   📝 {file_path.name} ({size_mb:.2f} MB)")
            elif ext == ".pdf":
                pdf_files.append((file_path.name, size_mb))
                print(f"   📄 {file_path.name} ({size_mb:.2f} MB)")
            elif ext in [".txt", ".md"]:
                text_files.append((file_path.name, size_mb))
                print(f"   📃 {file_path.name} ({size_mb:.2f} MB)")
            else:
                other_files.append((file_path.name, size_mb))
                print(f"   📋 {file_path.name} ({size_mb:.2f} MB)")

    print("\n📊 File Summary:")
    if word_files:
        print(f"   📝 Word files: {len(word_files)}")
    if pdf_files:
        print(f"   📄 PDF files: {len(pdf_files)}")
    if text_files:
        print(f"   📃 Text files: {len(text_files)}")
    if other_files:
        print(f"   📋 Other files: {len(other_files)}")

    return word_files, pdf_files, text_files, other_files


def main():
    """Main analysis function."""
    print("🚀 MCP RAG Local ChromaDB Analysis")
    print("=" * 60)
    print("Analyzing persistent ChromaDB databases used by your MCP RAG project")

    project_root = Path(__file__).parent
    data_dir = project_root / "data"

    print(f"\n📁 Project root: {project_root}")
    print(f"📁 Data directory: {data_dir}")

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("💡 Have you run the document storage process yet?")
        print("   Try running: python main.py store")
        sys.exit(1)

    # Check what files are available to process
    word_files, pdf_files, text_files, other_files = check_data_directory()

    # Analyze Google embeddings database
    google_db_path = data_dir / "chroma_db_google"
    google_total, google_word, google_types = analyze_database_safe(
        google_db_path, "Google Embeddings"
    )

    # Analyze OpenAI embeddings database
    openai_db_path = data_dir / "chroma_db_openai"
    openai_total, openai_word, openai_types = analyze_database_safe(
        openai_db_path, "OpenAI Embeddings"
    )

    # Final summary
    print(f"\n{'=' * 60}")
    print("🎯 FINAL ANALYSIS SUMMARY")
    print(f"{'=' * 60}")

    total_docs = google_total + openai_total
    total_word_docs = google_word + openai_word

    print("📂 Source Files Available:")
    if word_files:
        print(f"   📝 Word files ready for processing: {len(word_files)}")
        for name, size in word_files:
            print(f"      • {name} ({size:.2f} MB)")
    else:
        print("   📝 No Word files found in data_source directory")

    print("\n💾 Stored in ChromaDB:")
    print(f"   📄 Total documents: {total_docs}")
    print(f"   📝 Word documents: {total_word_docs}")

    if total_word_docs == 0 and word_files:
        print("\n⚠️  ISSUE DETECTED:")
        print("   📝 Word files are available but not stored in ChromaDB")
        print("   💡 Try running the storage process:")
        print("      python main.py store")
        print("   💡 Or run directly:")
        print("      python src/rag_store/store_embeddings.py")
    elif total_word_docs > 0:
        print("\n✅ SUCCESS:")
        print("   📝 Word documents are successfully stored in ChromaDB!")
        print("   🔍 You can now search them using:")
        print('      python main.py search "your query about word content"')
    elif not word_files and total_word_docs == 0:
        print("\n📝 TO ADD WORD DOCUMENTS:")
        print("   1. Place .docx or .doc files in: src/rag_store/data_source/")
        print("   2. Run: python main.py store")
        print('   3. Search: python main.py search "your query"')


if __name__ == "__main__":
    main()
