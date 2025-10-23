#!/usr/bin/env python3
"""
Test script to verify rerank warning is fixed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.knowledge_base import KnowledgeService

async def test_rerank_warning_fix():
    """Test if the rerank warning is fixed by disabling rerank in QueryParam"""
    
    print("Testing rerank warning fix...")
    
    try:
        # Initialize the knowledge service
        knowledge_service = KnowledgeService()
        
        # Create a test space
        space_name = "test_rerank_fix"
        
        print(f"Creating knowledge space: {space_name}")
        success = await knowledge_service.create_space(space_name)
        
        if success:
            print(f"✅ Knowledge space '{space_name}' created successfully!")
            
            # Add a simple document to have some content to query
            print("Adding test document...")
            await knowledge_service.add_document(
                space_name=space_name,
                content="This is a test document about machine learning. Machine learning is a subset of artificial intelligence.",
                title="Test Document",
                doc_type="text"
            )
            
            # Try to query the knowledge base (this should NOT show rerank warning)
            print("Testing knowledge query (should NOT show rerank warning)...")
            result = await knowledge_service.query_knowledge(
                space_name=space_name, 
                question="What is machine learning?",
                mode="hybrid"
            )
            
            print(f"Query result: {result.get('answer', 'No answer')[:100]}...")
            
            if result and result.get("answer"):
                print("✅ SUCCESS: Query completed successfully!")
                print("✅ If you see no WARNING about rerank above, the fix worked!")
            else:
                print("❌ Query returned empty result")
                
        else:
            print(f"❌ FAILED: Could not create knowledge space '{space_name}'")
            
    except Exception as e:
        print(f"❌ FAILED: Test encountered error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing rerank warning fix...")
    print("=" * 60)
    asyncio.run(test_rerank_warning_fix())