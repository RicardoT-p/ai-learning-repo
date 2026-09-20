import tempfile
import unittest
from pathlib import Path

from upload import load_records


class LoadRecordsTest(unittest.TestCase):
    def test_missing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text('{"prompt":"问题","response_a":"回答"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)


if __name__ == "__main__":
    unittest.main()
