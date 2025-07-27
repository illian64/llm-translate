from dataclasses import dataclass, field


# dict_field: dict = field(default_factory=lambda: {})
@dataclass
class Request:
    text: str
    from_lang: str | None
    to_lang: str | None
    translator_plugin: str | None


@dataclass
class Sentence:
    text: str


@dataclass
class Part:
    text: str
    translate: str
    paragraph_end: bool
    cache_found: bool

    def is_numeric_or_empty(self):
        processed_text = (self.text
                          .replace(" ", "")
                          .replace(",", "")
                          .replace(".", ""))

        return processed_text.isnumeric() or len(processed_text) == 0

    def need_to_translate(self):
        return not self.cache_found and self.text and self.text != "" and not self.is_numeric_or_empty()

    def __init__(self, text: str, paragraph_end: bool):
        self.text = text
        self.translate = ""
        self.paragraph_end = paragraph_end
        self.cache_found = False


@dataclass
class TranslateStruct:
    req: Request
    processed_text: str
    parts: list[Part]


@dataclass
class TranslationParams:
    default_from_lang: str
    default_to_lang: str


@dataclass
class TextSplitParams:
    split_by_paragraphs_and_length: bool
    split_by_sentences_and_length: bool
    split_expected_length: int

    split_by_paragraphs_only: bool
    split_by_sentences_only: bool

    # pysbd (default) / blingfire
    sentence_splitter: str

    def split_enabled(self):
        return (self.split_by_paragraphs_only or self.split_by_paragraphs_and_length
                or self.split_by_sentences_and_length or self.split_by_sentences_only)


@dataclass
class TextProcessParams:
    apply_for_request: bool
    apply_for_response: bool

    replace_non_standard_new_lines_chars: bool
    replace_not_text_chars: bool
    allowed_chars_ignoring_replace: set
    replace_not_text_target_char: str

    remove_identical_characters: bool
    remove_identical_characters_extra_chars: str
    remove_identical_characters_max_repeats: int

    remove_multiple_spaces: bool
    replace_text_from_to: dict


@dataclass
class CacheParams:
    enabled: bool
    file: str
    disable_for_plugins: list[str]
    expire_days: int


@dataclass
class TranslateProgress:
    unit: str
    ascii: bool
    desc: str


tp: TranslateProgress = TranslateProgress(unit="part", ascii=True, desc="translate parts: ")


def read_plugin_params(manifest: dict):
    manifest["options"]["translation_params_struct"] = read_translation_params(manifest)
    manifest["options"]["text_split_params_struct"] = read_text_split_params(manifest)
    manifest["options"]["text_process_params_struct"] = read_text_process_params(manifest)


def read_translation_params(manifest: dict):
    options = manifest["options"]
    if "translation_params" not in options:
        return None

    return TranslationParams(
        default_from_lang=options["translation_params"]["default_from_lang"],
        default_to_lang=options["translation_params"]["default_to_lang"]
    )


def read_text_split_params(manifest: dict):
    options = manifest["options"]

    if "text_split_params" not in options:
        return None

    return TextSplitParams(
        split_by_paragraphs_and_length=options["text_split_params"].get("split_by_paragraphs_and_length", False),
        split_by_sentences_and_length=options["text_split_params"].get("split_by_sentences_and_length", False),
        split_expected_length=options["text_split_params"].get("split_expected_length", 1000),

        split_by_paragraphs_only=options["text_split_params"].get("split_by_paragraphs_only", False),
        split_by_sentences_only=options["text_split_params"].get("split_by_sentences_only", False),

        sentence_splitter=options["text_split_params"].get("sentence_splitter", "default"),
    )


def read_text_process_params(manifest: dict):
    options = manifest["options"]

    if "text_processing_params" not in options:
        return None

    return TextProcessParams(
        apply_for_request=options["text_processing_params"].get("apply_for_request", True),
        apply_for_response=options["text_processing_params"].get("apply_for_response", True),

        replace_non_standard_new_lines_chars=options["text_processing_params"].get("replace_non_standard_new_lines_chars", True),
        replace_not_text_chars=options["text_processing_params"].get("replace_not_text_chars", False),
        allowed_chars_ignoring_replace=options["text_processing_params"].get("allowed_chars_ignoring_replace", " .,<>:;\"'-–…?!#@№$%+/\\^&[]=*()«»—\r\t\n"),
        replace_not_text_target_char=options["text_processing_params"].get("replace_not_text_target_char", " "),

        remove_identical_characters=options["text_processing_params"].get("remove_identical_characters", False),
        remove_identical_characters_extra_chars=options["text_processing_params"].get("remove_identical_characters_extra_chars", ""),
        remove_identical_characters_max_repeats=options["text_processing_params"].get("remove_identical_characters_max_repeats", 3),

        remove_multiple_spaces=options["text_processing_params"].get("remove_multiple_spaces", True),
        replace_text_from_to=options["text_processing_params"].get("replace_text_from_to", {}),
    )


def read_cache_params(manifest: dict):
    options = manifest["options"]

    return CacheParams(
        enabled=options["cache_params"]["enabled"],
        file=options["cache_params"]["file"],
        disable_for_plugins=options["cache_params"]["disable_for_plugins"],
        expire_days=options["cache_params"]["expire_days"],
    )
