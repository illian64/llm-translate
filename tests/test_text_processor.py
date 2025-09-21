from unittest import TestCase

from app import text_processor

allowed_chars_ignoring_replace = set(" .,<>:;\"'-…?!#@№$%+/\\^&[]=*()—\r\t\n")


class TextProcessorTest(TestCase):
    def test_replace_not_text_chars_eng_rus_digits(self):
        text = "Южно-эфиопский грач увёл мышь за хобот на съезд ящериц. Quick wafting zephyrs vex bold Jim. 1234567890"
        processed = text_processor.replace_not_text_chars(text, allowed_chars_ignoring_replace, "|")
        self.assertEqual(text, processed)

    def test_replace_not_text_chars_with_japan_german_chars(self):
        text = "こんにちわ / Ü ü, Ö ö, Ä ä, ẞ ß"
        processed = text_processor.replace_not_text_chars(text, allowed_chars_ignoring_replace, "|")
        self.assertEqual(text, processed)

    def test_replace_not_text_chars_with_ignored_chars(self):
        text = "{ }"
        processed = text_processor.replace_not_text_chars(text, allowed_chars_ignoring_replace, "|")
        self.assertEqual("| |", processed)

    def test_trim_duplicate_characters(self):
        text = "soooooome textttttt оёёёёёёё 12222223 qÖÖÖÖÖÖöööööwe こここここ 00000"
        processed = text_processor.remove_identical_characters(text, 3)
        self.assertEqual("sooome texttt оёёё 12222223 qÖÖÖöööwe こここ 00000", processed)

        text = "soooooome textttttt оёёёёёёё 12222223 qÖÖÖÖÖÖöööööwe こここここ 00000"
        processed = text_processor.remove_identical_characters(text, 4)
        self.assertEqual("soooome textttt оёёёё 12222223 qÖÖÖÖööööwe ここここ 00000", processed)

    def test_remove_multiple_spaces(self):
        text = "q  w     e       r     t y"
        processed = text_processor.remove_multiple_spaces(text)
        self.assertEqual("q w e r t y", processed)

    def test_replace_text_from_to(self):
        text = "qwe 123 asd zxc"
        processed = text_processor.replace_text_from_to(text, None)
        self.assertEqual(text, processed)

        processed = text_processor.replace_text_from_to(text, {"123": "456", "zxc": "789"})
        self.assertEqual("qwe 456 asd 789", processed)

    def test_remove_multiple_words(self):
        text = "Hello, hello, hello, hello, hello, world, hello, hello! t1 t1 t1 t1 t1."
        processed = text_processor.remove_repeated_words(text, 3)
        self.assertEqual("Hello Hello Hello, world, hello, hello! t1 t1 t1.", processed)

        processed = text_processor.remove_repeated_words(text, 4)
        self.assertEqual("Hello Hello Hello Hello, world, hello, hello! t1 t1 t1 t1.", processed)
