import os

import pysrt

from app import file_processor, params
from app.app_core import AppCore
from app.dto import ProcessingFileDirReq, ProcessingFileResp, FileProcessingPluginInitInfo, ProcessingFileStruct

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Translator for srt files",  # name
        "version": "1.0",  # version

        "default_options": {
            "enabled": True,
            "text_format": {
                "original_prefix": "",
                "original_postfix": "",
                "translate_prefix": "<i>",
                "translate_postfix": "</i>",
            },
            "remove_src_filename_postfix": ".src_sub",
            "translate_delimiter": "\n",
            "output_file_name_template": {
                "preserve_original": "%%source%%.%%from_lang%%_%%to_lang%%",
                "without_original": "%%source%%.%%to_lang%%",
            },
            "default_extension_processor": {
                "srt": True
            },
        },

        "file_processing": {
            "file_srt_translate": (init, file_processing, processed_file_name, after_processing)
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    pass


def init(core: AppCore) -> FileProcessingPluginInitInfo:
    return FileProcessingPluginInitInfo(plugin_name=plugin_name, supported_extensions={"srt"})


def file_processing(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> ProcessingFileResp:
    options = core.plugin_options(plugin_name)
    text_format = params.read_plugin_file_processing_text_format(options)

    subs = pysrt.open(file_struct.path_file_in())
    for sub in subs:
        text = sub.text
        translate_req = req.translate_req(text, "")
        translate_text = core.translate(translate_req).result
        translate_text_format = text_format.translate_text(translate_text)

        if req.preserve_original_text:
            original_text_format = text_format.original_text(text)
            sub.text = f'{original_text_format}{options["translate_delimiter"]}{translate_text_format}'

    out_file_name = processed_file_name(core=core, file_struct=file_struct, req=req)

    subs.save(file_struct.path_file_out(out_file_name))

    return file_processor.get_processing_file_resp_ok(file_struct=file_struct, file_out=out_file_name)


def processed_file_name(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> str:
    options = core.plugin_options(plugin_name)
    src_postfix = options["remove_src_filename_postfix"]

    return file_processor.file_name_from_template(file_struct=file_struct, req=req, options=options).replace(src_postfix + ".", ".")


def after_processing(core: AppCore) -> None:
    pass
