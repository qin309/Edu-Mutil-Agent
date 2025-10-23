"""
测试LightRAG集成的脚本
运行方式: python test_lightrag.py
"""
import asyncio
import sys
from pathlib import Path

# 添加app目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.knowledge_base import KnowledgeBaseManager

async def test_knowledge_base():
    """测试知识库功能"""
    print("=" * 60)
    print("测试 LightRAG 知识库集成")
    print("=" * 60)

    # 初始化知识库管理器
    print("\n1. 初始化知识库管理器...")
    kb_manager = KnowledgeBaseManager()

    # 检查默认空间
    print("\n2. 检查默认知识空间...")
    spaces = kb_manager.list_spaces()
    print(f"   可用空间: {spaces}")

    # 检查LightRAG状态
    print("\n3. 检查LightRAG状态...")
    is_available = kb_manager.is_available("default")
    print(f"   LightRAG可用: {is_available}")

    if not is_available:
        print("   ⚠️  LightRAG未初始化或不可用")
        return

    # 测试文档添加
    print("\n4. 测试添加文档...")
    test_content = """
    人工智能(Artificial Intelligence, AI)是计算机科学的一个分支。
    它企图了解智能的实质,并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。

    机器学习是人工智能的一个子领域,它使计算机能够在没有明确编程的情况下学习。
    深度学习是机器学习的一个分支,它使用多层神经网络来学习数据的表示。
    """

    try:
        success = await kb_manager.add_document(
            content=test_content,
            title="AI基础知识",
            doc_type="text/plain",
            metadata={
                "course": "人工智能导论",
                "test": True
            },
            space_name="default"
        )

        if success:
            print("   ✅ 文档添加成功")
        else:
            print("   ❌ 文档添加失败")
            return
    except Exception as e:
        print(f"   ❌ 文档添加异常: {e}")
        import traceback
        traceback.print_exc()
        return

    # 等待一下让索引完成
    print("\n5. 等待索引完成...")
    await asyncio.sleep(2)

    # 测试查询
    print("\n6. 测试知识查询...")
    test_questions = [
        "什么是人工智能?",
        "机器学习和深度学习的关系是什么?",
        "AI的研究领域包括哪些?"
    ]

    for question in test_questions:
        print(f"\n   问题: {question}")
        try:
            result = await kb_manager.query_knowledge(
                question=question,
                mode="hybrid",
                space_name="default"
            )
            print(f"   回答: {result['answer'][:200]}...")
            print(f"   来源: {result.get('sources', [])}")
            print(f"   模式: {result.get('mode', 'unknown')}")
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

    # 测试统计信息
    print("\n7. 查看统计信息...")
    stats = kb_manager.get_stats("default")
    print(f"   总文档数: {stats.get('total_documents', 0)}")
    print(f"   文档类型: {stats.get('document_types', {})}")
    print(f"   内容总量: {stats.get('total_content_length', 0)} 字符")
    print(f"   LightRAG状态: {'可用' if stats.get('lightrag_available') else '不可用'}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    print("开始测试LightRAG集成...\n")

    # 检查依赖
    try:
        from lightrag import LightRAG
        print("✅ LightRAG已安装")
    except ImportError:
        print("❌ LightRAG未安装，请运行: pip install lightrag-hku")
        sys.exit(1)

    try:
        import nest_asyncio
        print("✅ nest_asyncio已安装")
    except ImportError:
        print("⚠️  nest_asyncio未安装，建议运行: pip install nest-asyncio")

    print()

    # 运行测试
    asyncio.run(test_knowledge_base())
