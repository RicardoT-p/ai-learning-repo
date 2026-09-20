"""项目 6：用 Polars 处理数据，用 DuckDB 生成质量报告。"""

import argparse
import json
from pathlib import Path


def duplicate_rows(total_rows: int, unique_rows: int) -> int:
    """重复行数 = 总行数 - 唯一内容数。"""
    return max(total_rows - unique_rows, 0)


def build_parquet(input_file: Path, parquet_file: Path) -> None:
    """惰性读取 JSONL，增加质量特征，并保存为 Parquet。"""
    import polars as pl

    parquet_file.parent.mkdir(parents=True, exist_ok=True)
    (
        pl.scan_ndjson(input_file)
        .with_columns(
            pl.col("text").str.len_chars().alias("char_count"),
            # 同样的文本会得到同样的哈希，便于统计精确重复。
            pl.col("text").hash(seed=0).alias("content_hash"),
        )
        .sink_parquet(parquet_file)
    )


def analyze(parquet_file: Path) -> dict:
    """直接查询 Parquet，无需先把整份数据装进 Python 内存。"""
    import duckdb

    database = duckdb.connect()
    total, average, minimum, maximum, unique = database.execute(
        """SELECT COUNT(*), AVG(char_count), MIN(char_count), MAX(char_count),
                  COUNT(DISTINCT content_hash) FROM read_parquet(?)""",
        [str(parquet_file)],
    ).fetchone()
    source_rows = database.execute(
        """SELECT source, COUNT(*) AS rows FROM read_parquet(?)
           GROUP BY source ORDER BY rows DESC""",
        [str(parquet_file)],
    ).fetchall()
    database.close()
    return {
        "total_rows": total,
        "unique_texts": unique,
        "duplicate_rows": duplicate_rows(total, unique),
        "average_chars": round(average or 0, 2),
        "min_chars": minimum or 0,
        "max_chars": maximum or 0,
        "rows_by_source": {source: rows for source, rows in source_rows},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Polars + DuckDB 数据质量分析")
    parser.add_argument("--input", type=Path, default=Path("sample.jsonl"))
    parser.add_argument("--parquet", type=Path, default=Path("output/data.parquet"))
    parser.add_argument("--report", type=Path, default=Path("output/report.json"))
    args = parser.parse_args()
    build_parquet(args.input, args.parquet)
    report = analyze(args.parquet)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
