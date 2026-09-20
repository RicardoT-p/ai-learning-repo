"""项目 10：用 Ray Data 并行处理 JSONL 数据。"""

import argparse
import hashlib
from pathlib import Path


def valid_record(row: dict) -> bool:
    """过滤缺失文本和过短文本。函数放在顶层，Ray 才容易序列化。"""
    return isinstance(row.get("text"), str) and len(row["text"].strip()) >= 15


def add_features(row: dict) -> dict:
    """增加长度和稳定哈希，后续可用于质量分析与去重。"""
    text = row["text"].strip()
    return {
        **row,
        "text": text,
        "char_count": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def run(input_file: Path, output_dir: Path) -> int:
    """启动本地 Ray，执行过滤、映射并输出 Parquet。"""
    import ray

    ray.init(ignore_reinit_error=True)
    try:
        dataset = ray.data.read_json(str(input_file), lines=True)
        result = dataset.filter(valid_record).map(add_features).materialize()
        row_count = result.count()
        output_dir.mkdir(parents=True, exist_ok=True)
        result.write_parquet(str(output_dir))
        return row_count
    finally:
        # 即使中途失败也关闭 Ray，避免 PyCharm 退出后残留进程。
        ray.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ray Data 分布式处理示例")
    parser.add_argument("--input", type=Path, default=Path("sample.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    print(f"处理完成，共输出 {run(args.input, args.output)} 条记录")


if __name__ == "__main__":
    main()
