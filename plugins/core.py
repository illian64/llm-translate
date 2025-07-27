from app.app_core import AppCore
from app.struct import TranslationParams, read_text_split_params, \
    read_text_process_params, read_translation_params, read_cache_params


def start(core: AppCore):
    manifest = {
        "name": "Core plugin",
        "version": "1.0",

        # this is DEFAULT options
        # ACTUAL options is in options/<plugin_name>.json after first run
        "default_options": {
            "default_translate_plugin": "lm_studio",  # default translation engine. Will be auto inited on start
            "init_on_start": "",  # additional list of engines, that must be init on start, separated by ","

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
                "remove_identical_characters_extra_chars": "",
                "remove_identical_characters_max_repeats": 3,

                "remove_multiple_spaces": True, # replace two or more space to one
                "replace_text_from_to": {  # additional replace variants, from : to
                },
            },

            "cache_params": {
                "enabled": True,  # enable/disable translate cache
                "file": "cache.db",  # path to cache file
                "disable_for_plugins": ["no_translate"], # list of plugin names without cache
                "expire_days": 0,  # 0 - without expire
            }
        },
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    options = manifest["options"]

    core.default_translate_plugin = options["default_translate_plugin"]
    core.init_on_start = options["init_on_start"]

    core.translation_params = read_translation_params(manifest)
    core.text_split_params = read_text_split_params(manifest)
    core.text_process_params = read_text_process_params(manifest)
    core.cache_params = read_cache_params(manifest)

    return manifest
