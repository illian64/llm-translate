from unittest import TestCase

from app.dto import Part


class StructTest(TestCase):
    def test_is_numeric_or_empty(self):
        self.assertEqual(False, Part("1 000 000 c", False).is_numeric_or_empty())

        self.assertEqual(True, Part("1.23", False).is_numeric_or_empty())
        self.assertEqual(True, Part("1,23", False).is_numeric_or_empty())
        self.assertEqual(True, Part("  ", False).is_numeric_or_empty())
        self.assertEqual(True, Part("1 000 000", False).is_numeric_or_empty())
        self.assertEqual(True, Part("Ⅻ", False).is_numeric_or_empty())
        self.assertEqual(True, Part("...", False).is_numeric_or_empty())
