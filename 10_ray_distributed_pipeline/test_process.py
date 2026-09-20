import unittest
from process import add_features, valid_record


class TransformTest(unittest.TestCase):
    def test_filter_and_features(self) -> None:
        self.assertFalse(valid_record({"text": "太短"}))
        record = add_features({"id": "1", "text": "  这是一段足够长的分布式处理测试文本。  "})
        self.assertEqual(record["char_count"], len(record["text"]))
        self.assertEqual(len(record["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
