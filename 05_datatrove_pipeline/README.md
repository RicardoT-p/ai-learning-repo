# 项目 5：DataTrove 训练语料流水线

目标：理解训练数据如何按“读取、过滤、统计、输出”组成流水线。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\05_datatrove_pipeline
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe pipeline.py
..\.venv\Scripts\python.exe -m unittest test_pipeline.py
```

先读 `keep_useful_text()`，再看 `pipeline` 列表，最后看执行器。下一步可加入语言识别、重复文本删除和敏感信息过滤。

