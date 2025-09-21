from app import params
from app.app_core import AppCore

manifest = {
    "name": "Core plugin",
    "version": "1.0",

    # this is DEFAULT options
    # ACTUAL options is in options/<plugin_name>.json after first run
    "default_options": {
        "default_translate_plugin": "nllb_200",  # default translation engine. Will be auto inited on start
        "init_on_start_plugins": [],  # additional list of engines, that must be init on start
        "sleep_after_translate": 0,  # delay after translate (in seconds, may be decimal, for example 0.1 for 100 ms), if you GPU too hot

        "translation_params": {
            "default_from_lang": "en",  # default from language
            "default_to_lang": "ru",  # default to language
        },

        "text_split_params": {
            "split_by_paragraphs_and_length": True,
            "split_by_sentences_and_length": False,
            "split_expected_length": 1000,

            "split_by_paragraphs_only": False,
            "split_by_sentences_only": False,

            "sentence_splitter": "default"
        },

        "text_processing_params": {
            "apply_for_request": True,  # apply processing params for text to translate
            "apply_for_response": True,  # apply processing params for result text

            "replace_non_standard_new_lines_chars": True,
            "replace_not_text_chars": False,
            # some models has issues with special chars (for example { or }) in text. this option replace all non-digit / non text / non-allowed (allowed_chars_for_replace) chars
            "allowed_chars_ignoring_replace": " .,<>:;\"'-–…?!#@№$%+/\\^&[]=*()«»—\r\t\n",
            # allowed chars for replace with replace_not_text_chars
            "replace_not_text_target_char": " ",  # replace not allowed char to this char

            # replace more than N char consecutive, for example: aaaa -> aaa, bbbbbbb -> bbb
            "remove_identical_characters": True,
            "remove_identical_characters_max_repeats": 3,

            # replace more than N words consecutive, for example: hello, hello, hello, hello, hello, world, hello, hello! -> hello hello hello, world, hello, hello!
            "remove_repeated_words": False,
            "remove_repeated_words_max_repeats": 3,

            "remove_multiple_spaces": True, # replace two or more space to one
            "replace_text_from_to": {  # additional replace variants, from : to
            },
        },

        "cache_params": {
            "enabled": True,  # enable/disable translate cache
            "file": "cache/cache.db",  # path to cache file
            "disable_for_plugins": ["no_translate"], # list of plugin names without cache
            "expire_days": 0,  # 0 - without expire
        },

        "file_processing_params": {
            "directory_in": "files_processing/in",
            "directory_out": "files_processing/out",
            "preserve_original_text": True,
            "overwrite_processed_files": True
        },
    },
}


def start(core: AppCore):
    return manifest


def start_with_options(core: AppCore, manifest: dict):
    options = manifest["options"]

    core.default_translate_plugin = options["default_translate_plugin"]
    core.init_on_start_plugins = options["init_on_start_plugins"]
    core.sleep_after_translate = options["sleep_after_translate"]

    core.translation_params = params.read_translation_params(manifest)
    core.text_split_params = params.read_text_split_params(manifest)
    core.text_process_params = params.read_text_process_params(manifest)
    core.cache_params = params.read_cache_params(manifest)
    core.file_processing_params = params.read_file_processing_params(manifest)


    return manifest
