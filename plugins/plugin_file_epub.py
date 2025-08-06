import os

from app.app_core import AppCore
from app.dto import ProcessingFileDirReq, ProcessingFileResp, FileProcessingPluginInitInfo, ProcessingFileStruct

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


# start function
def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Translator for epub books",  # name
        "version": "1.0",  # version

        "default_options": {
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


def file_processing(core: AppCore, file: ProcessingFileStruct, req: ProcessingFileDirReq) -> ProcessingFileResp:
    # core.translate()
    pass


def processed_file_name(core: AppCore, file: ProcessingFileStruct, req: ProcessingFileDirReq) -> str:
    from_lang_part = "_" + req.from_lang if req.preserve_original_text else ""

    return f'{file.file_name}__{from_lang_part}_{req.to_lang}.{file.file_ext}'
