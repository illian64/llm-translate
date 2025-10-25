import os

from app import file_processor, params, parallel_process, dto
from app.app_core import AppCore

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Translator for txt files",  # name
        "version": "1.0",  # version

        "default_options": {
            "enabled": True,
            "markdown_output": False,
            "text_format": {
                "original_prefix": "",
                "original_postfix": "",
                "translate_prefix": "*",
                "translate_postfix": "*",
            },
            "new_line_delimiter": "\n",
            "output_file_name_template": {
                "preserve_original": "%%source%%__%%from_lang%%_%%to_lang%%",
                "without_original": "%%source%%__%%to_lang%%",
            },
            "default_extension_processor": {
                "txt": True
            },
        },

        "file_processing": {
            "file_txt_translate": (init, file_processing, processed_file_name, after_processing)
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    pass


def init(core: AppCore) -> dto.FileProcessingPluginInitInfo:
    return dto.FileProcessingPluginInitInfo(plugin_name=plugin_name, supported_extensions={"txt"})


def parallel_preprocessing(lines: list[str], core: AppCore, req: dto.ProcessingFileDirReq) -> None:
    gpu_count_for_parallel = parallel_process.translate_plugin_support_parallel_gpu_count(core, req.translator_plugin)
    if gpu_count_for_parallel is None:
        return None

    # First pre-pass - translate without any actions, for fill cache. Next pass get translated text from cache.
    translate_params: list[dto.TranslateCommonRequest] = list()
    all_original_text_items: list[str] = []
    for line in lines:
        if line != '':
            context = file_processor.get_context(items_to_context=all_original_text_items,
                                                 params=core.file_processing_params.context_params, translate_text=line)
            translate_req = req.translate_req(line, context)
            all_original_text_items.append(line)
            translate_params.append(translate_req)

    parallel_process.start_parallel_processing(gpu_count_for_parallel, core, translate_params)


def file_processing(core: AppCore, file_struct: dto.ProcessingFileStruct, req: dto.ProcessingFileDirReq) -> dto.ProcessingFileResp:
    options = core.plugin_options(plugin_name)
    markdown_output: bool = options["markdown_output"]
    new_line_delimiter: str = options["new_line_delimiter"]
    text_format = params.read_plugin_file_processing_text_format(options)
    new_line_delimiter_count = 2 if markdown_output else 1

    result_lines: list[str] = []
    all_original_text_items: list[str] = []
    file_content = file_processor.read_file_with_fix_encoding(file_struct.path_file_in())
    lines: list[str] = file_content.splitlines()

    parallel_preprocessing(lines, core, req)

    for line in lines:
        if line == '':
            result_lines.append(new_line_delimiter)
            continue

        if req.preserve_original_text:
            result_lines.append(text_format.original_text(line) +
                                new_line_delimiter * new_line_delimiter_count)

        context = file_processor.get_context(items_to_context=all_original_text_items,
                                             params=core.file_processing_params.context_params, translate_text=line)
        translate_req = req.translate_req(line, context)
        all_original_text_items.append(line)
        translate_txt = core.translate(translate_req).result
        translate_txt_format = text_format.translate_text(translate_txt)
        result_lines.append(translate_txt_format + new_line_delimiter * new_line_delimiter_count)

    out_file_name = processed_file_name(core=core, file_struct=file_struct, req=req)
    with open(file_struct.path_file_out(out_file_name), "w", encoding=options["encoding_output"]) as f:
        f.write((''.join(result_lines)))

    return file_processor.get_processing_file_resp_ok(file_struct=file_struct, file_out=out_file_name)


def processed_file_name(core: AppCore, file_struct: dto.ProcessingFileStruct, req: dto.ProcessingFileDirReq) -> str:
    options = core.plugin_options(plugin_name)
    ext = "md" if options["markdown_output"] else None

    return file_processor.file_name_from_template(file_struct=file_struct, req=req, options=options, replace_ext=ext)


def after_processing(core: AppCore) -> None:
    pass
