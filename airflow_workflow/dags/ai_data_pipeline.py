"""项目 7：一个可在 Airflow 3 中加载的数据流水线 DAG。"""

import os
from airflow.sdk import dag, task
from pipeline_steps import clean, extract, quality


@dag(schedule=None, catchup=False, tags=["ai-data"])
def ai_data_pipeline():
    """任务依赖关系：抽取 -> 清洗 -> 质量检查。"""

    @task(retries=2)
    def extract_task() -> str:
        return extract(os.getenv("AI_DATA_HOME", "/opt/airflow/data"))

    @task
    def clean_task(raw_path: str) -> str:
        return clean(raw_path)

    @task
    def quality_task(clean_path: str) -> dict:
        return quality(clean_path)

    quality_task(clean_task(extract_task()))


# Airflow 扫描文件时会找到这个 DAG 对象。
ai_data_pipeline()
