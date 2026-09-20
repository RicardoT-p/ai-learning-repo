"""项目4B：用SQLite保存人工对大模型回答的评分、标签和备注。"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# 表结构直接由程序创建，初学阶段不需要额外的数据库迁移工具。
SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    tags TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
)
"""


def connect(path: Path) -> sqlite3.Connection:
    """连接SQLite文件，并确保feedback表已经存在。"""
    database = sqlite3.connect(path)
    database.execute(SCHEMA)
    return database


def main() -> None:
    """提供add、list、export三个子命令管理反馈数据。"""
    parser = argparse.ArgumentParser(description="本地LLM人工反馈库")
    parser.add_argument("--db", type=Path, default=Path("feedback.sqlite3"))
    # 子命令让三种操作共享同一个脚本和数据库参数。
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add负责写入一条人工反馈。
    add = subparsers.add_parser("add")
    add.add_argument("--prompt", required=True)
    add.add_argument("--response", required=True)
    add.add_argument("--rating", required=True, type=int, choices=range(1, 6))
    add.add_argument("--tags", default="")
    add.add_argument("--notes", default="")

    # list在终端查看全部反馈；export把数据导出成训练常用的JSONL。
    subparsers.add_parser("list")
    export = subparsers.add_parser("export")
    export.add_argument("--output", type=Path, default=Path("feedback.jsonl"))
    args = parser.parse_args()

    # Connection上下文成功时自动提交事务，发生异常时自动回滚。
    with connect(args.db) as database:
        if args.command == "add":
            # 使用?占位符传值，避免字符串拼接造成SQL注入或引号错误。
            database.execute(
                "INSERT INTO feedback(prompt,response,rating,tags,notes,created_at) VALUES(?,?,?,?,?,?)",
                (args.prompt, args.response, args.rating, args.tags, args.notes, datetime.now(timezone.utc).isoformat()),
            )
        else:
            # 从表结构动态获得列名，再把每一行转换为容易导出的字典。
            columns = [item[1] for item in database.execute("PRAGMA table_info(feedback)")]
            rows = [dict(zip(columns, row)) for row in database.execute("SELECT * FROM feedback ORDER BY id")]
            if args.command == "list":
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                # JSONL每行一条完整记录，适合流式读取和追加处理。
                args.output.write_text(
                    "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
                )
                print(f"导出 {len(rows)} 条 -> {args.output}")


if __name__ == "__main__":
    main()
