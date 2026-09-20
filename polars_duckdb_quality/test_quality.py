import unittest
from quality import duplicate_rows


class QualityTest(unittest.TestCase):
    def test_duplicate_count(self) -> None:
        self.assertEqual(duplicate_rows(10, 7), 3)
        self.assertEqual(duplicate_rows(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
