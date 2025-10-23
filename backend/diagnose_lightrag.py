"""
诊断LightRAG安装和配置的脚本
运行方式: python diagnose_lightrag.py
"""
import sys
from pathlib import Path

print("=" * 70)
print("LightRAG 诊断工具")
print("=" * 70)

# 1. 检查Python版本
print("\n1. Python版本检查")
print(f"   Python版本: {sys.version}")
if sys.version_info >= (3, 9):
    print("   ✅ Python版本符合要求 (>= 3.9)")
else:
    print("   ❌ Python版本过低,需要 >= 3.9")

# 2. 检查LightRAG安装
print("\n2. LightRAG安装检查")
try:
    import lightrag
    print(f"   ✅ LightRAG已安装")
    try:
        print(f"   版本: {lightrag.__version__}")
    except:
        print(f"   版本: 未知")

    # 检查关键组件
    try:
        from lightrag import LightRAG, QueryParam
        print("   ✅ 核心组件可导入: LightRAG, QueryParam")
    except Exception as e:
        print(f"   ❌ 核心组件导入失败: {e}")

except ImportError as e:
    print(f"   ❌ LightRAG未安装")
    print(f"   错误: {e}")
    print(f"   安装命令: pip install lightrag-hku")

# 3. 检查依赖包
print("\n3. 依赖包检查")

dependencies = {
    "httpx": "HTTP客户端",
    "nest_asyncio": "异步事件循环",
    "numpy": "数值计算",
    "PyMuPDF": "PDF处理",
    "python-docx": "DOCX处理",
    "pdfplumber": "PDF处理(备选)",
}

for pkg, desc in dependencies.items():
    try:
        if pkg == "PyMuPDF":
            import fitz
            print(f"   ✅ {pkg} ({desc}): 已安装")
        elif pkg == "python-docx":
            import docx
            print(f"   ✅ {pkg} ({desc}): 已安装")
        else:
            __import__(pkg)
            print(f"   ✅ {pkg} ({desc}): 已安装")
    except ImportError:
        print(f"   ⚠️  {pkg} ({desc}): 未安装")
        if pkg in ["httpx", "numpy"]:
            print(f"      安装命令: pip install {pkg}")

# 4. 检查环境变量
print("\n4. 环境变量检查")
import os

env_vars = {
    "OPENROUTER_API_KEY": "OpenRouter API密钥",
    "SILICONFLOW_API_KEY": "SiliconFlow API密钥",
}

for var, desc in env_vars.items():
    value = os.getenv(var)
    if value:
        masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
        print(f"   ✅ {var} ({desc}): {masked}")
    else:
        print(f"   ⚠️  {var} ({desc}): 未设置")

# 5. 测试LightRAG初始化
print("\n5. LightRAG初始化测试")
try:
    from lightrag import LightRAG
    import tempfile

    test_dir = Path(tempfile.mkdtemp())
    print(f"   测试目录: {test_dir}")

    def dummy_llm(prompt, **kwargs):
        return "Test response"

    def dummy_embed(texts):
        return [[0.0] * 2560] * len(texts)  # Qwen3-Embedding-4B: 2560维

    print("   创建LightRAG实例...")
    rag = LightRAG(
        working_dir=str(test_dir),
        llm_model_func=dummy_llm,
        embedding_func=dummy_embed,
        tiktoken_model_name="gpt-4"  # 修复tokenizer错误
    )
    print("   ✅ LightRAG实例创建成功")

    # 测试插入
    print("   测试文档插入...")
    try:
        rag.insert("This is a test document.")
        print("   ✅ 文档插入成功")
    except Exception as e:
        print(f"   ❌ 文档插入失败: {e}")
        import traceback
        traceback.print_exc()

    # 清理
    import shutil
    shutil.rmtree(test_dir)

except Exception as e:
    print(f"   ❌ LightRAG初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 检查知识空间目录
print("\n6. 知识空间目录检查")
uploads_dir = Path("./uploads/knowledge_spaces")
if uploads_dir.exists():
    print(f"   目录: {uploads_dir}")
    spaces = [d.name for d in uploads_dir.iterdir() if d.is_dir()]
    if spaces:
        print(f"   已有空间: {', '.join(spaces)}")
        for space in spaces:
            space_dir = uploads_dir / space
            files = list(space_dir.glob("*"))
            print(f"   - {space}: {len(files)} 个文件")
    else:
        print("   ⚠️  没有已创建的知识空间")
else:
    print(f"   ⚠️  目录不存在: {uploads_dir}")

# 7. 总结和建议
print("\n" + "=" * 70)
print("诊断总结")
print("=" * 70)

issues = []
recommendations = []

# 检查LightRAG
try:
    from lightrag import LightRAG
except ImportError:
    issues.append("LightRAG未安装")
    recommendations.append("运行: pip install lightrag-hku")

# 检查nest_asyncio
try:
    import nest_asyncio
except ImportError:
    issues.append("nest_asyncio未安装")
    recommendations.append("运行: pip install nest-asyncio")

# 检查PDF支持
try:
    import fitz
except ImportError:
    try:
        import pdfplumber
    except ImportError:
        issues.append("PDF处理库未安装")
        recommendations.append("运行: pip install PyMuPDF")

# 检查DOCX支持
try:
    import docx
except ImportError:
    issues.append("DOCX处理库未安装")
    recommendations.append("运行: pip install python-docx")

# 检查API密钥
if not os.getenv("OPENROUTER_API_KEY"):
    issues.append("OPENROUTER_API_KEY未设置")
    recommendations.append("在.env文件中设置OPENROUTER_API_KEY")

if not os.getenv("SILICONFLOW_API_KEY"):
    issues.append("SILICONFLOW_API_KEY未设置(可选)")
    recommendations.append("在.env文件中设置SILICONFLOW_API_KEY")

if issues:
    print("\n发现的问题:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

    print("\n建议的解决方案:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("\n✅ 所有检查通过! LightRAG配置正确。")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
