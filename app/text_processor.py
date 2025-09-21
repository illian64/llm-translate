import logging
import re

from app.params import TextProcessParams

logger = logging.getLogger('uvicorn')


def pre_process(params: TextProcessParams, original_text: str) -> str:
    processed_text = replace_text_from_to(original_text, params.replace_text_from_to)

    if params.replace_non_standard_new_lines_chars:
        processed_text = replace_non_standard_new_lines_chars(processed_text)

    if params.remove_multiple_spaces:
        processed_text = remove_multiple_spaces(processed_text)

    if params.replace_not_text_chars:
        processed_text = replace_not_text_chars(
            original_text, params.allowed_chars_ignoring_replace, params.replace_not_text_target_char)

    if params.remove_identical_characters:
        processed_text = remove_identical_characters(processed_text, params.remove_identical_characters_max_repeats)

    if params.remove_repeated_words:
        processed_text = remove_repeated_words(processed_text, params.remove_repeated_words_max_repeats)

    return processed_text


def replace_not_text_chars(text: str, allowed_chars_ignoring_replace: set, replace_not_text_target_char: str) -> str:
    result = ""
    replaced_chars = []
    for char in text:
        if char.isalpha() or char.isdigit() or char in allowed_chars_ignoring_replace:
            result = result + char
        else:
            result = result + replace_not_text_target_char
            replaced_chars.append(char)

    if len(replaced_chars) > 0:
        replaced_chars_set = set(replaced_chars)
        logger.info("Replaced chars in text {0}: {1}".format(text, replaced_chars_set))

    return result


def replace_non_standard_new_lines_chars(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\n\r", "\n").replace("\r", "\n")


def remove_identical_characters(text, remove_identical_characters_max_repeats):
    # Удаляет символы, повторяющиеся более max_repeats раз
    pattern = r'([^\d])\1{' + str(remove_identical_characters_max_repeats) + ',}'
    return re.sub(pattern, r'\1' * remove_identical_characters_max_repeats, text)


def remove_multiple_spaces(text: str) -> str:
    while '  ' in text:
        text = text.replace('  ', ' ')

    return text


def replace_text_from_to(text: str, from_to: dict | None) -> str:
    if from_to and len(from_to) > 0:
        for key, value in from_to.items():
            text = text.replace(key, value)

    return text


def remove_repeated_words1(text: str, remove_identical_words_max_repeats) -> str:
    pattern = r'(\b\w+\b)(?:\s*[^\w\s]*\s*\1){' + str(remove_identical_words_max_repeats) + ',}'
    replacement = ' '.join([r'\1'] * remove_identical_words_max_repeats)

    return re.sub(pattern=pattern, repl=replacement, string=text, flags=re.IGNORECASE)





