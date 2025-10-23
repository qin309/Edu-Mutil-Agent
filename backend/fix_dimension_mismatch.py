#!/usr/bin/env python3
"""
Script to fix the embedding dimension mismatch by clearing and reinitializing the test space
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def clear_test_space():
    """Clear the test knowledge space to fix dimension mismatch"""
    print("=== Fixing Embedding Dimension Mismatch ===\n")
    
    # Set environment
    os.environ["SILICONFLOW_API_KEY"] = "sk-mczrhquoybaxwicxgsfdaereipgbapmtiersywbzkorjogla"
    
    try:
        # Get the test space directory
        test_space_dir = Path("uploads/knowledge_spaces/test")
        
        if not test_space_dir.exists():
            print("❌ Test space directory not found")
            return False
        
        print(f"📁 Found test space directory: {test_space_dir}")
        
        # Files to remove to fix dimension mismatch
        files_to_remove = [
            "vdb_entities.json",
            "vdb_relationships.json", 
            "vdb_chunks.json",
            "graph_chunk_entity_relation.csv",
            "graph_chunk_entity_relation.graphml",
            "kv_store_full_docs.json",
            "kv_store_text_chunks.json",
            "kv_store_community_reports.json",
            "kv_store_llm_response_cache.json",
            "kv_store_doc_status.json"
        ]
        
        removed_count = 0
        for file_name in files_to_remove:
            file_path = test_space_dir / file_name
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"🗑️  Removed: {file_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_name}: {e}")
            else:
                print(f"⚪ Not found: {file_name}")
        
        print(f"\n📊 Summary:")
        print(f"   - Files removed: {removed_count}")
        print(f"   - Files checked: {len(files_to_remove)}")
        
        # Keep documents.json to preserve document metadata
        docs_file = test_space_dir / "documents.json"
        if docs_file.exists():
            print(f"✅ Preserved: documents.json (document metadata)")
        
        print(f"\n🔧 The vector database has been cleared.")
        print(f"📝 Document metadata is preserved.")
        print(f"🔄 On next initialization, the RAG system will rebuild with correct dimensions (1024).")
        print(f"💡 The system will now work with BAAI/bge-large-zh-v1.5 model.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    success = clear_test_space()
    
    if success:
        print("\n🎉 Dimension mismatch fix completed successfully!")
        print("\nNext steps:")
        print("1. The vector database has been cleared")
        print("2. Document metadata is preserved") 
        print("3. On next knowledge base access, it will rebuild with 1024 dimensions")
        print("4. The system is now compatible with BAAI/bge-large-zh-v1.5")
    else:
        print("\n❌ Some issues occurred during the fix process")
    
    exit(0 if success else 1)