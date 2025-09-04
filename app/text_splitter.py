import pysbd
from blingfire import text_to_sentences

from app.dto import TranslatePart, Part
from app.params import TextSplitParams


def is_arr_fin(arr: list, i):
    return len(arr) - 1 == i


def split_by_sentences(text: str, split_params: TextSplitParams, language="en"):
    if split_params.sentence_splitter == 'blingfire':
        return text_to_sentences(text).splitlines(False)
    else:
        seg = pysbd.Segmenter(language=language, clean=False)
        result = []
        for s in seg.segment(text):
            result.append(s.strip())

        return result


def split_text(processed_text: str, split_params: TextSplitParams, language="en"):
    result: list[Part] = []

    # no split
    if not split_params.split_enabled():
        part = Part(processed_text, False)
        result.append(part)

        return result
    else:
        # split by paragraphs
        paragraphs = processed_text.splitlines(False)

        if split_params.split_by_paragraphs_and_length:
            parts_in_paragraph: list[list[str]] = []
            part_length = 0
            # current_part = 0
            part_in_paragraph: list[str] = []
            for i, paragraph in enumerate(paragraphs):
                if part_length == 0 or part_length + len(paragraph) <= split_params.split_expected_length:
                    part_in_paragraph.append(paragraph)
                    part_length += len(paragraph)
                else:
                    parts_in_paragraph.append(part_in_paragraph)
                    part_in_paragraph = [paragraph]
                    part_length = len(paragraph)

            parts_in_paragraph.append(part_in_paragraph)

            for part_in_paragraph in parts_in_paragraph:
                result.append(Part("\n".join(part_in_paragraph), True))

            return result

        if split_params.split_by_paragraphs_only:
            for i, paragraph in enumerate(paragraphs):
                part = Part(paragraph, not is_arr_fin(paragraphs, i))
                result.append(part)

            return result

        # split by sentences
        sentences_in_paragraph: list[list[str]] = []
        for paragraph in paragraphs:
            sentences = split_by_sentences(paragraph, split_params, language)
            sentences_in_paragraph.append(sentences)

        if split_params.split_by_sentences_and_length:
            sentences_part = ""
            arr_fin = False
            for i, sentences_list in enumerate(sentences_in_paragraph):
                if len(sentences_list) == 0:
                    sentences_part = sentences_part + "\n"
                for j, sentence in enumerate(sentences_list):
                    if not sentence:
                        sentences_part = sentences_part + "\n"
                        pass
                    if sentence == "" or len(sentences_part) + len(sentence) <= split_params.split_expected_length:
                        if is_arr_fin(sentences_in_paragraph, i) and is_arr_fin(sentences_list, j):
                            sentences_part = sentences_part + sentence
                        elif j == len(sentences_list) - 1:
                            sentences_part = sentences_part + sentence + "\n"
                        else:
                            sentences_part = sentences_part + sentence + " "
                    else:
                        part = Part(sentences_part.strip(), arr_fin)
                        result.append(part)
                        if is_arr_fin(sentences_in_paragraph, i) and is_arr_fin(sentences_list, j):
                            sentences_part = sentence
                        elif is_arr_fin(sentences_list, j):
                            sentences_part = sentence + "\n"
                        else:
                            sentences_part = sentence + " "
                    arr_fin = is_arr_fin(sentences_list, j)

            result.append(Part(sentences_part, False))

            return result

        if split_params.split_by_sentences_only:
            for i, sentences_list in enumerate(sentences_in_paragraph):
                if len(sentences_list) == 0:
                    result.append(Part("", True))
                for j, sentence in enumerate(sentences_list):
                    result.append(Part(sentence, is_arr_fin(sentences_list, j) and not is_arr_fin(sentences_in_paragraph, i)))

            return result

        raise ValueError("Incorrect split params - can't split: " + str(split_params))


def join_text(parts: list[Part]):
    result = ""
    translate_parts: list[TranslatePart] = []
    for i, part in enumerate(parts):
        translate_part = TranslatePart(text=part.text, translate=part.translate, paragraph_end=part.paragraph_end)
        translate_parts.append(translate_part)
        result = result + part.translate
        if not is_arr_fin(parts, i):
            if part.paragraph_end:
                result = result + "\n"
            else:
                result = result + " "

    return result, translate_parts
