"""
Test and compare different PDF chunking methods for search quality.
"""

import json
from pathlib import Path
from pdf_processor import PDFProcessor
from store_embeddings import store_to_chroma, ModelVendor
import tempfile
import shutil

def test_search_quality():
    """Test search quality with both chunking methods."""
    processor = PDFProcessor()
    pdf_path = Path("thinkpython.pdf")
    
    if not pdf_path.exists():
        print("thinkpython.pdf not found. Please ensure it's in the current directory.")
        return
    
    print("🔍 Testing Search Quality Comparison")
    print("=" * 60)
    
    # Test queries to evaluate
    test_queries = [
        "Python function definition syntax",
        "return statements and values",
        "variables and assignment",
        "conditional statements if else",
        "loops and iteration"
    ]
    
    # Process with both methods
    print("📚 Processing PDF with both methods...")
    
    try:
        # Custom method
        custom_docs = processor.pdf_to_documents(pdf_path)
        print(f"Custom method: {len(custom_docs)} chunks")
        
        # Recursive method
        recursive_docs = processor.pdf_to_documents_recursive(pdf_path)
        print(f"Recursive method: {len(recursive_docs)} chunks")
        
        # Create temporary vector stores for testing
        print("\n🗄️ Creating separate vector stores for comparison...")
        
        from langchain_chroma import Chroma
        from store_embeddings import load_embedding_model
        import tempfile
        
        # Create temporary directories for separate testing
        custom_temp_dir = tempfile.mkdtemp(prefix="custom_chunks_")
        recursive_temp_dir = tempfile.mkdtemp(prefix="recursive_chunks_")
        
        embedding_model = load_embedding_model(ModelVendor.GOOGLE)
        
        # Store custom chunks in separate DB
        custom_vs = Chroma.from_documents(
            documents=custom_docs,
            embedding=embedding_model,
            persist_directory=custom_temp_dir
        )
        
        # Store recursive chunks in separate DB
        recursive_vs = Chroma.from_documents(
            documents=recursive_docs,
            embedding=embedding_model,
            persist_directory=recursive_temp_dir
        )
        
        print("\n🔎 Testing search queries...")
        print("-" * 60)
        
        results_comparison = []
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            # Search with custom method
            custom_results = custom_vs.similarity_search(query, k=3)
            custom_scores = custom_vs.similarity_search_with_score(query, k=3)
            custom_avg_score = sum(score for _, score in custom_scores) / len(custom_scores)
            
            # Search with recursive method
            recursive_results = recursive_vs.similarity_search(query, k=3)
            recursive_scores = recursive_vs.similarity_search_with_score(query, k=3)
            recursive_avg_score = sum(score for _, score in recursive_scores) / len(recursive_scores)
            
            print(f"  Custom avg score: {custom_avg_score:.4f}")
            print(f"  Recursive avg score: {recursive_avg_score:.4f}")
            
            # Analyze result quality
            custom_avg_length = sum(len(doc.page_content) for doc in custom_results) / len(custom_results)
            recursive_avg_length = sum(len(doc.page_content) for doc in recursive_results) / len(recursive_results)
            
            print(f"  Custom avg result length: {custom_avg_length:.1f} chars")
            print(f"  Recursive avg result length: {recursive_avg_length:.1f} chars")
            
            # Store comparison
            results_comparison.append({
                "query": query,
                "custom_score": custom_avg_score,
                "recursive_score": recursive_avg_score,
                "custom_length": custom_avg_length,
                "recursive_length": recursive_avg_length,
                "winner": "custom" if custom_avg_score < recursive_avg_score else "recursive"  # Lower score = better similarity
            })
        
        # Summary analysis
        print("\n📊 SUMMARY ANALYSIS")
        print("=" * 60)
        
        custom_wins = sum(1 for r in results_comparison if r["winner"] == "custom")
        recursive_wins = sum(1 for r in results_comparison if r["winner"] == "recursive")
        
        avg_custom_score = sum(r["custom_score"] for r in results_comparison) / len(results_comparison)
        avg_recursive_score = sum(r["recursive_score"] for r in results_comparison) / len(results_comparison)
        
        print(f"Custom method wins: {custom_wins}/{len(test_queries)} queries")
        print(f"Recursive method wins: {recursive_wins}/{len(test_queries)} queries")
        print(f"Average custom score: {avg_custom_score:.4f}")
        print(f"Average recursive score: {avg_recursive_score:.4f}")
        
        # Recommendation
        print(f"\n🏆 RECOMMENDATION:")
        if avg_custom_score < avg_recursive_score:
            print("Custom method provides better search relevance overall")
            print("✅ Keep current custom chunking approach")
        else:
            print("Recursive method provides better search relevance overall") 
            print("✅ Switch to RecursiveCharacterTextSplitter approach")
        
        print(f"\n💡 TRADE-OFFS:")
        print(f"• Custom: Fewer chunks ({len(custom_docs)}), more context per result")
        print(f"• Recursive: More chunks ({len(recursive_docs)}), more precise boundaries")
        
        # Cleanup temporary directories
        import shutil
        shutil.rmtree(custom_temp_dir, ignore_errors=True)
        shutil.rmtree(recursive_temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temporary test databases")
        
        return results_comparison
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return None

if __name__ == "__main__":
    test_search_quality()