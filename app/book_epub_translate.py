import logging

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from tqdm import tqdm

from app.app_core import AppCore
from app.dto import TranslateBookItemStatus
from app.struct import TranslateBook, Request, tp

logger = logging.getLogger('uvicorn')
tag_headers = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
tag_text = ['p']


class BookEpubTranslate:
    def translate_book(self, translate_func, req: TranslateBook, output_file_name: str) -> TranslateBookItemStatus:
        book = epub.read_epub(req.file)
        for item in book.get_items():
            logger.info("Translate item with id %s", item.get_id())
            if item.get_type() == ebooklib.ITEM_DOCUMENT and item.get_id() == "item_1":
                content = BeautifulSoup(item.get_content(), features="xml")

                for child in tqdm(content.descendants, unit=tp.unit, ascii=tp.ascii, desc=tp.desc):
                    if child and child.text and child.parent:
                        if child.parent.name and child.parent.string and (child.parent.name in tag_text or child.parent.name in tag_headers):
                            text = child.parent.string
                            translated_text = self.translate_text(core, req, text)

                            if child.parent.name in tag_text:
                                if req.preserve_original_text:
                                    translate_tag = content.new_tag(child.parent.name)
                                    translate_tag.string = translated_text
                                    child.insert_after(translate_tag)
                                else:
                                    child.parent.string = translated_text

                            if child.parent.name in tag_headers:
                                if req.preserve_original_text:
                                    child.parent.string = f'{child.parent.string} / {translated_text}'
                                else:
                                    child.parent.string = translated_text

                item.set_content(content.encode())

        epub.write_epub(file[:len(file) - 4] + "__translate.epub", book, {})

    def translate_text(self, core: AppCore, req: TranslateBook, text: str) -> str:
        translate_result = core.translate(Request(text=text, from_lang=req.from_lang, to_lang=req.to_lang,
                                                  translator_plugin=req.translator_plugin))

        return translate_result.result
