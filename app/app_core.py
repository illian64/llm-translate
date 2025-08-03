import logging
import traceback

from app import text_splitter
from app.books_translate import BookDirectoryTranslate
from app.cache import Cache
from app.dto import TranslateResp, TranslateBookDirReq, TranslateBookDirResp
from app.struct import TranslateStruct, TranslationParams, TextSplitParams, TextProcessParams, Request, Part, \
    CacheParams, ModelInitInfo
from app.text_processor import pre_process
from jaa import JaaCore

logger = logging.getLogger('uvicorn')
version = "0.1.0"


class AppCore(JaaCore):
    def __init__(self):
        JaaCore.__init__(self)

        self.default_translate_plugin = ""
        self.init_on_start = ""

        self.translation_params = TranslationParams("", "")
        self.text_split_params: TextSplitParams = None
        self.text_process_params: TextProcessParams = None
        self.cache_params: CacheParams = None

        self.translators: dict = {}
        self.initialized_translator_engines: dict[str, ModelInitInfo] = dict()
        self.cache: Cache = None

    def process_plugin_manifest(self, modname, manifest):
        if "translate" in manifest:  # process commands
            for cmd in manifest["translate"].keys():
                self.translators[cmd] = manifest["translate"][cmd]

        return manifest

    def init_with_plugins(self) -> None:
        self.init_plugins(["core"])
        self.cache = Cache(self.cache_params)

        logger.info("Default translator: %s", self.default_translate_plugin)

        self.init_translator_engine(self.default_translate_plugin)

        init_on_start_list = self.init_on_start.replace(" ", "").split(",") #TODO to array
        for translator in init_on_start_list:
            if translator != "":
                self.init_translator_engine(translator)

        logger.info("Found translation engines: %s", ", ".join(str(key) for key in self.translators.keys()))

    def init_translator_engine(self, translator_engine: str) -> None:
        if translator_engine in self.initialized_translator_engines:
            # already inited
            return

        try:
            logger.info("Try to init translation plugin '%s'...", translator_engine)
            model_init_info: ModelInitInfo = self.translators[translator_engine][0](self)
            self.initialized_translator_engines[translator_engine] = model_init_info
            logger.info("Success init translation plugin: '%s'.", translator_engine)

        except Exception as e:
            logger.error("Error init translation plugin '%s'...", translator_engine, e)

    def get_plugin_options(self, translator_engine: str):
        translator_engine = self.initialized_translator_engines[translator_engine].plugin_name
        return self.plugin_options(translator_engine)

    def get_translation_params(self, translator_engine: str) -> TranslationParams:
        options = self.get_plugin_options(translator_engine)
        if options and options['translation_params_struct']:
            return options['translation_params_struct']
        else:
            return self.translation_params

    def get_text_split_params(self, translator_engine: str) -> TextSplitParams:
        options = self.get_plugin_options(translator_engine)
        if options and options['text_split_params_struct']:
            return options['text_split_params_struct']
        else:
            return self.text_split_params

    def get_text_process_params(self, translator_engine: str) -> TextProcessParams:
        options = self.get_plugin_options(translator_engine)
        if options and options['text_process_params_struct']:
            return options['text_process_params_struct']
        else:
            return self.text_process_params

    def get_translator_plugin(self, req_plugin: str) -> str:
        translator_plugin: str
        if not req_plugin or req_plugin == "":
            translator_plugin = self.default_translate_plugin
        else:
            translator_plugin = req_plugin

        if translator_plugin not in self.initialized_translator_engines:
            raise ValueError("This translate_plugin not in initialized: " + translator_plugin)

        return translator_plugin

    def get_from_language(self, req_lang: str, translator_plugin: str) -> str:
        if req_lang == "" or req_lang == "--":
            return self.get_translation_params(translator_plugin).default_from_lang
        else:
            return req_lang

    def get_to_language(self, req_lang: str, translator_plugin: str) -> str:
        if req_lang == "" or req_lang == "--":
            return self.get_translation_params(translator_plugin).default_to_lang
        else:
            return req_lang

    def translate(self, req: Request) -> TranslateResp:
        if req.text == '':
            return TranslateResp(result='', parts=[], error=None)

        try:
            req.translator_plugin = self.get_translator_plugin(req.translator_plugin)
            req.from_lang = self.get_from_language(req.from_lang, req.translator_plugin)
            req.to_lang = self.get_to_language(req.to_lang, req.translator_plugin)

            processed_text: str
            if self.get_text_process_params(req.translator_plugin).apply_for_request:
                processed_text: str = pre_process(self.get_text_process_params(req.translator_plugin), req.text)
            else:
                processed_text = req.text

            text_parts: list[Part] = text_splitter.split_text(processed_text,
                                                              self.get_text_split_params(req.translator_plugin),
                                                              req.from_lang)
            self.cache_read(req, text_parts)

            translate_struct = TranslateStruct(req=req, processed_text=processed_text, parts=text_parts)

            translate_struct: TranslateStruct = self.translators[req.translator_plugin][1](self, translate_struct)
            self.cache_write(req, translate_struct.parts)

            (translate_text, translate_parts) = text_splitter.join_text(translate_struct.parts)

            if self.text_process_params.apply_for_response:
                translate_text: str = pre_process(self.text_process_params, translate_text)
            else:
                translate_text = req.text

            return TranslateResp(result=translate_text, parts=translate_parts, error=None)
        except ValueError as ve:
            return TranslateResp(result=None, parts=None, error=ve.args[0])
        except Exception as e:
            traceback.print_tb(e.__traceback__, limit=10)
            return TranslateResp(result=None, parts=None, error=getattr(e, 'message', repr(e)))

    def translate_books_dir(self, req: TranslateBookDirReq) -> TranslateBookDirResp:
        try:
            req.translator_plugin = self.get_translator_plugin(req.translator_plugin)
            req.from_lang = self.get_from_language(req.from_lang, req.translator_plugin)
            req.to_lang = self.get_to_language(req.to_lang, req.translator_plugin)

            if not req.directory_in or req.directory_in == "":
                req.directory_in = 'books/in'
            if not req.directory_out or req.directory_out == "":
                req.directory_in = 'books/out'

            return BookDirectoryTranslate(self).translate(req)
        except ValueError as ve:
            return TranslateBookDirResp(books=None, error=ve.args[0])
        except Exception as e:
            traceback.print_tb(e.__traceback__, limit=10)
            return TranslateBookDirResp(books=None, error=getattr(e, 'message', repr(e)))

    def cache_read(self, req: Request, parts: list[Part]):
        if self.cache_params.enabled and req.translator_plugin not in self.cache_params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate():
                    cached_translate = self.cache.get(req, part.text)
                    if cached_translate:
                        part.cache_found = True
                        part.translate = cached_translate
                    else:
                        part.cache_found = False

    def cache_write(self, req: Request, parts: list[Part]):
        if self.cache_params.enabled and req.translator_plugin not in self.cache_params.disable_for_plugins:
            for part in parts:
                if part.need_to_translate() and not part.cache_found:
                    self.cache.put(req, part.text, part.translate)
