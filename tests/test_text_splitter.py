import unittest

from app import text_splitter
from app.dto import Part
from app.params import TextSplitParams

s1 = "Text one."
s2 = "Text two."
s3 = "Text three."
s4 = "Text four."
s5 = "Text five."
s6 = "Text six."
s7 = "Text seven."
s8 = "Text eight."
s9 = "Text nine."

split_txt1 = "Some text. Mr. John Johnson Jr. was born in the U.S.A but earned his Ph.D. in Israel before joining Nike Inc. as an engineer. He also worked at craigslist.org as a business analyst. Some text one. Some text two."
split_txt2 = "Some sentence. Mr. Holmes... This is a new sentence! And This is another one.. Hi "


def get_params():
    return TextSplitParams(
        split_expected_length=20, sentence_splitter="def",
        split_by_paragraphs_only=False, split_by_paragraphs_and_length=False,
        split_by_sentences_only=False, split_by_sentences_and_length=False)


def get_text(*sentences):
    return " ".join(sentences).replace("\n ", "\n")


class ReqProcessorTest(unittest.TestCase):
    def test_split_by_sentences_blingfire(self):
        params = get_params()
        params.sentence_splitter = "blingfire"

        split = text_splitter.split_by_sentences(split_txt1, params)
        exp = ['Some text. Mr. John Johnson Jr. was born in the U.S.A but earned his Ph.D. in Israel before joining Nike Inc. as an engineer.',
               'He also worked at craigslist.org as a business analyst.',
               'Some text one.',
               'Some text two.']
        self.assertEqual(exp, split)

        split = text_splitter.split_by_sentences(split_txt2, params)
        exp = ['Some sentence.',
               'Mr.',
               'Holmes...',
               'This is a new sentence!',
               'And This is another one..',
               'Hi ']
        self.assertEqual(exp, split)

    def test_split_by_sentences_pysbd(self):
        params = get_params()

        split = text_splitter.split_by_sentences(split_txt1, params)
        exp = ['Some text.',
               'Mr. John Johnson Jr. was born in the U.S.A but earned his Ph.D. in Israel before joining Nike Inc. as an engineer.',
               'He also worked at craigslist.org as a business analyst.',
               'Some text one.',
               'Some text two.']
        self.assertEqual(exp, split)

        split = text_splitter.split_by_sentences(split_txt2, params)
        exp = ['Some sentence.',
               'Mr. Holmes...',
               'This is a new sentence!',
               'And This is another one.',
               '.',
               'Hi']
        self.assertEqual(exp, split)

    def test_no_split(self):
        params = get_params()

        text = get_text(s1, s2, s3, s4, s5)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1, s2, s3, s4, s5), False)]

        self.assertEqual(exp, split)

    def test_split_by_few_paragraphs_and_length__long_text_with_one_paragraph(self):
        params = get_params()
        params.split_by_paragraphs_and_length = True

        text = get_text(s1, s2, s3, s4, s5)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1, s2, s3, s4, s5), True)]

        self.assertEqual(exp, split)

    def test_split_by_few_paragraphs_and_length__short_text_with_one_paragraph(self):
        params = get_params()
        params.split_by_paragraphs_and_length = True

        text = get_text(s1, s2)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1, s2), True)]

        self.assertEqual(exp, split)

    def test_split_by_few_paragraphs_and_length__text_with_few_paragraphs_01(self):
        params = get_params()
        params.split_by_paragraphs_and_length = True
        # text with few paragraphs
        text = get_text(s1 + "\n\n", s2 + "\n", s3, s4 + "\n", s5, s6, s7, s8 + "\n", s9 + "\n", s1)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1 + "\n\n", s2), True),
               Part(get_text(s3, s4), True),
               Part(get_text(s5, s6, s7, s8), True),
               Part(get_text(s9 + "\n", s1), True),]

        self.assertEqual(exp, split)

    def test_split_by_few_paragraphs_and_length__text_with_few_paragraphs_02(self):
        params = get_params()
        params.split_by_paragraphs_and_length = True

        text = get_text(s1 + "\n", s2 + "\n", s3 + "\n", s4 + "\n", s5)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1 + "\n", s2), True),
               Part(get_text(s3), True),
               Part(get_text(s4 + "\n", s5), True),]

        self.assertEqual(exp, split)

    def test_split_by_paragraphs_only_01(self):
        params = get_params()
        params.split_by_paragraphs_only = True
        # text with few paragraphs
        text = get_text(s1 + "\n\n", s2 + "\n", s3, s4 + "\n", s5, s6)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1), True),
               Part(get_text(""), True),
               Part(get_text(s2), True),
               Part(get_text(s3, s4), True),
               Part(get_text(s5, s6), False)]

        self.assertEqual(exp, split)

    def test_split_by_paragraphs_only_02(self):
        params = get_params()
        params.split_by_paragraphs_only = True
        # text with few paragraphs
        split = text_splitter.split_text(s1, params)
        exp = [Part(get_text(s1), True),
               Part(get_text(""), True),
               Part(get_text(s2), True),
               Part(get_text(s3, s4), True),
               Part(get_text(s5, s6), True)]

        self.assertEqual([Part(s1, False)], split)

    def test_split_by_few_sentences_and_length_01(self):
        params = get_params()
        params.split_by_sentences_and_length = True
        params.split_expected_length = 25
        # text with few paragraphs
        text = get_text(s1 + "\n\n", s2 + "\n", s3, s4 + "\n", s5, s6, s7, s8 + "\n", s9 + "\n", s1)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1 + "\n\n", s2), True),
               Part(get_text(s3, s4), True),
               Part(get_text(s5, s6), False),
               Part(get_text(s7, s8), True),
               Part(get_text(s9 + "\n", s1), False),]

        self.assertEqual(exp, split)

    def test_split_by_few_sentences_and_length_02(self):
        params = get_params()
        params.split_by_sentences_and_length = True
        params.split_expected_length = 40
        # text with few paragraphs
        text = get_text(s1 + "\n\n", s2 + "\n", s3, s4 + "\n", s5, s6, s7, s8 + "\n", s9 + "\n", s1)
        split = text_splitter.split_text(text, params)
        exp = [Part(get_text(s1 + "\n\n", s2 + "\n", s3), False),
               Part(get_text(s4 + "\n", s5, s6), False),
               Part(get_text(s7, s8 + "\n", s9), True),
               Part(get_text(s1), False),]

        self.assertEqual(exp, split)

    def test_split_by_few_sentences_and_length_03(self):
        params = get_params()
        params.split_by_sentences_and_length = True
        split = text_splitter.split_text(s1, params)

        self.assertEqual([Part(s1, False)], split)

    def test_split_by_sentences_only_01(self):
        params = get_params()
        params.split_by_sentences_only = True
        split = text_splitter.split_text(s1, params)
        self.assertEqual([Part(s1, False)], split)

    def test_split_by_sentences_only_02(self):
        params = get_params()
        params.split_by_sentences_only = True
        # text with few paragraphs
        text = get_text(s1 + "\n\n", s2 + "\n", s3, s4 + "\n", s5, s6, s7, s8 + "\n", s9 + "\n", s1)
        split = text_splitter.split_text(text, params)
        exp = [Part(s1, True),
               Part("", True),
               Part(s2, True),
               Part(s3, False),
               Part(s4, True),
               Part(s5, False),
               Part(s6, False),
               Part(s7, False),
               Part(s8, True),
               Part(s9, True),
               Part(s1, False),]

        self.assertEqual(exp, split)
