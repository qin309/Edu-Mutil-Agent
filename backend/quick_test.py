#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test for SiliconFlow + LightRAG integration"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Set environment
os.environ["SILICONFLOW_API_KEY"] = "sk-mczrhquoybaxwicxgsfdaereipgbapmtiersywbzkorjogla"
os.environ["UPLOAD_DIR"] = str(backend_path / "uploads")

print("=" * 60)
print("SiliconFlow Integration Quick Test")
print("=" * 60)

# Test 1: Import
print("\n[1] Importing services...")
try:
    from app.services.knowledge_base import knowledge_base
    print("OK: Knowledge base service imported")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)

# Test 2: Get default space
print("\n[2] Getting default knowledge space...")
try:
    default_space = knowledge_base.get_space("default")
    if default_space:
        print(f"OK: Default space found")
        print(f"    - Available: {default_space.is_available()}")
        print(f"    - Directory: {default_space.space_dir}")

        if default_space.rag:
            print(f"    - LightRAG initialized: YES")
            print(f"    - Working dir: {default_space.rag.working_dir}")
        else:
            print(f"    - LightRAG initialized: NO")
    else:
        print("FAIL: Default space not found")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test embedding function
print("\n[3] Testing embedding function...")
try:
    from app.services.knowledge_base import siliconflow_embed
    test_texts = ["Hello", "World"]
    embeddings = siliconflow_embed(test_texts)
    print(f"OK: Generated {len(embeddings)} embeddings")
    print(f"    - Dimension: {len(embeddings[0])}")
    if len(embeddings[0]) == 2560:
        print(f"    - Correct dimension (Qwen3-Embedding-4B)")
    else:
        print(f"    - WARNING: Expected 2560, got {len(embeddings[0])}")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Stats
print("\n[4] Checking knowledge base stats...")
try:
    stats = knowledge_base.get_stats("default")
    print(f"OK: Stats retrieved")
    print(f"    - Total documents: {stats['total_documents']}")
    print(f"    - LightRAG available: {stats['lightrag_available']}")
except Exception as e:
    print(f"FAIL: {e}")

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

# Final check
default_space = knowledge_base.get_space("default")
if default_space and default_space.is_available():
    print("\nSUCCESS: SiliconFlow integration working!")
    print("  - Embedding Model: Qwen/Qwen3-Embedding-4B")
    print("  - LLM Model: Qwen/Qwen3-Next-80B-A3B-Instruct")
    print("  - LightRAG: Ready")
else:
    print("\nFAIL: LightRAG not properly initialized")
    print("Check logs above for errors")
