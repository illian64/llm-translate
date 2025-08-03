import logging
import os
from os import walk

from app.dto import TranslateBookDirReq, TranslateBookDirResp, TranslateBookItem, TranslateBookItemStatus

logger = logging.getLogger('uvicorn')


class BookDirectoryTranslate:
    supported_extensions = ['epub']
    overwrite_exists_translated_books = True

    def __init__(self, translate_func):
        self.translate_func = translate_func

    def translate(self, req: TranslateBookDirReq) -> TranslateBookDirResp:
        filenames = list[str]
        for dir_path, dir_names, filenames in walk(req.directory_in):
            break

        if not filenames:
            return TranslateBookDirResp([], "")

        books: list[TranslateBookItem] = []
        for filename in filenames:
            books.append(self.process_file(req, filename))


    def process_file(self, req: TranslateBookDirReq, filename: str) -> TranslateBookItem:
        name, extension = os.path.splitext(filename)
        if extension in self.supported_extensions:
            translate_book_file_name = self.get_translate_book_file_name(req, name, extension)
            if not self.overwrite_exists_translated_books and os.path.isfile(f'{req.directory_out}/{translate_book_file_name}'):
                return TranslateBookItem(f'{req.directory_in}/{filename}', "", TranslateBookItemStatus.translate_already_exists)
            else:
                if extension == 'epub':
                    pass #TODO fix

        else:
            return TranslateBookItem(f'{req.directory_in}/{name}.{extension}', "", TranslateBookItemStatus.type_not_support)


    def get_translate_book_file_name(self, req: TranslateBookDirReq, name: str, extension: str) -> str:
        from_lang_part = "_" + req.from_lang if req.preserve_original_text else ""

        return f'{name}__{from_lang_part}_{req.to_lang}.{extension}'



