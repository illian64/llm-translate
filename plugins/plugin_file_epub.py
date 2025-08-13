import logging
import os
import traceback

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from app import file_processor
from app.app_core import AppCore
from app.dto import ProcessingFileDirReq, ProcessingFileResp, FileProcessingPluginInitInfo, ProcessingFileStruct
from app.file_processor_html import FileProcessorHtml

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname
logger = logging.getLogger('uvicorn')


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Translator for epub books",  # name
        "version": "1.0",  # version

        "default_options": {
            "enabled": True,
            "text_format": {
                "original_tag": "",
                "translate_tag": "i",
                "header_delimiter": " / "
            },
            "header_tags": ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
            "text_tags": ['p'],
            "output_file_name_template": {
                "preserve_original": "%source%__%from_lang%_%to_lang%",
                "without_original": "%source%__%to_lang%",
            },
            "default_extension_processor": {
                "epub": True
            },
        },

        "file_processing": {
            "file_epub_translate": (init, file_processing, processed_file_name)
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    pass


def init(core: AppCore) -> FileProcessingPluginInitInfo:
    return FileProcessingPluginInitInfo(plugin_name=plugin_name, supported_extensions={"epub"})


def file_processing(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> ProcessingFileResp:
    options = core.plugin_options(plugin_name)
    html_processor = FileProcessorHtml(core=core, options=options)

    try:
        book = epub.read_epub(file_struct.path_file_in())

        docs_count = 0
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                docs_count = docs_count + 1

        processed_count = 0
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                processed_count = processed_count + 1
                logger.info("Translate file %s, item with id %s, item %s / %s",
                            file_struct.file_name_ext, item.get_id(), processed_count, docs_count)
                soup = BeautifulSoup(item.get_content(), features="xml")
                html_processor.process(req=req, soup=soup)
                item.set_content(soup.encode())

        out_file_name = processed_file_name(core=core, file_struct=file_struct, req=req)
        epub.write_epub(file_struct.path_file_out(out_file_name), book, {})

        return file_processor.get_processing_file_resp_ok(file_struct=file_struct, file_out=out_file_name)
    except Exception as e:
        traceback.print_tb(e.__traceback__, limit=10)
        logging.error("Error with processing file %s: %s", file_struct.file_name_ext, str(e))
        return file_processor.get_processing_file_resp_error(
            file_in=file_struct.file_name_ext, path_in=file_struct.path_in, error_msg=str(e))


def processed_file_name(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> str:
    options = core.plugin_options(plugin_name)

    return file_processor.file_name_from_template(file_struct=file_struct, req=req, options=options)
