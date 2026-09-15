from typing import Callable

from bs4 import BeautifulSoup, Tag

from app import dto, parallel_process, file_processor
from app.app_core import AppCore
from app.file_html_parser import HtmlParser, HtmlParseResult


class FileHtmlProcessor:
    attribute_source = "llmt-src"
    attribute_translate = "llmt-tr"

    def __init__(self, core: AppCore, options: dict):
        self.core = core
        self.translate_only_first_paragraphs = options.get("translate_only_first_paragraphs", 0)
        self.html_parser = HtmlParser(options)
        self.translate_func: Callable[[dto.TranslateCommonRequest], dto.TranslateResp] = self.core.translate
        self.context_params = core.file_processing_params.context_params
        self.header_delimiter: str = options["text_format"]["header_delimiter"]

    def process(self, req: dto.ProcessingFileDirReq, soup: BeautifulSoup, body_tag: str = None) -> HtmlParseResult:
        gpu_count_for_parallel = parallel_process.translate_plugin_support_parallel_gpu_count(
            self.core, req.translator_plugin)
        parse_result: HtmlParseResult = self.html_parser.parse_html(soup, body_tag)

        # process headers
        translate_reqs_headers: list[dto.TranslateCommonRequest] = list()
        for header_tag in parse_result.header_tags:
            translate_req = self.get_translate_req(header_tag.text, [], req)
            translate_reqs_headers.append(translate_req)
        translate_responses = self.translate_requests(translate_reqs_headers, gpu_count_for_parallel)
        for i, item in enumerate(parse_result.header_tags):
            self.process_header_translate(item, translate_responses[i].result, req.preserve_original_text)

        if self.translate_only_first_paragraphs > 0:
            html_paragraphs = parse_result.paragraphs[:self.translate_only_first_paragraphs]
        else:
            html_paragraphs = parse_result.paragraphs

        translate_reqs: list[dto.TranslateCommonRequest] = list()
        translate_reqs_sub_paragraphs: list[dto.TranslateCommonRequest] = list()
        previous_text_items: list[str] = []
        html_paragraphs_iter = html_paragraphs.copy()

        # iterate paragraphs and find sub-paragraphs
        for html_paragraph in html_paragraphs_iter:
            if len(html_paragraph.sub_paragraph_items) > 0:
                # found paragraph with sub-paragraphs
                for sub_paragraph_item in html_paragraph.sub_paragraph_items:
                    translate_req = self.get_translate_req(sub_paragraph_item.text, previous_text_items, req)
                    translate_reqs_sub_paragraphs.append(translate_req)
                translate_responses = self.translate_requests(translate_reqs_sub_paragraphs, gpu_count_for_parallel)
                translate_reqs_sub_paragraphs.clear()

                sub_paragraph_items_iter = html_paragraph.sub_paragraph_items.copy()
                for i, item in enumerate(sub_paragraph_items_iter):
                    self.process_translate(item.text, translate_responses[i].result, soup,
                                           item.sub_paragraph, req.preserve_original_text)

            else:
                translate_req = self.get_translate_req(html_paragraph.paragraph.text, previous_text_items, req)
                translate_reqs.append(translate_req)

        translate_responses = self.translate_requests(translate_reqs, gpu_count_for_parallel)

        tr_num = 0
        for i, item in enumerate(html_paragraphs_iter):
            if len(item.sub_paragraph_items) == 0:
                self.process_translate(item.paragraph.text, translate_responses[tr_num].result, soup,
                                       item.paragraph, req.preserve_original_text)
                tr_num = tr_num + 1

        return parse_result

    def get_translate_req(self, text: str, previous_text_items: list[str],
                          req: dto.ProcessingFileDirReq) -> dto.TranslateCommonRequest:
        context = file_processor.get_context(items_to_context=previous_text_items,
                                             params=self.context_params,
                                             translate_text=text)
        previous_text_items.append(text)
        return req.translate_req(text=text, context=context)

    def translate_requests(self, translate_reqs: list[dto.TranslateCommonRequest],
                           gpu_count_for_parallel: int | None) -> list[dto.TranslateResp]:
        translate_responses: list[dto.TranslateResp] = []
        if gpu_count_for_parallel is None:
            for translate_req in translate_reqs:
                resp = self.translate_func(translate_req)
                translate_responses.append(resp)
        else:
            translate_responses = parallel_process.start_parallel_processing(
                gpu_count_for_parallel, self.core, translate_reqs)

        return translate_responses

    def process_translate(self, original_text: str, translate_text: str, soup: BeautifulSoup, tag: Tag,
                          preserve_original_text: bool) -> None:
        if translate_text == original_text or translate_text.strip() == '':
            return

        translate_element = self.html_parser.get_translate_element(soup, tag, translate_text)
        if preserve_original_text:
            if tag.name == "span":
                br_tag = soup.new_tag("br")
                tag.append(br_tag)
            tag.insert_after(translate_element)
            original_element = self.html_parser.get_original_element(soup, tag, original_text)
            if original_element:
                tag.replaceWith(original_element)
        tag.append(translate_element)

    def process_header_translate(self, tag: Tag, translate_text: str, preserve_original_text: bool) -> None:
        if tag.text == translate_text:
            return

        if preserve_original_text:
            tag.string = f'{tag.text} {self.header_delimiter} {translate_text}'
        else:
            tag.string = translate_text
