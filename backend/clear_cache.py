#!/usr/bin/env python3
"""
清除Python缓存并启动服务器
"""
import os
import shutil
import sys

print("=" * 60)
print("清除Python缓存...")
print("=" * 60)

# 删除所有 __pycache__ 目录
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        cache_dir = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(cache_dir)
            print(f"已删除: {cache_dir}")
        except Exception as e:
            print(f"无法删除 {cache_dir}: {e}")

# 删除所有 .pyc 文件
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_file = os.path.join(root, file)
            try:
                os.remove(pyc_file)
                print(f"已删除: {pyc_file}")
            except Exception as e:
                print(f"无法删除 {pyc_file}: {e}")

print("\n" + "=" * 60)
print("缓存清除完成!")
print("=" * 60)
print("\n现在请手动运行: python main.py")
