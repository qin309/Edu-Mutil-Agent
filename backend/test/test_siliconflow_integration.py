#!/usr/bin/env python3
"""
Test script for SiliconFlow integration with LightRAG
Tests embedding and LLM functions
"""
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Set environment variables
os.environ["SILICONFLOW_API_KEY"] = "sk-mczrhquoybaxwicxgsfdaereipgbapmtiersywbzkorjogla"
os.environ["UPLOAD_DIR"] = str(backend_path / "uploads")

print("=" * 60)
print("SiliconFlow + LightRAG Integration Test")
print("=" * 60)

# Test 1: Import and check availability
print("\n[Test 1] Checking imports...")
try:
    from app.services.knowledge_base import knowledge_base, siliconflow_embed
    print("✅ Knowledge base service imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check LightRAG availability
print("\n[Test 2] Checking LightRAG availability...")
try:
    from lightrag import LightRAG, QueryParam
    print(f"✅ LightRAG library available")
except ImportError as e:
    print(f"❌ LightRAG not installed: {e}")
    sys.exit(1)

# Test 3: Test embedding function directly
print("\n[Test 3] Testing SiliconFlow embedding function...")
try:
    test_texts = ["Hello world", "LightRAG integration test"]
    print(f"Testing with {len(test_texts)} sample texts...")
    embeddings = siliconflow_embed(test_texts)
    print(f"✅ Embedding successful!")
    print(f"   - Generated {len(embeddings)} embeddings")
    print(f"   - Embedding dimension: {len(embeddings[0])}")
    if len(embeddings[0]) == 2560:
        print(f"   - ✅ Correct dimension (Qwen3-Embedding-4B: 2560)")
    else:
        print(f"   - ⚠️ Unexpected dimension (expected 2560)")
except Exception as e:
    print(f"❌ Embedding test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check knowledge spaces
print("\n[Test 4] Checking knowledge spaces...")
try:
    spaces = knowledge_base.list_spaces()
    print(f"✅ Found {len(spaces)} knowledge space(s): {spaces}")

    # Check default space
    default_space = knowledge_base.get_space("default")
    if default_space:
        print(f"✅ Default space available")
        print(f"   - LightRAG initialized: {default_space.is_available()}")
        if default_space.rag:
            print(f"   - Working directory: {default_space.space_dir}")
        else:
            print(f"   - ⚠️ LightRAG instance not initialized")
    else:
        print(f"❌ Default space not found")
except Exception as e:
    print(f"❌ Space check failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test document addition (small test)
print("\n[Test 5] Testing document addition...")
try:
    test_content = """
    LightRAG是一个基于知识图谱的RAG系统。
    它使用向量嵌入和大语言模型来构建知识库。
    本测试验证SiliconFlow API集成是否成功。
    """

    async def test_add_document():
        result = await knowledge_base.add_document(
            content=test_content.strip(),
            title="SiliconFlow Integration Test",
            doc_type="text/plain",
            metadata={"test": True},
            space_name="default"
        )
        return result

    print("Adding test document to default space...")
    success = asyncio.run(test_add_document())

    if success:
        print("✅ Document added successfully")

        # Check stats
        stats = knowledge_base.get_stats("default")
        print(f"   - Total documents: {stats['total_documents']}")
        print(f"   - LightRAG available: {stats['lightrag_available']}")
    else:
        print("❌ Document addition failed")

except Exception as e:
    print(f"❌ Document test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test query (if documents exist)
print("\n[Test 6] Testing knowledge query...")
try:
    stats = knowledge_base.get_stats("default")
    if stats['total_documents'] > 0:
        async def test_query():
            result = await knowledge_base.query_knowledge(
                question="什么是LightRAG？",
                mode="hybrid",
                space_name="default"
            )
            return result

        print("Querying: '什么是LightRAG？'")
        result = asyncio.run(test_query())

        print(f"✅ Query completed")
        print(f"   - Answer length: {len(result['answer'])} characters")
        print(f"   - Mode: {result['mode']}")
        print(f"   - Answer preview: {result['answer'][:200]}...")
    else:
        print("⚠️ Skipping query test (no documents in knowledge base)")

except Exception as e:
    print(f"❌ Query test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Integration Test Complete")
print("=" * 60)

# Summary
print("\n[Summary]")
default_space = knowledge_base.get_space("default")
if default_space and default_space.is_available():
    print("✅ SiliconFlow integration successful!")
    print(f"✅ Embedding Model: Qwen/Qwen3-Embedding-4B (2560 dim)")
    print(f"✅ LLM Model: Qwen/Qwen3-Next-80B-A3B-Instruct")
    print(f"✅ Tokenizer: gpt-4 (fixed)")
    print(f"✅ LightRAG initialized and ready")
else:
    print("⚠️ LightRAG initialization incomplete")
    print("Check logs above for specific errors")
