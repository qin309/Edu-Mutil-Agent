#!/usr/bin/env python3
"""
Test script to verify timeout fix works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import time
from app.services.knowledge_base import KnowledgeService

async def test_timeout_fix():
    """Test if the timeout issue is resolved"""
    
    print("Testing knowledge query performance...")
    
    try:
        # Initialize the knowledge service
        knowledge_service = KnowledgeService()
        
        # Use existing test space
        space_name = "test"
        
        # Test different query complexities
        test_queries = [
            ("Simple query", "What is this about?"),
            ("Complex query", "请问deepseekv3.2用的什么注意力机制，具体的技术实现是怎样的？"),
            ("Medium query", "Please analyze the main concepts in this knowledge base")
        ]
        
        for query_name, question in test_queries:
            print(f"\nTesting {query_name}: '{question[:50]}...'")
            
            start_time = time.time()
            
            result = await knowledge_service.query_knowledge(
                space_name=space_name, 
                question=question,
                mode="hybrid"
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Duration: {duration:.2f} seconds")
            
            if result and result.get("answer"):
                answer_preview = result["answer"][:100].replace('\n', ' ')
                print(f"✅ SUCCESS: {answer_preview}...")
                
                if duration > 30:
                    print(f"⚠️  WARNING: Query took {duration:.2f}s, may timeout on frontend")
                elif duration > 60:
                    print(f"❌ CRITICAL: Query took {duration:.2f}s, will timeout even with new settings")
                else:
                    print(f"✅ GOOD: Query completed in {duration:.2f}s")
            else:
                print(f"❌ Query returned empty result")
            
            print("-" * 60)
                
    except Exception as e:
        print(f"❌ FAILED: Test encountered error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Knowledge Query Performance")
    print("=" * 60)
    asyncio.run(test_timeout_fix())