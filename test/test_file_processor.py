from unittest import TestCase

from app import file_processor


class FileProcessTest(TestCase):
    def test_encoding(self):
        content = file_processor.read_file_with_fix_encoding("../files/test_encoding_ansi.txt")
        self.assertEqual("Hello, World. Привет, Мир. Ёё.", content)
