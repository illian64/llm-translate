import os

import chardet

from app import log
from app.dto import ProcessingFileStruct, ProcessingFileDirReq, ProcessingFileResp, ProcessingFileStatus
from app.params import FileProcessingContextParams

logger = log.logger()


def processed_file_name_def(file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> str:
    from_lang_part = "_" + req.from_lang if req.preserve_original_text else ""

    return f'{file_struct.file_name}__{from_lang_part}_{req.to_lang}.{file_struct.file_ext}'


def file_name_from_template(file_struct: ProcessingFileStruct, req: ProcessingFileDirReq, options: dict) -> str:
    """
    Generate output file name from template. Template in options, for preserve original and not.
    Special parameters in template:
    %%source%% - original file name
    %%from_lang%% - source language
    %%to_lang%% - target language

    :param file_struct: struct with file info
    :param req: file process request
    :param options: template parameters source
    :return: output file name
    """
    template_dict = options["output_file_name_template"]
    template = template_dict["preserve_original"] if req.preserve_original_text else template_dict["without_original"]
    return ((template.replace("%%source%%", file_struct.file_name)
                 .replace("%%from_lang%%", req.from_lang)
                 .replace("%%to_lang%%", req.to_lang))
            + "." + file_struct.file_ext)


def get_file_with_path_for_list(init_dir: str, root: str, file_name: str) -> str:
    file_with_path = root.replace(init_dir, "") + "/" + file_name
    return file_with_path[1:]


def get_processing_file_resp(file_struct: ProcessingFileStruct, file_out: str, file_processor: str,
                             status: ProcessingFileStatus, message: str | None = None) -> ProcessingFileResp:
    return ProcessingFileResp(
        file_in=file_struct.file_name, file_out=file_out,
        path_file_in=file_struct.path_file_in().replace(os.sep, "/"),
        path_file_out=file_struct.path_file_out(file_out).replace(os.sep, "/"),
        status=status, file_processor=file_processor, message=message
    )


def get_processing_file_resp_ok(file_struct: ProcessingFileStruct, file_out: str) -> ProcessingFileResp:
    return get_processing_file_resp(
        file_struct=file_struct, file_out=file_out,
        status=ProcessingFileStatus.OK, file_processor=file_struct.file_processor
    )


def get_processing_file_resp_error(file_in: str, path_in: str, error_msg: str) -> ProcessingFileResp:
    return ProcessingFileResp(
        file_in=file_in, path_file_in=f'{path_in}{os.sep}{file_in}', file_out=None, path_file_out=None,
        file_processor=None, status=ProcessingFileStatus.ERROR, message=error_msg
    )


def read_file_with_fix_encoding(path_file: str) -> str:
    with open(path_file, "rb") as file:
        content_raw = file.read()
        encoding = chardet.detect(content_raw)['encoding']
        if encoding.lower() != "utf-8":
            logger.info("Charset encoding in file %s: %s",path_file, encoding)
            return content_raw.decode(encoding=encoding, errors='ignore')
        else:
            return content_raw.decode(encoding="utf-8")


def get_context(items_to_context: list[str], params: FileProcessingContextParams, translate_text: str) -> str | None:
    """
    Generate context message for file processing.
    If params.enabled -> None.
    If translate_text == item in items_to_context - this item will be ignored.

    :param items_to_context: all previous paragraphs in file
    :param params: cache params
    :param translate_text: current text to translate
    :return: context message or None if not text tto generate context
    """

    if params.enabled:
        result_list: list[str] = []
        result_list_context_length = 0

        for item in reversed(items_to_context):
            if translate_text == item:
                continue

            strip_item = item.strip()
            add_anyway = len(result_list) == 0 and params.include_at_least_one_paragraph
            if add_anyway or (len(strip_item) + result_list_context_length <= params.expected_length):
                result_list.insert(0, strip_item)
                result_list_context_length += len(strip_item)
            else:
                break

        if len(result_list) == 0:
            return None
        else:
            return params.prompt.replace("%%context%%", params.paragraph_join_str.join(result_list))
    else:
        return None
