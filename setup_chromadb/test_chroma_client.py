#!/usr/bin/env python3
"""
ChromaDB Client Test Script for Docker Setup

This script connects to your ChromaDB Docker instance and displays information about
collections and documents. Works with the standard open-source ChromaDB Docker image.
"""

import chromadb
import sys

def test_docker_chromadb():
    """Test connection to ChromaDB running in Docker."""
    print("🐳 Testing ChromaDB Docker Instance")
    print("=" * 50)
    
    try:
        # Connect to ChromaDB running in Docker
        client = chromadb.HttpClient(host="localhost", port=8000)
        
        # Test connection with heartbeat
        heartbeat = client.heartbeat()
        print(f"✅ Successfully connected to ChromaDB Docker")
        print(f"📡 Heartbeat response: {heartbeat}")
        
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB Docker: {e}")
        print("💡 Make sure ChromaDB is running: docker-compose up -d")
        return None
    
    return client

def list_collections(client):
    """List all collections in the ChromaDB instance."""
    print(f"\n📚 Collections in ChromaDB")
    print("-" * 30)
    
    try:
        collections = client.list_collections()
        
        if not collections:
            print("📭 No collections found")
            return []
        
        print(f"Found {len(collections)} collection(s):")
        
        for collection in collections:
            count = collection.count()
            print(f"  📁 {collection.name}")
            print(f"     📊 Documents: {count}")
            print(f"     🆔 ID: {collection.id}")
            
            # Show sample metadata if documents exist
            if count > 0:
                try:
                    sample = collection.peek(limit=1)
                    if sample.get('metadatas') and sample['metadatas'][0]:
                        metadata_keys = list(sample['metadatas'][0].keys())
                        print(f"     🏷️  Sample metadata fields: {metadata_keys}")
                except Exception as e:
                    print(f"     ⚠️  Could not peek metadata: {e}")
            
            print()
        
        return collections
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        return []

def show_collection_details(client, collection_name):
    """Show detailed information about a specific collection."""
    print(f"\n🔍 Detailed Analysis: {collection_name}")
    print("-" * 40)
    
    try:
        collection = client.get_collection(collection_name)
        count = collection.count()
        
        print(f"📊 Total documents: {count}")
        
        if count == 0:
            print("📭 Collection is empty")
            return
        
        # Get sample documents
        sample_size = min(3, count)
        sample = collection.peek(limit=sample_size)
        
        print(f"\n📄 Sample Documents (showing {sample_size} of {count}):")
        
        if sample.get('documents'):
            for i, doc in enumerate(sample['documents']):
                preview = doc[:150] + "..." if len(doc) > 150 else doc
                print(f"\n  Document {i+1}:")
                print(f"    Content: {preview}")
                
                if sample.get('metadatas') and i < len(sample['metadatas']):
                    metadata = sample['metadatas'][i]
                    if metadata:
                        print(f"    Metadata: {metadata}")
                
                if sample.get('ids') and i < len(sample['ids']):
                    print(f"    ID: {sample['ids'][i]}")
        
    except Exception as e:
        print(f"❌ Error getting collection details: {e}")

def create_test_collection(client):
    """Create a test collection for demonstration."""
    print(f"\n🧪 Creating Test Collection")
    print("-" * 30)
    
    try:
        # Create or get test collection
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"description": "Test collection created by test script"}
        )
        
        print(f"✅ Test collection created/retrieved: {collection.name}")
        
        # Add some test documents if collection is empty
        if collection.count() == 0:
            test_docs = [
                "This is a test document about ChromaDB.",
                "ChromaDB is a vector database for embeddings.",
                "Docker makes it easy to run ChromaDB locally."
            ]
            
            test_metadata = [
                {"source": "test", "type": "intro"},
                {"source": "test", "type": "definition"},
                {"source": "test", "type": "deployment"}
            ]
            
            test_ids = ["test_1", "test_2", "test_3"]
            
            collection.add(
                documents=test_docs,
                metadatas=test_metadata,
                ids=test_ids
            )
            
            print(f"📝 Added {len(test_docs)} test documents")
        else:
            print(f"📚 Collection already has {collection.count()} documents")
        
        return collection
        
    except Exception as e:
        print(f"❌ Error creating test collection: {e}")
        return None

def search_test(client, collection_name="test_collection"):
    """Test search functionality."""
    print(f"\n🔍 Testing Search Functionality")
    print("-" * 35)
    
    try:
        collection = client.get_collection(collection_name)
        
        # Test query
        query = "vector database"
        print(f"🔎 Searching for: '{query}'")
        
        # Note: This will only work if you have embeddings configured
        # For basic testing, we'll just show the collection info
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        if results['documents']:
            print(f"✅ Found {len(results['documents'][0])} results:")
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results.get('distances') else "N/A"
                preview = doc[:100] + "..." if len(doc) > 100 else doc
                print(f"  {i+1}. {preview} (distance: {distance})")
        else:
            print("📭 No results found")
            
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")
        print("💡 This might be because embeddings aren't configured for this collection")

def show_system_info(client):
    """Show ChromaDB system information."""
    print(f"\n💻 System Information")
    print("-" * 25)
    
    try:
        # Get version info
        version = client.get_version()
        print(f"🔢 ChromaDB Version: {version}")
        
        # Count total collections
        collections = client.list_collections()
        print(f"📚 Total Collections: {len(collections)}")
        
        # Count total documents across all collections
        total_docs = sum(collection.count() for collection in collections)
        print(f"📄 Total Documents: {total_docs}")
        
    except Exception as e:
        print(f"⚠️  Could not get system info: {e}")

def main():
    """Main function to run all tests."""
    print("🚀 ChromaDB Docker Connection Test")
    print("=" * 50)
    print("Testing connection to ChromaDB running in Docker container\n")
    
    # Test connection
    client = test_docker_chromadb()
    if not client:
        sys.exit(1)
    
    # Show system info
    show_system_info(client)
    
    # List existing collections
    collections = list_collections(client)
    
    # Create a test collection for demonstration
    test_collection = create_test_collection(client)
    
    # Show details of collections
    if collections:
        # Show details of first collection
        show_collection_details(client, collections[0].name)
    
    # Test search functionality
    if test_collection:
        search_test(client, test_collection.name)
    
    print(f"\n" + "=" * 50)
    print("✨ ChromaDB Docker test complete!")
    print("\n💡 Notes:")
    print("   • Multi-tenancy features (get_or_create_tenant) are enterprise-only")
    print("   • Standard ChromaDB works with collections directly")
    print("   • Your MCP RAG project likely creates collections for document storage")

if __name__ == "__main__":
    main()