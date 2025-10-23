#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终配置验证脚本
验证SiliconFlow + Qwen模型集成
"""
import os
import sys

print("=" * 70)
print("SiliconFlow + Qwen 模型集成 - 最终验证")
print("=" * 70)

# 1. 检查LightRAG配置
print("\n[1] 检查LightRAG默认配置...")
try:
    import lightrag
    from lightrag import LightRAG
    import inspect

    sig = inspect.signature(LightRAG.__init__)
    tiktoken_param = sig.parameters.get('tiktoken_model_name')
    if tiktoken_param:
        default_val = tiktoken_param.default
        print(f"    LightRAG版本: {lightrag.__version__}")
        print(f"    tiktoken_model_name默认值: {default_val}")
        if default_val == "gpt-4":
            print("    [OK] 已修复为 gpt-4")
        else:
            print(f"    [WARNING] 仍为 {default_val}")
except Exception as e:
    print(f"    [ERROR] {e}")

# 2. 检查embedding配置
print("\n[2] 检查Embedding模型配置...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from app.services.knowledge_base import siliconflow_embed

    if hasattr(siliconflow_embed, 'embedding_dim'):
        dim = siliconflow_embed.embedding_dim
        print(f"    Embedding维度: {dim}")
        if dim == 2560:
            print("    [OK] Qwen3-Embedding-4B (2560维)")
        else:
            print(f"    [WARNING] 维度不匹配 (期望2560)")
    else:
        print("    [ERROR] embedding_dim属性未设置")

    # 测试embedding
    print("    测试embedding函数...")
    result = siliconflow_embed(["测试"])
    print(f"    [OK] 生成 {len(result)} 个向量, 维度: {len(result[0])}")

except Exception as e:
    print(f"    [ERROR] {e}")

# 3. 检查LLM配置
print("\n[3] 检查LLM模型配置...")
try:
    # 读取源代码检查模型名称
    with open('app/services/knowledge_base.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Qwen/Qwen3-Next-80B-A3B-Instruct' in content:
            print("    [OK] LLM模型: Qwen/Qwen3-Next-80B-A3B-Instruct")
        else:
            print("    [WARNING] 未找到Qwen3-Next-80B配置")

        if 'Qwen/Qwen3-Embedding-4B' in content:
            print("    [OK] Embedding模型: Qwen/Qwen3-Embedding-4B")
        else:
            print("    [WARNING] 未找到Qwen3-Embedding-4B配置")

        if 'tokenizer=None' in content:
            print("    [OK] Tokenizer已禁用 (避免pickle错误)")
        else:
            print("    [WARNING] Tokenizer配置可能有问题")

except Exception as e:
    print(f"    [ERROR] {e}")

# 4. 检查环境变量
print("\n[4] 检查环境变量...")
try:
    siliconflow_key = os.getenv('SILICONFLOW_API_KEY', '')
    if siliconflow_key:
        masked = siliconflow_key[:15] + '...' + siliconflow_key[-4:]
        print(f"    [OK] SILICONFLOW_API_KEY: {masked}")
    else:
        print("    [WARNING] SILICONFLOW_API_KEY 未设置")
except Exception as e:
    print(f"    [ERROR] {e}")

# 5. 测试LightRAG初始化
print("\n[5] 测试LightRAG初始化...")
try:
    from app.services.knowledge_base import knowledge_base

    default_space = knowledge_base.get_space('default')
    if default_space:
        is_available = default_space.is_available()
        print(f"    Default空间: {'可用' if is_available else '不可用'}")
        if is_available:
            print("    [OK] LightRAG已成功初始化")
        else:
            print("    [WARNING] LightRAG初始化失败")
    else:
        print("    [ERROR] 无法获取default空间")

except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "=" * 70)
print("验证总结")
print("=" * 70)

print("\n已完成的集成:")
print("  - Embedding模型: Qwen/Qwen3-Embedding-4B (2560维)")
print("  - LLM模型: Qwen/Qwen3-Next-80B-A3B-Instruct")
print("  - API提供商: SiliconFlow (https://api.siliconflow.cn)")
print("  - Tokenizer: 已禁用 (避免pickle错误)")
print("\n如果所有检查都显示 [OK], 系统已准备就绪!")
print("=" * 70)
