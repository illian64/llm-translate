from pathlib import Path
from unittest import TestCase

from app import file_processor


class FileProcessTest(TestCase):
    test_dir = Path(__file__).parent.absolute()

    def test_encoding(self):
        content = file_processor.read_file_with_fix_encoding(str(self.test_dir / "files/test_encoding_ansi.txt"))
        self.assertEqual("Hello, World. Привет, Мир. Ёё.", content)
