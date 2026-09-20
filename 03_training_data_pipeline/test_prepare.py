import json
import tempfile
import unittest
from pathlib import Path

from prepare import prepare


class PrepareTests(unittest.TestCase):
    """用小型临时文件验证清洗流水线的核心行为。"""

    def test_filter_redact_and_deduplicate(self) -> None:
        # 同一长文本放两次，用于验证精确去重；同时包含需要遮盖的邮箱。
        text = "这是一段足够长的训练文本，包含联系邮箱 test@example.com。" * 4
        # TemporaryDirectory在测试结束后自动清理，不污染项目目录。
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "raw.jsonl"
            target = Path(directory) / "clean.jsonl"
            # 三条输入依次是：过短、有效、与有效文本重复。
            source.write_text(
                "\n".join(json.dumps({"id": index, "text": value}, ensure_ascii=False) for index, value in enumerate(["短", text, text])),
                encoding="utf-8",
            )
            stats = prepare(source, target, min_chars=20)
            output = target.read_text(encoding="utf-8")
            # 验证每个分支都按预期计数，并确认邮箱已被替换。
            self.assertEqual(stats["kept"], 1)
            self.assertEqual(stats["short"], 1)
            self.assertEqual(stats["exact_duplicate"], 1)
            self.assertIn("<EMAIL>", output)


if __name__ == "__main__":
    unittest.main()
