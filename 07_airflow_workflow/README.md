# 项目 7：Airflow 数据工作流

目标：把数据抽取、清洗、质量检查变成有依赖、有重试、有运行记录的任务。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\07_airflow_workflow
..\.venv\Scripts\python.exe -m unittest test_steps.py
```

Airflow 官方主要支持 Linux/macOS；Windows 建议使用 WSL2 或 Docker。把 `dags` 目录放进 Airflow 的 DAG 目录后，在网页中触发 `ai_data_pipeline`。

阅读顺序：`pipeline_steps.py` -> `ai_data_pipeline.py`。下一步可把模拟抽取换成爬虫产物，并增加失败告警。

