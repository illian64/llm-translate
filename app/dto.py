import enum
from dataclasses import dataclass
from typing import Callable, Any

from pydantic import BaseModel


class TranslateReq(BaseModel):
    text: str
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""


class ProcessingFileDirReq(BaseModel):
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""
    preserve_original_text: bool
    directory_in: str | None = None
    directory_out: str | None = None
    file_processor: dict[str, str] | None
    overwrite_processed_files: bool | None


@dataclass
class ProcessingFileStruct:
    path: str
    file_name: str
    file_ext: str
    file_name_ext: str


@dataclass
class TranslatePart:
    text: str
    translate: str
    paragraph_end: bool


@dataclass
class TranslateResp:
    result: str | None
    parts: list[TranslatePart] | None
    error: str | None


class ProcessingFileStatus(enum.Enum):
    ok = 1
    error = 2
    translate_already_exists = 3
    type_not_support = 4


@dataclass
class ProcessingFileResp:
    file_in: str
    file_out: str
    state: ProcessingFileStatus
    file_processor: str
    message: str | None


@dataclass
class ProcessingFileDirResp:
    files: list[ProcessingFileResp] | None
    error: str | None


@dataclass
class ProcessingFileDirListItemIn:
    file: str
    file_processor: str | None
    file_processor_error: str | None


@dataclass
class ProcessingFileDirListItemOut:
    file: str


@dataclass
class ProcessingFileDirListResp:
    files_in: list[ProcessingFileDirListItemIn]
    files_out: list[ProcessingFileDirListItemOut]
    error: str | None


@dataclass
class TranslateCommonRequest:
    text: str
    from_lang: str | None
    to_lang: str | None
    translator_plugin: str | None


@dataclass
class TranslatePluginInitInfo:
    plugin_name: str
    model_name: str
    #todo  translate_function: Callable[[...], ...]


@dataclass
class FileProcessingPluginInitInfo:
    name: str
    plugin_name: str
    processing_function: Callable[[Any, ProcessingFileStruct, ProcessingFileDirReq], ProcessingFileResp]
    processed_file_name_function: Callable[[Any, ProcessingFileStruct, ProcessingFileDirReq], ProcessingFileResp]
    supported_extensions: set[str]  # lower case

    def __init__(self, plugin_name: str, supported_extensions: set[str]):
        self.plugin_name = plugin_name
        self.supported_extensions = supported_extensions


@dataclass
class Part:
    text: str
    translate: str
    paragraph_end: bool
    cache_found: bool

    def is_numeric_or_empty(self):
        processed_text = (self.text
                          .replace(" ", "")
                          .replace(",", "")
                          .replace(".", ""))

        return processed_text.isnumeric() or len(processed_text) == 0

    def need_to_translate(self):
        return not self.cache_found and self.text and self.text != "" and not self.is_numeric_or_empty()

    def __init__(self, text: str, paragraph_end: bool):
        self.text = text
        self.translate = ""
        self.paragraph_end = paragraph_end
        self.cache_found = False


@dataclass
class TranslateStruct:
    req: TranslateCommonRequest
    processed_text: str
    parts: list[Part]
