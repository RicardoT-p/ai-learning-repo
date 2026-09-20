# 项目 6：Polars + DuckDB 数据质量分析

目标：把 JSONL 转成 Parquet，并统计长度、来源分布和精确重复数。

```powershell
cd D:\learning\python\ai-data-engineer-portfolio\06_polars_duckdb_quality
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe quality.py
..\.venv\Scripts\python.exe -m unittest test_quality.py
```

先看 `build_parquet()` 如何增加列，再看 `analyze()` 中的 SQL。下一步可增加空值率、语言分布和文本长度分位数。

