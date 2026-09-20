"""项目 8：把两份模型回答上传到 Argilla，供人工反馈。"""

import argparse
import json
import os
from pathlib import Path


REQUIRED_FIELDS = {"prompt", "response_a", "response_b"}


def load_records(path: Path) -> list[dict]:
    """读取并校验待标注数据，尽早发现字段缺失。"""
    records = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            record = json.loads(line)
            missing = REQUIRED_FIELDS - record.keys()
            if missing:
                raise ValueError(f"第 {line_number} 行缺少字段：{sorted(missing)}")
            records.append(record)
    return records


def upload(input_file: Path, dataset_name: str) -> None:
    """创建反馈数据集并上传记录。"""
    import argilla as rg

    api_url = os.getenv("ARGILLA_API_URL")
    api_key = os.getenv("ARGILLA_API_KEY")
    if not api_url or not api_key:
        raise RuntimeError("请先设置 ARGILLA_API_URL 和 ARGILLA_API_KEY")

    client = rg.Argilla(api_url=api_url, api_key=api_key)
    settings = rg.Settings(
        fields=[
            rg.TextField(name="prompt", title="用户问题"),
            rg.TextField(name="response_a", title="回答 A"),
            rg.TextField(name="response_b", title="回答 B"),
        ],
        questions=[
            rg.LabelQuestion(
                name="preference",
                title="哪一个回答更好？",
                labels=["A", "B", "平局", "都不好"],
            ),
            rg.RatingQuestion(name="score", title="最佳回答质量", values=[1, 2, 3, 4, 5]),
            rg.TextQuestion(name="reason", title="请说明原因", required=False),
        ],
    )
    dataset = rg.Dataset(name=dataset_name, settings=settings, client=client)
    dataset.create()
    records = [rg.Record(fields=record) for record in load_records(input_file)]
    dataset.records.log(records)
    print(f"已上传 {len(records)} 条记录到数据集：{dataset_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="上传 Argilla 人工反馈任务")
    parser.add_argument("--input", type=Path, default=Path("sample.jsonl"))
    parser.add_argument("--dataset", default="llm-answer-preference-v1")
    args = parser.parse_args()
    upload(args.input, args.dataset)


if __name__ == "__main__":
    main()
