import enum
import os
from dataclasses import dataclass
from typing import Callable, Any

from pydantic import BaseModel


class TranslateReq(BaseModel):
    text: str
    context: str | None = ""
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""


@dataclass
class TranslateCommonRequest:
    text: str
    context: str | None
    from_lang: str | None
    to_lang: str | None
    translator_plugin: str | None


class ProcessingFileDirReq(BaseModel):
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""
    preserve_original_text: bool
    directory_in: str | None = None
    directory_out: str | None = None
    file_processors: dict[str, str] | None
    overwrite_processed_files: bool | None
    recursive_sub_dirs: bool

    def translate_req(self, text: str, context: str) -> TranslateCommonRequest:
        return TranslateCommonRequest(text=text, context=context, from_lang=self.from_lang, to_lang=self.to_lang,
                                      translator_plugin=self.translator_plugin)


@dataclass
class ProcessingFileStruct:
    path_in: str
    path_out: str
    file_name: str
    file_ext: str
    file_name_ext: str
    file_processor: str

    def path_file_in(self) -> str:
        return f'{self.path_in}{os.sep}{self.file_name_ext}'

    def path_file_out(self, out_file_name_ext: str) -> str:
        return f'{self.path_out}{os.sep}{out_file_name_ext}'


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
    OK = "OK"
    ERROR = "ERROR"
    TRANSLATE_ALREADY_EXISTS = "TRANSLATE_ALREADY_EXISTS"
    TYPE_NOT_SUPPORT = "TYPE_NOT_SUPPORT"


@dataclass
class ProcessingFileResp:
    file_in: str
    file_out: str | None

    path_file_in: str
    path_file_out: str | None

    status: ProcessingFileStatus
    file_processor: str | None
    message: str | None


@dataclass
class ProcessingFileDirResp:
    files: list[ProcessingFileResp] | None
    error: str | None


@dataclass
class ProcessingFileDirListItemIn:
    file_with_path: str
    file_processor: str | None
    file_processor_error: str | None


@dataclass
class ProcessingFileDirListItemOut:
    file_with_path: str


@dataclass
class ProcessingFileDirListResp:
    files_in: list[ProcessingFileDirListItemIn]
    files_out: list[ProcessingFileDirListItemOut]
    directory_in: str
    directory_out: str

    error: str | None


@dataclass
class TranslatePluginInitInfo:
    plugin_name: str
    model_name: str
    # todo  translate_function: Callable[[...], ...]


@dataclass
class FileProcessingPluginInitInfo:
    name: str
    plugin_name: str
    processing_function: Callable[[Any, ProcessingFileStruct, ProcessingFileDirReq], ProcessingFileResp]
    processed_file_name_function: Callable[[Any, ProcessingFileStruct, ProcessingFileDirReq], str]
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

    def is_contains_alpha(self) -> bool:
        if any(letter.isalpha() for letter in self.text):
            return True

        return False

    def need_to_translate(self):
        return not self.cache_found and self.text and self.is_contains_alpha()

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

    def need_to_translate(self) -> bool:
        for part in self.parts:
            if part.need_to_translate():
                return True

        return False
