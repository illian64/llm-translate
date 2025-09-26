from typing import Iterator

from bs4 import BeautifulSoup, PageElement, Tag

from app import file_processor
from app.app_core import AppCore
from app.dto import ProcessingFileDirReq


class FileProcessorHtml:
    attribute_source = "data-src"
    attribute_translate = "data-tr"

    def __init__(self, core: AppCore, options: dict):
        self.core = core
        self.options = options
        self.header_tags = options["header_tags"]
        self.text_tags = options["text_tags"]
        self.original_tag: str = options["text_format"]["original_tag"]
        self.translate_tag: str = options["text_format"]["translate_tag"]
        self.header_delimiter: str = options["text_format"]["header_delimiter"]
        self.context_params = core.file_processing_params.context_params

    def get_translate_element(self, soup: BeautifulSoup, child: PageElement, translate_txt: str) -> Tag:
        translate_element = soup.new_tag(child.parent.name)
        translate_element[self.attribute_translate] = "1"
        if self.translate_tag == "":
            translate_element.string = translate_txt
        else:
            additional_tag_element = soup.new_tag(self.translate_tag)
            additional_tag_element.string = translate_txt
            translate_element.append(additional_tag_element)

        return translate_element

    def get_original_element(self, soup: BeautifulSoup, child: PageElement, original_text: str) -> None | Tag:
        if self.original_tag == "":
            return None
        else:
            original_element = soup.new_tag(child.parent.name)
            additional_tag_element = soup.new_tag(self.original_tag)
            additional_tag_element.string = original_text
            original_element.append(additional_tag_element)
            return original_element

    def process(self, req: ProcessingFileDirReq, soup: BeautifulSoup, body_tag: str = None) -> None:
        translate_only_first_paragraphs: int = self.options.get("translate_only_first_paragraphs", 0)
        children: Iterator[PageElement] = soup.find(body_tag).descendants if body_tag else soup.descendants
        translated_paragraphs = 0

        all_original_text_items: list[str] = []

        for child in children:
            if (child and child.text and child.parent and child.parent.get(self.attribute_source) is None
                    and child.parent.get(self.attribute_translate) is None):
                child_tag = child.parent.name
                if child_tag and child.parent.text and (child_tag in self.text_tags or child_tag in self.header_tags):
                    # get contents - for example <p><b>1</b>2<i>3</i><p> - 3 items. 1, 3 - tags, 2 - simple string
                    # contents = child.parent.contents - for translate with save format within paragraph

                    child.parent[self.attribute_source] = "1"
                    original_text = child.parent.text

                    # generate context before add text in all_original_text_items
                    context = file_processor.get_context(items_to_context=all_original_text_items,
                                                         params=self.context_params, translate_text=original_text)

                    all_original_text_items.append(original_text)

                    translate_req = req.translate_req(text=original_text, context=context)
                    translate_txt = self.core.translate(translate_req).result
                    translated_paragraphs = translated_paragraphs + 1
                    if 0 < translate_only_first_paragraphs <= translated_paragraphs:
                        break

                    if child_tag in self.text_tags:
                        translate_element = self.get_translate_element(soup, child, translate_txt)
                        if req.preserve_original_text:
                            child.parent.insert_after(translate_element)
                            original_element = self.get_original_element(soup, child, original_text)
                            if original_element:
                                child.replaceWith(original_element)
                        else:
                            child.replaceWith(translate_element)

                    elif child_tag in self.header_tags:
                        if req.preserve_original_text:
                            child.parent.string = f'{original_text}{self.header_delimiter}{translate_txt}'
                        else:
                            child.parent.string = translate_txt

