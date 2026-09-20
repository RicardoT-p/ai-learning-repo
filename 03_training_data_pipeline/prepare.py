"""项目3：把原始JSONL文本清洗、脱敏、去重后生成训练数据。"""

import argparse
import hashlib
import json
import re
from pathlib import Path


# 预编译正则，避免处理每条记录时重复解析表达式。
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
# 英文按完整单词切分，中文按单字切分，作为简化的相似度特征。
TOKEN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", re.UNICODE)


def clean_text(text: str) -> str:
    """统一空白字符，并用占位符遮盖示例中的邮箱和中国大陆手机号。"""
    # split再join可把换行、制表符和连续空格统一成单个空格。
    text = " ".join(text.split())
    text = EMAIL.sub("<EMAIL>", text)
    return PHONE.sub("<PHONE>", text)


def simhash(text: str) -> int:
    """把文本压缩为64位SimHash；内容越相似，二进制位通常越接近。"""
    tokens = TOKEN.findall(text.lower())
    if not tokens:
        return 0
    # 连续5个token构成一个shingle，比单个词更能保留局部语序。
    shingles = [" ".join(tokens[index : index + 5]) for index in range(max(1, len(tokens) - 4))]
    # 每一位分别投票：哈希为1加一票，为0减一票。
    weights = [0] * 64
    for shingle in shingles:
        # blake2b生成稳定的64位值；Python内置hash会随进程随机变化，不适合落盘数据。
        value = int.from_bytes(hashlib.blake2b(shingle.encode(), digest_size=8).digest())
        for bit in range(64):
            weights[bit] += 1 if value >> bit & 1 else -1
    # 票数非负的位设为1，最终合成一个64位整数指纹。
    return sum((1 << bit) for bit, weight in enumerate(weights) if weight >= 0)


def prepare(input_path: Path, output_path: Path, min_chars: int = 80) -> dict[str, int]:
    """逐行处理原始JSONL，返回每种保留或淘汰原因的数量。"""
    # 分原因计数，真实项目可用这些数字监控数据质量和规则变化。
    stats = {"read": 0, "invalid": 0, "short": 0, "exact_duplicate": 0, "near_duplicate": 0, "kept": 0}
    # SHA-256集合判断完全相同的文本，查询平均复杂度为O(1)。
    exact_seen: set[str] = set()
    # 保存已接收文本的SimHash，用于判断近似重复。
    fingerprints: list[int] = []

    # JSONL逐行读取，不需要把整个输入文件一次性放入内存。
    with input_path.open(encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
        for line in source:
            # 空行不是坏数据，直接跳过且不计入read。
            if not line.strip():
                continue
            stats["read"] += 1
            try:
                # 每行必须是JSON对象，并且包含可清洗的text字段。
                record = json.loads(line)
                text = clean_text(record["text"])
            except (json.JSONDecodeError, KeyError, TypeError):
                stats["invalid"] += 1
                continue
            # 太短的文本通常缺少训练价值，阈值由命令行控制。
            if len(text) < min_chars:
                stats["short"] += 1
                continue
            # 先做便宜且精确的哈希去重，再做成本更高的相似度比较。
            digest = hashlib.sha256(text.encode()).hexdigest()
            if digest in exact_seen:
                stats["exact_duplicate"] += 1
                continue
            fingerprint = simhash(text)
            # ponytail: O(n²)适合学习样本；百万级数据改用DataTrove的MinHash分桶去重。
            # 异或后为1的位代表两指纹不同，bit_count得到汉明距离。
            if any((fingerprint ^ old).bit_count() <= 3 for old in fingerprints):
                stats["near_duplicate"] += 1
                continue
            # 只有真正保留的记录才加入去重状态，避免被淘汰数据影响后续判断。
            exact_seen.add(digest)
            fingerprints.append(fingerprint)
            record["text"] = text
            # ensure_ascii=False让中文直接保存，而不是写成\uXXXX。
            target.write(json.dumps(record, ensure_ascii=False) + "\n")
            stats["kept"] += 1
    return stats


def main() -> None:
    """解析输入输出参数，运行流水线并保存统计报告。"""
    parser = argparse.ArgumentParser(description="训练文本清洗、脱敏和去重")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("clean.jsonl"))
    parser.add_argument("--stats", type=Path, default=Path("stats.json"))
    parser.add_argument("--min-chars", type=int, default=80)
    args = parser.parse_args()
    stats = prepare(args.input, args.output, args.min_chars)
    # 统计单独写成JSON，便于后续画图或比较不同清洗规则。
    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
