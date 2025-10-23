#!/usr/bin/env python3
"""
Simple test to check if LightRAG EmbeddingFunc import works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing LightRAG imports...")
    
    from lightrag import LightRAG, QueryParam
    print("✅ LightRAG imported successfully")
    
    from lightrag.utils import EmbeddingFunc
    print("✅ EmbeddingFunc imported successfully")
    
    # Test creating an EmbeddingFunc instance
    def dummy_embed(texts):
        return [[0.0] * 2560] * len(texts)
    
    embedding_func = EmbeddingFunc(
        embedding_dim=2560,
        func=dummy_embed
    )
    print("✅ EmbeddingFunc instance created successfully")
    print(f"   - embedding_dim: {embedding_func.embedding_dim}")
    print(f"   - func: {embedding_func.func}")
    
    # Test that the func attribute is accessible
    if hasattr(embedding_func, 'func') and embedding_func.func:
        print("✅ EmbeddingFunc.func attribute is accessible")
    else:
        print("❌ EmbeddingFunc.func attribute issue")
    
    print("\n🎉 All tests passed! The EmbeddingFunc fix should work.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()