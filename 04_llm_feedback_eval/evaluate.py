"""项目4A：用固定测试集比较候选模型和基线模型的回答质量。"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path


# 英文按单词、中文按单字切分，让两种语言都能做简单的重合度评测。
TOKEN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", re.UNICODE)


def token_f1(prediction: str, expected: str) -> float:
    """计算模型回答与参考答案的token级F1，范围为0到1。"""
    # Counter不仅记录token是否出现，也保留重复次数。
    predicted = Counter(TOKEN.findall(prediction.lower()))
    wanted = Counter(TOKEN.findall(expected.lower()))
    # 两个Counter取&后保留每个token的较小计数，即真正重合的数量。
    overlap = sum((predicted & wanted).values())
    if not predicted or not wanted or not overlap:
        return 0.0
    # precision：回答中的内容有多少命中；recall：参考答案有多少被覆盖。
    precision = overlap / sum(predicted.values())
    recall = overlap / sum(wanted.values())
    # F1是precision和recall的调和平均，任一项很低都会拉低总分。
    return 2 * precision * recall / (precision + recall)


def evaluate(cases: list[dict[str, object]]) -> dict[str, object]:
    """汇总候选/基线得分、人工偏好，并找出候选模型退化的案例。"""
    candidate_scores: list[float] = []
    baseline_scores: list[float] = []
    exact = 0
    failures: list[str] = []
    preferences = Counter()

    for case in cases:
        # get提供默认值，使缺少字段的案例不会直接崩溃。
        expected = str(case.get("expected", ""))
        candidate = str(case.get("candidate", ""))
        baseline = str(case.get("baseline", ""))
        candidate_score = token_f1(candidate, expected)
        baseline_score = token_f1(baseline, expected)
        candidate_scores.append(candidate_score)
        baseline_scores.append(baseline_score)
        # bool在Python中可按0/1累加，因此表达式成立时exact加1。
        exact += candidate.strip().lower() == expected.strip().lower()
        # 候选分数低于基线时记录案例ID，方便回头逐条排查。
        if candidate_score < baseline_score:
            failures.append(str(case.get("id", "unknown")))
        preference = case.get("human_preference")
        if preference in {"candidate", "baseline", "tie"}:
            preferences[str(preference)] += 1

    count = len(cases)
    # 空测试集时返回0而不是除以0，方便流水线稳定运行。
    return {
        "cases": count,
        "candidate_exact_match": exact / count if count else 0.0,
        "candidate_token_f1": sum(candidate_scores) / count if count else 0.0,
        "baseline_token_f1": sum(baseline_scores) / count if count else 0.0,
        "human_preferences": dict(preferences),
        "regressions": failures,
    }


def main() -> None:
    """读取JSONL测试集，生成机器可读的JSON评测报告。"""
    parser = argparse.ArgumentParser(description="比较基线模型和候选模型")
    parser.add_argument("cases", type=Path)
    parser.add_argument("--output", type=Path, default=Path("report.json"))
    args = parser.parse_args()
    # 每一行都是独立案例；忽略空行，便于手工编辑文件。
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = evaluate(cases)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
