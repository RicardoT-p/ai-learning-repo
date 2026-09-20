"""Airflow 任务调用的纯 Python 数据处理步骤。"""

import json
from pathlib import Path


def write_jsonl_safely(path: Path, records: list[dict]) -> None:
    """先写临时文件再替换，避免任务中断后留下半个文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    temporary.replace(path)


def extract(base_dir: str) -> str:
    """模拟从外部系统抽取数据；重复执行会得到同样结果。"""
    path = Path(base_dir) / "raw" / "sample.jsonl"
    records = [
        {"id": "1", "text": "太短"},
        {"id": "2", "text": "这是可以进入训练数据集的一条示例文本。"},
        {"id": "3", "text": "这是可以进入训练数据集的一条示例文本。"},
        {"id": "4", "text": "Airflow 负责安排任务顺序、重试和运行记录。"},
    ]
    write_jsonl_safely(path, records)
    return str(path)


def clean(raw_path: str) -> str:
    """过滤短文本，并按完整文本做精确去重。"""
    source = Path(raw_path)
    output = source.parents[1] / "clean" / "data.jsonl"
    kept, seen = [], set()
    with source.open(encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            text = record["text"].strip()
            if len(text) < 15 or text in seen:
                continue
            seen.add(text)
            record["text"] = text
            kept.append(record)
    write_jsonl_safely(output, kept)
    return str(output)


def quality(clean_path: str) -> dict:
    """生成简单质量报告，供 Airflow 页面查看返回值。"""
    source = Path(clean_path)
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    report = {
        "clean_rows": len(records),
        "average_chars": round(sum(len(row["text"]) for row in records) / len(records), 2)
        if records else 0,
    }
    report_path = source.parents[1] / "reports" / "quality.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
