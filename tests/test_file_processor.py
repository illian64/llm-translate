from pathlib import Path
from unittest import TestCase

from app import file_processor
from app.params import FileProcessingContextParams


class FileProcessTest(TestCase):
    test_dir = Path(__file__).parent.absolute()

    def test_encoding(self):
        content = file_processor.read_file_with_fix_encoding(str(self.test_dir / "files/test_encoding_ansi.txt"))
        self.assertEqual("Hello, World. Привет, Мир. Ёё.", content)

    def test_get_context(self):
        items_to_context = ["111", "222", "333", "444", "555"]

        params = FileProcessingContextParams(enabled=True, prompt="Use context: %%context%%", expected_length=9,
                                             include_at_least_one_paragraph=True, paragraph_join_str="\n")

        context = file_processor.get_context(items_to_context, params, "000")
        self.assertEqual("Use context: 333\n444\n555", context)

        context = file_processor.get_context(items_to_context, params, "555")
        self.assertEqual("Use context: 222\n333\n444", context)

        context = file_processor.get_context(items_to_context, params, "444")
        self.assertEqual("Use context: 222\n333\n555", context)

        params.expected_length = 8
        params.paragraph_join_str = " "
        context = file_processor.get_context(items_to_context, params, "000")
        self.assertEqual("Use context: 444 555", context)

        params.expected_length = 2
        params.paragraph_join_str = "\n"
        params.include_at_least_one_paragraph = True
        context = file_processor.get_context(items_to_context, params, "000")
        self.assertEqual("Use context: 555", context)

        params.expected_length = 2
        params.include_at_least_one_paragraph = False
        context = file_processor.get_context(items_to_context, params, "000")
        self.assertEqual(None, context)
