import logging
import traceback

from app import text_splitter
from app.cache import Cache
from app.dto import TranslateResp
from app.struct import TranslateStruct, TranslationParams, TextSplitParams, TextProcessParams, Request, Part, \
    CacheParams
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
        self.initialized_translator_engines = dict()
        self.cache: Cache = None

    def process_plugin_manifest(self, modname, manifest):
        if "translate" in manifest:  # process commands
            for cmd in manifest["translate"].keys():
                self.translators[cmd] = manifest["translate"][cmd]

        return manifest

    def init_with_plugins(self):
        self.init_plugins(["core"])
        self.cache = Cache(self.cache_params)

        logger.info("Default translator: %s", self.default_translate_plugin)

        self.init_translator_engine(self.default_translate_plugin)

        init_on_start_list = self.init_on_start.replace(" ", "").split(",")
        for translator in init_on_start_list:
            if translator != "":
                self.init_translator_engine(translator)

        logger.info("Found translation engines: %s", ", ".join(str(key) for key in self.translators.keys()))

    def init_translator_engine(self, translator_engine: str):
        if translator_engine in self.initialized_translator_engines:
            # already inited
            return

        try:
            logger.info("Try to init translation plugin '%s'...", translator_engine)
            modname = self.translators[translator_engine][0](self)
            self.initialized_translator_engines[translator_engine] = modname
            logger.info("Success init translation plugin: '%s'.", translator_engine)

        except Exception as e:
            logger.error("Error init translation plugin '%s'...", translator_engine, e)

    def get_plugin_options(self, translator_engine: str):
        modname = self.initialized_translator_engines[translator_engine]
        return self.plugin_options(modname)

    def get_translation_params(self, translator_engine: str):
        options = self.get_plugin_options(translator_engine)
        if options['translation_params_struct']:
            return options['translation_params_struct']
        else:
            return self.translation_params

    def get_text_split_params(self, translator_engine: str):
        options = self.get_plugin_options(translator_engine)
        if options['text_split_params_struct']:
            return options['text_split_params_struct']
        else:
            return self.text_split_params

    def get_text_process_params(self, translator_engine: str):
        options = self.get_plugin_options(translator_engine)
        if options['text_process_params_struct']:
            return options['text_process_params_struct']
        else:
            return self.text_process_params

    def translate(self, req: Request):
        if req.text == '':
            return TranslateResp(result='', parts=[], error=None)

        try:
            if not req.translator_plugin or req.translator_plugin == "":
                req.translator_plugin = self.default_translate_plugin

            if req.translator_plugin not in self.initialized_translator_engines:
                raise ValueError("This translate_plugin not in initialized: " + req.translator_plugin)

            if req.from_lang == "":
                req.from_lang = self.get_translation_params(req.translator_plugin).default_from_lang

            if req.to_lang == "":
                req.to_lang = self.get_translation_params(req.translator_plugin).default_to_lang

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
