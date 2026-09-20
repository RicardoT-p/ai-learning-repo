import unittest
from evaluate import average


class AverageTest(unittest.TestCase):
    def test_average(self) -> None:
        self.assertEqual(average([0.5, 1.0]), 0.75)
        self.assertEqual(average([]), 0.0)


if __name__ == "__main__":
    unittest.main()
