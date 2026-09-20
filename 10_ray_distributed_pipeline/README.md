# 项目 10：Ray Data 分布式数据处理

目标：从单机 Python 循环过渡到可扩展的数据集过滤、映射和 Parquet 输出。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\10_ray_distributed_pipeline
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe process.py
..\.venv\Scripts\python.exe -m unittest test_process.py
```

先读两个纯函数，再看 `run()` 如何把它们交给 Ray。Windows 若遇到兼容问题，放到 WSL2 中运行。下一步可生成百万行数据，比较普通 Python 与 Ray 的耗时。

