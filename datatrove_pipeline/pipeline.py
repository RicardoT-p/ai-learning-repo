"""项目 5：使用 DataTrove 清洗大模型训练语料。"""

import argparse
from functools import partial
from pathlib import Path


def keep_useful_text(document, min_chars: int = 20) -> bool:
    """只保留长度达标、并且不是纯空白的文本。"""
    return len(document.text.strip()) >= min_chars


def run(input_dir: Path, output_dir: Path, logs_dir: Path, min_chars: int) -> None:
    """组装并执行 DataTrove 本地流水线。"""
    # 放在函数里导入：即使还没安装 DataTrove，也可以先运行下面的单元测试。
    from datatrove.executor import LocalPipelineExecutor
    from datatrove.pipeline.filters import LambdaFilter
    from datatrove.pipeline.readers import JsonlReader
    from datatrove.pipeline.tokens import TokensCounter
    from datatrove.pipeline.writers import JsonlWriter

    # DataTrove 的思路是：Reader -> 若干处理步骤 -> Writer。
    pipeline = [
        JsonlReader(data_folder=str(input_dir)),
        LambdaFilter(
            filter_function=partial(keep_useful_text, min_chars=min_chars),
            # 被过滤的数据单独保存，方便抽查规则是否过严。
            exclusion_writer=JsonlWriter(
                output_folder=str(output_dir / "removed"),
                output_filename="${rank}.jsonl",
                compression=None,
            ),
        ),
        TokensCounter(),  # 训练成本通常按 token 估算。
        JsonlWriter(
            output_folder=str(output_dir / "kept"),
            output_filename="${rank}.jsonl",
            compression=None,
        ),
    ]
    LocalPipelineExecutor(
        pipeline=pipeline,
        logging_dir=str(logs_dir),
        tasks=1,
        workers=1,
    ).run()


def main() -> None:
    parser = argparse.ArgumentParser(description="DataTrove 训练语料清洗示例")
    parser.add_argument("--input", type=Path, default=Path("input"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--logs", type=Path, default=Path("logs"))
    parser.add_argument("--min-chars", type=int, default=20)
    args = parser.parse_args()
    run(args.input, args.output, args.logs, args.min_chars)


if __name__ == "__main__":
    main()
