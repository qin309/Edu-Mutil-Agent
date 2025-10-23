#!/usr/bin/env python3
"""
Test script to verify EmbeddingFunc fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.knowledge_base import KnowledgeService
import asyncio

async def test_embedding_func_fix():
    """Test if the EmbeddingFunc fix resolves the LightRAG initialization error"""
    
    print("Testing EmbeddingFunc fix...")
    
    try:
        # Initialize the knowledge service
        knowledge_service = KnowledgeService()
        
        # Try to create a test space (this should trigger the EmbeddingFunc usage)
        space_name = "test_embedding_fix"
        
        print(f"Creating knowledge space: {space_name}")
        success = await knowledge_service.create_space(space_name)
        
        if success:
            print(f"✅ SUCCESS: Knowledge space '{space_name}' created successfully!")
            
            # Try to query the knowledge base (this should trigger the embedding function usage)
            print("Testing knowledge query...")
            result = await knowledge_service.query_knowledge(
                space_name=space_name, 
                question="What is this space about?",
                mode="hybrid"
            )
            
            print(f"Query result: {result}")
            
            if "AttributeError" not in str(result.get("answer", "")):
                print("✅ SUCCESS: Query completed without AttributeError!")
            else:
                print("❌ FAILED: Query still has AttributeError")
                
        else:
            print(f"❌ FAILED: Could not create knowledge space '{space_name}'")
            
    except Exception as e:
        print(f"❌ FAILED: Test encountered error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_embedding_func_fix())