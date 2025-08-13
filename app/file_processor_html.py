from bs4 import BeautifulSoup, PageElement, Tag

from app.app_core import AppCore
from app.dto import ProcessingFileDirReq


class FileProcessorHtml:
    def __init__(self, core: AppCore, options: dict):
        self.core = core
        self.header_tags = options["header_tags"]
        self.text_tags = options["text_tags"]
        self.original_tag: str = options["text_format"]["original_tag"]
        self.translate_tag: str = options["text_format"]["translate_tag"]
        self.header_delimiter: str = options["text_format"]["header_delimiter"]

    def get_translate_element(self, soup: BeautifulSoup, child: PageElement, translate_txt: str) -> Tag:
        translate_element = soup.new_tag(child.parent.name)
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

    def process(self, req: ProcessingFileDirReq, soup: BeautifulSoup) -> None:
        for child in soup.descendants:
            if child and child.text and child.parent:
                child_tag = child.parent.name
                if child_tag and child.parent.string and (child_tag in self.text_tags or child_tag in self.header_tags):
                    original_text = child.parent.string

                    translate_req = req.translate_req(original_text)
                    translate_txt = self.core.translate(translate_req).result

                    if child_tag in self.text_tags:
                        translate_element = self.get_translate_element(soup, child, translate_txt)
                        if req.preserve_original_text:
                            child.insert_after(translate_element)
                            original_element = self.get_original_element(soup, child, original_text)
                            if original_element:
                                child.replaceWith(original_element)
                        else:
                            child.replaceWith(translate_element)

                    if child_tag in self.header_tags:
                        if req.preserve_original_text:
                            child.parent.string = f'{original_text}{self.header_delimiter}{translate_txt}'
                        else:
                            child.parent.string = translate_txt
