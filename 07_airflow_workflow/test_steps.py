import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "dags"))
from pipeline_steps import clean, extract, quality  # noqa: E402


class PipelineStepsTest(unittest.TestCase):
    def test_complete_local_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = quality(clean(extract(directory)))
            self.assertEqual(report["clean_rows"], 2)


if __name__ == "__main__":
    unittest.main()
