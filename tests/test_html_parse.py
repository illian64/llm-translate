from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from app import dto, params
from app.app_core import AppCore
from app.file_html_processor import FileHtmlProcessor


class HtmlParseTest(TestCase):
    test_dir = Path(__file__).parent.absolute()

    @staticmethod
    def translate_func(req: dto.TranslateCommonRequest) -> dto.TranslateResp:
        text = 'TR ' + req.text + ' TR' if any(letter.isalpha() for letter in req.text) else req.text
        return dto.TranslateResp(text, None, None)

    @staticmethod
    def def_instance() -> FileHtmlProcessor:
        options = dict()
        options["header_tags"] = ["h1", "h2", "h3", "h4", "h5", "h6"]
        options["text_tags"] = ["p"]
        options["text_format"] = dict()
        options["text_format"]["original_tag"] = ""
        options["text_format"]["translate_tag"] = "i"
        options["text_format"]["header_delimiter"] = "/"
        options["translate_only_first_paragraphs"] = 10

        core = AppCore()
        core.default_translate_plugin = "default_translate_plugin"
        core.initialized_translator_engines = {"default_translate_plugin": None}
        context_params = params.FileProcessingContextParams(
            enabled=True, prompt="", expected_length=500, include_at_least_one_paragraph=False, paragraph_join_str="/")
        core.file_processing_params = params.FileProcessingParams(
            directory_in="", directory_out="", preserve_original_text=True,
            overwrite_processed_files=True, context_params=context_params)
        processor = FileHtmlProcessor(core, options)
        processor.translate_func = HtmlParseTest.translate_func

        return processor

    @staticmethod
    def def_file_dir_req() -> dto.ProcessingFileDirReq:
        data = {
            "preserve_original_text": True, "recursive_sub_dirs": True
        }
        req = dto.ProcessingFileDirReq.model_construct(**data)

        return req

    def test_html_file_01(self):
        with open(str(self.test_dir / "files/html_file_01.xhtml"), "r", encoding="utf-8") as file:
            file_content = file.read()
        soup = BeautifulSoup(file_content, features='html.parser')
        html_processor = HtmlParseTest.def_instance()

        parse_html = html_processor.process(soup=soup, req=HtmlParseTest.def_file_dir_req(), body_tag=None)
        self.assertEqual(1, len(parse_html.header_tags))

        with open(str(self.test_dir / "files/html_file_01_tr.html"), "w", encoding="utf-8") as file:
            file.write(soup.prettify())
