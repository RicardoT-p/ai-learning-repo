import unittest
from types import SimpleNamespace

from pipeline import keep_useful_text


class FilterTest(unittest.TestCase):
    def test_short_text_is_removed(self) -> None:
        self.assertFalse(keep_useful_text(SimpleNamespace(text="太短"), min_chars=10))
        self.assertTrue(keep_useful_text(SimpleNamespace(text="这是一段足够长的训练文本"), min_chars=10))


if __name__ == "__main__":
    unittest.main()
