from lightrag import LightRAG
import inspect

sig = inspect.signature(LightRAG.__init__)
print("LightRAG __init__ parameters:")
for k, v in sig.parameters.items():
    if k != 'self':
        print(f"  {k}: {v.annotation} = {v.default}")
