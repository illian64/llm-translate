from dataclasses import dataclass


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

    def split_enabled(self) -> bool:
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
    remove_identical_characters_max_repeats: int

    remove_repeated_words: bool
    remove_repeated_words_max_repeats: int

    remove_multiple_spaces: bool
    replace_text_from_to: dict


@dataclass
class CacheParams:
    enabled: bool
    file: str
    disable_for_plugins: list[str]
    expire_days: int


@dataclass
class FileProcessingParams:
    directory_in: str
    directory_out: str
    preserve_original_text: bool
    overwrite_processed_files: bool


@dataclass
class TranslateProgress:
    unit: str
    ascii: bool
    desc: str


@dataclass
class FileProcessingTextFormat:
    original_prefix: str
    original_postfix: str
    translate_prefix: str
    translate_postfix: str

    def original_text(self, text: str) -> str:
        return self.original_prefix + text + self.original_postfix

    def translate_text(self, text: str) -> str:
        return self.translate_prefix + text + self.translate_postfix


def read_plugin_translate_params(manifest: dict):
    manifest["options"]["translation_params_struct"] = read_translation_params(manifest)
    manifest["options"]["text_split_params_struct"] = read_text_split_params(manifest)
    manifest["options"]["text_process_params_struct"] = read_text_process_params(manifest)


def read_plugin_file_processing_params(manifest: dict):
    manifest["options"]["translation_params_struct"] = read_translation_params(manifest)


def read_translation_params(manifest: dict) -> TranslationParams | None:
    options = manifest["options"]
    if "translation_params" not in options:
        return None

    return TranslationParams(
        default_from_lang=options["translation_params"]["default_from_lang"],
        default_to_lang=options["translation_params"]["default_to_lang"]
    )


def read_text_split_params(manifest: dict) -> TextSplitParams | None:
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


def read_text_process_params(manifest: dict) -> TextProcessParams | None:
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
        remove_identical_characters_max_repeats=options["text_processing_params"].get("remove_identical_characters_max_repeats", 3),

        remove_repeated_words=options["text_processing_params"].get("remove_repeated_words", False),
        remove_repeated_words_max_repeats=options["text_processing_params"].get("remove_repeated_words_max_repeats", 3),

        remove_multiple_spaces=options["text_processing_params"].get("remove_multiple_spaces", True),
        replace_text_from_to=options["text_processing_params"].get("replace_text_from_to", {}),
    )


def read_cache_params(manifest: dict) -> CacheParams:
    options = manifest["options"]

    return CacheParams(
        enabled=options["cache_params"]["enabled"],
        file=options["cache_params"]["file"],
        disable_for_plugins=options["cache_params"]["disable_for_plugins"],
        expire_days=options["cache_params"]["expire_days"],
    )


def read_file_processing_params(manifest: dict) -> FileProcessingParams | None:
    options = manifest["options"]
    if "file_processing_params" not in options:
        return None

    return FileProcessingParams(
        directory_in=options["file_processing_params"]["directory_in"],
        directory_out=options["file_processing_params"]["directory_out"],
        preserve_original_text=options["file_processing_params"]["preserve_original_text"],
        overwrite_processed_files=options["file_processing_params"]["overwrite_processed_files"],
    )


def read_plugin_file_processing_text_format(options: dict):
    return FileProcessingTextFormat(
        original_prefix=options["text_format"]["original_prefix"],
        original_postfix=options["text_format"]["original_postfix"],
        translate_prefix=options["text_format"]["translate_prefix"],
        translate_postfix=options["text_format"]["translate_postfix"],
    )


tp: TranslateProgress = TranslateProgress(unit="part", ascii=True, desc="translate parts: ")
