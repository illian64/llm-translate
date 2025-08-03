import enum
from dataclasses import dataclass

from pydantic import BaseModel


class TranslateReq(BaseModel):
    text: str
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""


class TranslateBookDirReq(BaseModel):
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""
    preserve_original_text: bool
    directory_in: str | None = None
    directory_out: str | None = None


@dataclass
class TranslateBook:
    book_dir_req: TranslateBookDirReq
    file: str
    preserve_original_text: bool
    from_lang: str | None
    to_lang: str | None
    translator_plugin: str | None

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


class TranslateBookItemStatus(enum.Enum):
    ok = 1
    error = 2
    translate_already_exists = 3
    type_not_support = 4


@dataclass
class TranslateBookItem:
    file_in: str
    file_out: str
    state: TranslateBookItemStatus


@dataclass
class TranslateBookDirResp:
    books: list[TranslateBookItem] | None
    error: str | None

