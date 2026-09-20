"""项目 9：使用 Ragas 评测回答，并可选地把调用轨迹发给 Phoenix。"""

import argparse
import asyncio
import json
import os
from pathlib import Path


def load_cases(path: Path) -> list[dict]:
    """加载 JSONL 测试集。"""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def average(values: list[float]) -> float:
    """空列表返回 0，避免生成报告时除以零。"""
    return round(sum(values) / len(values), 4) if values else 0.0


async def evaluate(cases: list[dict], model: str, trace: bool) -> dict:
    """逐条计算回答与参考答案之间的事实正确性。"""
    from openai import AsyncOpenAI
    from ragas.llms import llm_factory
    from ragas.metrics.collections import FactualCorrectness

    if trace:
        # Phoenix 地址可通过 PHOENIX_COLLECTOR_ENDPOINT 配置。
        from phoenix.otel import register
        register(project_name="rag-eval-learning", auto_instrument=True)

    scorer = FactualCorrectness(llm=llm_factory(model, client=AsyncOpenAI()))
    results = []
    for case in cases:
        result = await scorer.ascore(response=case["response"], reference=case["reference"])
        results.append({"id": case["id"], "factual_correctness": float(result.value)})

    scores = [item["factual_correctness"] for item in results]
    return {"model": model, "average_score": average(scores), "cases": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ragas + Phoenix RAG 评测")
    parser.add_argument("--cases", type=Path, default=Path("cases.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("output/report.json"))
    parser.add_argument("--model", default=os.getenv("RAGAS_MODEL", "gpt-4o-mini"))
    parser.add_argument("--trace", action="store_true", help="把调用轨迹发送给 Phoenix")
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY；本项目会产生少量模型 API 费用")
    report = asyncio.run(evaluate(load_cases(args.cases), args.model, args.trace))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
