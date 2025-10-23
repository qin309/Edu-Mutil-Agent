#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试 - 确认系统完全正常
"""
import os
import sys

print("=" * 70)
print("EduAgent - SiliconFlow集成 - 最终测试")
print("=" * 70)

# 测试1: 导入检查
print("\n[测试1] 模块导入...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from app.services.knowledge_base import knowledge_base, siliconflow_embed
    from lightrag import LightRAG
    print("    ✓ 所有模块导入成功")
except Exception as e:
    print(f"    ✗ 导入失败: {e}")
    sys.exit(1)

# 测试2: LightRAG默认配置
print("\n[测试2] LightRAG tokenizer配置...")
try:
    import inspect
    sig = inspect.signature(LightRAG.__init__)
    default_tokenizer = sig.parameters['tiktoken_model_name'].default

    if default_tokenizer == "gpt-4":
        print(f"    ✓ tiktoken_model_name = {default_tokenizer}")
    else:
        print(f"    ✗ tiktoken_model_name = {default_tokenizer} (应该是 gpt-4)")
        print("    请运行: python -c \"from lightrag import LightRAG; print(LightRAG.__file__)\"")
        print("    然后编辑该文件,将第222行的 'gpt-4o-mini' 改为 'gpt-4'")
except Exception as e:
    print(f"    ✗ 检查失败: {e}")

# 测试3: Embedding配置
print("\n[测试3] Embedding函数...")
try:
    if hasattr(siliconflow_embed, 'embedding_dim'):
        dim = siliconflow_embed.embedding_dim
        if dim == 2560:
            print(f"    ✓ Embedding维度: {dim} (Qwen3-Embedding-4B)")
        else:
            print(f"    ✗ Embedding维度错误: {dim} (应该是 2560)")
    else:
        print("    ✗ embedding_dim属性未设置")
except Exception as e:
    print(f"    ✗ 测试失败: {e}")

# 测试4: 知识空间初始化
print("\n[测试4] 知识空间状态...")
try:
    spaces = knowledge_base.list_spaces()
    print(f"    ✓ 发现 {len(spaces)} 个知识空间: {', '.join(spaces)}")

    for space_name in spaces:
        space = knowledge_base.get_space(space_name)
        if space and space.is_available():
            print(f"    ✓ '{space_name}' 空间: LightRAG已初始化")
        else:
            print(f"    ✗ '{space_name}' 空间: LightRAG未初始化")
except Exception as e:
    print(f"    ✗ 测试失败: {e}")

# 测试5: API密钥
print("\n[测试5] API密钥配置...")
try:
    api_key = os.getenv('SILICONFLOW_API_KEY', '')
    if api_key:
        masked = api_key[:10] + '...' + api_key[-4:]
        print(f"    ✓ SILICONFLOW_API_KEY: {masked}")
    else:
        print("    ✗ SILICONFLOW_API_KEY 未设置")
        print("    请在 backend/.env 文件中添加:")
        print("    SILICONFLOW_API_KEY=你的API密钥")
except Exception as e:
    print(f"    ✗ 检查失败: {e}")

# 测试6: Embedding实际调用
print("\n[测试6] Embedding实际调用...")
try:
    test_texts = ["测试文本"]
    result = siliconflow_embed(test_texts)

    if len(result) == 1 and len(result[0]) == 2560:
        print(f"    ✓ 成功生成向量: {len(result)} 个, 维度: {len(result[0])}")
    else:
        print(f"    ✗ 向量生成异常: {len(result)} 个向量, 维度: {len(result[0]) if result else 0}")
except Exception as e:
    print(f"    ✗ 调用失败: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70)

print("\n✓ 表示测试通过")
print("✗ 表示测试失败,请按照提示修复")
print("\n如果所有测试都显示 ✓, 系统已完全就绪!")
print("\n启动服务器:")
print("  Windows: start_server.bat")
print("  Linux/Mac: python main.py")
print("\n服务器地址: http://localhost:8000")
print("=" * 70)
