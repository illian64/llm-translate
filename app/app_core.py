import logging
import os
import time
import traceback
from os import walk

from app import text_splitter, file_processor
from app.cache import Cache
from app.dto import TranslateResp, ProcessingFileDirReq, \
    ProcessingFileDirResp, TranslatePluginInitInfo, Part, TranslateStruct, FileProcessingPluginInitInfo, \
    TranslateCommonRequest, ProcessingFileResp, ProcessingFileStruct, ProcessingFileStatus, ProcessingFileDirListResp, \
    ProcessingFileDirListItemIn, ProcessingFileDirListItemOut
from app.params import TranslationParams, TextSplitParams, TextProcessParams, CacheParams, FileProcessingParams
from app.text_processor import pre_process
from jaa import JaaCore

logger = logging.getLogger('uvicorn')
version = "0.1.0"


class AppCore(JaaCore):
    def __init__(self):
        JaaCore.__init__(self)

        self.default_translate_plugin = ""
        self.init_on_start_plugins: list[str] = []

        self.translation_params = TranslationParams("", "")
        self.text_split_params: TextSplitParams | None = None
        self.text_process_params: TextProcessParams | None = None
        self.cache_params: CacheParams | None = None
        self.file_processing_params: FileProcessingParams | None = None

        self.translators: dict = {}
        self.initialized_translator_engines: dict[str, TranslatePluginInitInfo] = dict()
        self.cache: Cache | None = None

        self.files_ext_to_processors: dict[str, list[FileProcessingPluginInitInfo]] = dict()
        self.sleep_after_translate: float = 0.0

    def process_plugin_manifest(self, modname, manifest):
        if "translate" in manifest:  # collect translate plugins
            for cmd in manifest["translate"].keys():
                self.translators[cmd] = manifest["translate"][cmd]

        if "file_processing" in manifest and manifest["options"]["enabled"]:  # collect file processing plugins
            for cmd in manifest["file_processing"].keys():
                init_info: FileProcessingPluginInitInfo = manifest["file_processing"][cmd][0](self)  # init call
                init_info.name = cmd
                init_info.processing_function = manifest["file_processing"][cmd][1]
                init_info.processed_file_name_function = manifest["file_processing"][cmd][2]
                logger.info("Init file processing plugin '%s' for next file extensions: %s",
                            init_info.name, init_info.supported_extensions)
                for ext in init_info.supported_extensions:
                    ext_list = self.files_ext_to_processors.get(ext, list())
                    ext_list.append(init_info)
                    self.files_ext_to_processors[ext] = ext_list

        return manifest

    def init_with_translate_plugins(self) -> None:
        self.init_plugins(["core"])
        self.cache = Cache(self.cache_params)

        logger.info("Default translator: %s", self.default_translate_plugin)

        self.init_translator_engine(self.default_translate_plugin)

        for translator in self.init_on_start_plugins:
            if translator != "":
                self.init_translator_engine(translator)

        logger.info("Found translation engines: %s", ", ".join(str(key) for key in self.translators.keys()))

    def init_translator_engine(self, translator_engine: str) -> None:
        if translator_engine in self.initialized_translator_engines:
            # already inited
            return

        try:
            logger.info("Try to init translation plugin '%s'...", translator_engine)
            model_init_info: TranslatePluginInitInfo = self.translators[translator_engine][0](self)
            self.initialized_translator_engines[translator_engine] = model_init_info
            logger.info("Success init translation plugin: '%s'.", translator_engine)

        except Exception as e:
            logger.error("Error init translation plugin '%s'...", translator_engine, e)

    def get_translation_params(self, plugin_name: str) -> TranslationParams:
        options = self.plugin_options(plugin_name)
        if options and options.get('translation_params_struct'):
            return options.get('translation_params_struct')
        else:
            return self.translation_params

    def get_text_split_params(self, plugin_name: str) -> TextSplitParams:
        options = self.plugin_options(plugin_name)
        if options and options.get('text_split_params_struct'):
            return options.get('text_split_params_struct')
        else:
            return self.text_split_params

    def get_text_process_params(self, plugin_name: str) -> TextProcessParams:
        options = self.plugin_options(plugin_name)
        if options and options.get('text_process_params_struct'):
            return options.get('text_process_params_struct')
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

    def get_from_language(self, req_lang: str, plugin_name: str) -> str:
        if req_lang == "" or req_lang == "--":
            return self.get_translation_params(plugin_name).default_from_lang
        else:
            return req_lang

    def get_to_language(self, req_lang: str, plugin_name: str) -> str:
        if req_lang == "" or req_lang == "--":
            return self.get_translation_params(plugin_name).default_to_lang
        else:
            return req_lang

    def translate(self, req: TranslateCommonRequest) -> TranslateResp:
        if req.text == '':
            return TranslateResp(result='', parts=[], error=None)

        try:
            req.translator_plugin = self.get_translator_plugin(req.translator_plugin)
            plugin_info = self.initialized_translator_engines[req.translator_plugin]
            req.from_lang = self.get_from_language(req.from_lang, plugin_info.plugin_name)
            req.to_lang = self.get_to_language(req.to_lang, plugin_info.plugin_name)

            processed_text: str
            if self.get_text_process_params(req.translator_plugin).apply_for_request:
                processed_text: str = pre_process(self.get_text_process_params(plugin_info.plugin_name), req.text)
            else:
                processed_text = req.text

            text_parts: list[Part] = text_splitter.split_text(processed_text,
                                                              self.get_text_split_params(plugin_info.plugin_name),
                                                              req.from_lang)
            for text_part in text_parts:
                if not text_part.need_to_translate():
                    text_part.translate = text_part.text

            self.cache.cache_read(req, text_parts, self.cache_params, plugin_info.model_name)

            translate_struct = TranslateStruct(req=req, processed_text=processed_text, parts=text_parts)
            if translate_struct.need_to_translate():
                translate_struct: TranslateStruct = self.translators[req.translator_plugin][1](self, translate_struct)
                self.cache.cache_write(req, translate_struct.parts, self.cache_params, plugin_info.model_name)
                if self.sleep_after_translate > 0:
                    time.sleep(self.sleep_after_translate)

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

    def process_files_list(self, recursive_sub_dirs: bool) -> ProcessingFileDirListResp:
        files_in: list[ProcessingFileDirListItemIn] = []
        for root, dirs, file_names in os.walk(self.file_processing_params.directory_in):
            for file_name in file_names:
                name, extension = os.path.splitext(file_name)
                extension = extension.lower().replace(".", "")
                processor_name = None
                file_processor_error = None
                try:
                    processor = self.get_file_processor(extension, None)
                    if processor:
                        processor_name = processor.name
                except ValueError as ve:
                    file_processor_error = "error: " + ve.args[0]

                files_in.append(ProcessingFileDirListItemIn(
                    file_with_path=file_processor.get_file_with_path_for_list(
                        self.file_processing_params.directory_in, root.replace(os.sep, "/"), file_name),
                    file_processor=processor_name, file_processor_error=file_processor_error))

            if not recursive_sub_dirs:
                break

        # output directory files list
        files_out: list[ProcessingFileDirListItemOut] = []
        for root, dirs, file_names in walk(self.file_processing_params.directory_out):
            for file_name in file_names:
                files_out.append(ProcessingFileDirListItemOut(
                    file_with_path=file_processor.get_file_with_path_for_list(self.file_processing_params.directory_out,
                                                                              root.replace(os.sep, "/"), file_name)))
            if not recursive_sub_dirs:
                break

        return ProcessingFileDirListResp(files_in=files_in, files_out=files_out,
                                         directory_in=self.file_processing_params.directory_in,
                                         directory_out=self.file_processing_params.directory_out,
                                         error=None)

    def process_files(self, req: ProcessingFileDirReq) -> ProcessingFileDirResp:
        try:
            req.translator_plugin = self.get_translator_plugin(req.translator_plugin)
            plugin_name = self.initialized_translator_engines[req.translator_plugin].plugin_name
            req.from_lang = self.get_from_language(req.from_lang, plugin_name)
            req.to_lang = self.get_to_language(req.to_lang, plugin_name)

            if not req.directory_in or req.directory_in == "":
                req.directory_in = self.file_processing_params.directory_in
            if not req.directory_out or req.directory_out == "":
                req.directory_out = self.file_processing_params.directory_out
            if req.preserve_original_text is None:
                req.preserve_original_text = self.file_processing_params.preserve_original_text
            if req.overwrite_processed_files is None:
                req.overwrite_processed_files = self.file_processing_params.overwrite_processed_files

            files: list[ProcessingFileResp] = []
            for root, dirs, file_names in walk(req.directory_in):
                for file_name in file_names:
                    files.append(self.process_file(req, root, file_name))
                if not req.recursive_sub_dirs:
                    break

            return ProcessingFileDirResp(files, "")
        except ValueError as ve:
            return ProcessingFileDirResp(files=list(), error=ve.args[0])
        except Exception as e:
            traceback.print_tb(e.__traceback__, limit=10)
            return ProcessingFileDirResp(files=list(), error=getattr(e, 'message', repr(e)))

    def process_file(self, req: ProcessingFileDirReq, root: str, file_name: str) -> ProcessingFileResp:
        try:
            name, extension = os.path.splitext(file_name)

            # try to find processor
            extension = extension.lower().replace(".", "")
            req_processor = req.file_processors.get(extension) if req.file_processors else None
            processor = self.get_file_processor(extension, req_processor)
            if processor is None:
                return ProcessingFileResp(file_in=file_name, file_out="",
                                          path_file_in=f'{root}/{file_name}'.replace(os.sep, "/"),
                                          path_file_out=None, status=ProcessingFileStatus.TYPE_NOT_SUPPORT,
                                          file_processor="", message=None)

            # calculate output path and validate file exists (depend on request)
            path_out = root.replace(req.directory_in, req.directory_out)
            file_struct = ProcessingFileStruct(
                path_in=root, path_out=path_out, file_name=name,
                file_ext=extension, file_name_ext=file_name, file_processor=processor.name)

            processed_file_name = processor.processed_file_name_function(self, file_struct, req)

            if (not req.overwrite_processed_files
                    and os.path.isfile(f'{path_out}/{processed_file_name}')):
                return file_processor.get_processing_file_resp(file_struct=file_struct, file_out=processed_file_name,
                                                               file_processor=processor.name,
                                                               status=ProcessingFileStatus.TRANSLATE_ALREADY_EXISTS)
            else:
                logger.info("Start processing file %s/%s", root.replace(os.sep, "/"), file_name)
                os.makedirs(file_struct.path_out, exist_ok=True)  # make output directory structure

                return processor.processing_function(self, file_struct, req)

        except ValueError as ve:
            return file_processor.get_processing_file_resp_error(file_in=file_name, path_in=root, error_msg=ve.args[0])
        except Exception as e:
            traceback.print_tb(e.__traceback__, limit=10)
            return file_processor.get_processing_file_resp_error(file_in=file_name, path_in=root, error_msg=repr(e))

    def get_file_processor(self, extension: str, req_processor: str | None) -> FileProcessingPluginInitInfo | None:
        if not extension or extension == "":  # skip files without extension
            return None

        processors: list[FileProcessingPluginInitInfo] = self.files_ext_to_processors.get(extension, None)
        if not processors:
            return None

        if req_processor:  # try to find processor by name from request (if set)
            for processor in processors:
                if processor.name == req_processor:
                    return processor
        if req_processor:
            raise ValueError(f'Not found processor with name from request: {req_processor} for extension {extension}')

        if len(processors) == 1:  # only one processor found - ok, return it
            return processors[0]

        # try to find default processor
        default_processors_list: list[FileProcessingPluginInitInfo] = []
        for processor in processors:
            options = self.plugin_options(processor.plugin_name)
            if options and options.get('default_extension_processor'):
                default_processors_list.append(processor)

        if len(default_processors_list) == 1: # only one default processor found - return it
            return default_processors_list[0]
        elif len(default_processors_list) > 1: # find more than one default processors - error
            processor_names = map(lambda p: p.name, default_processors_list)
            raise ValueError(f'Found more than one default processor {processor_names} for extension: {extension}')

        processor_names = map(lambda p: p.name, processors) # find more than one processor, without default - error
        raise ValueError(f'Found more than one not default processors {processor_names} for extension: {extension}')
