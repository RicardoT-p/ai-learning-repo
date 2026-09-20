# 项目 9：Ragas + Phoenix 评测与可观测性

目标：建立固定测试集，计算事实正确性；需要排查模型调用时，再打开 Phoenix 轨迹。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\09_rag_eval_observability
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY="你的密钥"
..\.venv\Scripts\python.exe evaluate.py
..\.venv\Scripts\python.exe -m unittest test_evaluate.py
```

可选 Phoenix：先运行 `phoenix serve`，设置 `PHOENIX_COLLECTOR_ENDPOINT`，再执行 `evaluate.py --trace`。下一步可加入检索上下文，评测忠实度和上下文召回率。

