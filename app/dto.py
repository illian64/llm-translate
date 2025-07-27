from dataclasses import dataclass

from pydantic import BaseModel


class TranslateReq(BaseModel):
    text: str
    from_lang: str | None = ""
    to_lang: str | None = ""
    translator_plugin: str | None = ""


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

