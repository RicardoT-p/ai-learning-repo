import tempfile
import unittest
from pathlib import Path

from evaluate import evaluate, token_f1
from feedback import connect


class EvaluateTests(unittest.TestCase):
    """验证自动评测计算和反馈数据库结构。"""

    def test_candidate_beats_baseline(self) -> None:
        # 候选回答正确、基线错误，候选应获得更好结果且没有退化案例。
        cases = [{"id": "1", "expected": "北京", "baseline": "上海", "candidate": "北京"}]
        report = evaluate(cases)
        self.assertEqual(report["candidate_exact_match"], 1.0)
        self.assertGreater(token_f1("中国首都是北京", "北京"), 0)
        self.assertEqual(report["regressions"], [])

    def test_feedback_schema(self) -> None:
        # 临时数据库用于确认建表、约束和读取逻辑都能工作。
        with tempfile.TemporaryDirectory() as directory:
            database = connect(Path(directory) / "feedback.sqlite3")
            try:
                database.execute(
                    "INSERT INTO feedback(prompt,response,rating,created_at) VALUES(?,?,?,?)",
                    ("问题", "回答", 5, "2026-01-01T00:00:00+00:00"),
                )
                self.assertEqual(database.execute("SELECT rating FROM feedback").fetchone(), (5,))
            finally:
                # Windows会锁定未关闭的SQLite文件，所以测试结束前必须显式关闭。
                database.close()


if __name__ == "__main__":
    unittest.main()
