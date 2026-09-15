from dataclasses import dataclass

from bs4 import Tag, BeautifulSoup


@dataclass
class HtmlSubParagraph:
    sub_paragraph: Tag
    text: str


@dataclass
class HtmlParagraph:
    sub_paragraph_items: list[HtmlSubParagraph]
    paragraph: Tag


@dataclass
class HtmlParseResult:
    paragraphs: list[HtmlParagraph]
    header_tags: list[Tag]


class HtmlParser:
    attribute_source = "llmt-src"
    attribute_translate = "llmt-tr"
    new_line_tag = "br"

    def __init__(self, options: dict):
        self.header_tags_names: list[str] = options["header_tags"]
        self.text_tags_names: list[str] = options["text_tags"]
        self.original_tag: str = options["text_format"]["original_tag"]
        self.translate_tag: str = options["text_format"]["translate_tag"]

    def get_translate_element(self, soup: BeautifulSoup, tag: Tag, translate_txt: str) -> Tag:
        tag[self.attribute_source] = "1"

        translate_element = soup.new_tag(tag.name)
        translate_element[self.attribute_translate] = "1"

        if self.translate_tag == "":
            translate_element.string = translate_txt
        else:
            additional_tag_element = soup.new_tag(self.translate_tag)
            additional_tag_element.string = translate_txt
            translate_element.append(additional_tag_element)

        return translate_element

    def get_original_element(self, soup: BeautifulSoup, tag: Tag, original_text: str) -> None | Tag:
        if self.original_tag == "":
            return None
        else:
            original_element = soup.new_tag(tag.name)
            additional_tag_element = soup.new_tag(self.original_tag)
            additional_tag_element.string = original_text
            original_element.append(additional_tag_element)
            return original_element

    def parse_html(self, soup: BeautifulSoup, body_tag: str | None) -> HtmlParseResult:
        base_elem = soup.find(body_tag) if body_tag else soup
        # paragraphs_amount = 0

        header_tags: list[Tag] = []
        for text_tag in self.header_tags_names:
            header_tags.extend(base_elem.find_all(text_tag))

        paragraph_tags: list[Tag] = []
        paragraphs: list[HtmlParagraph] = []
        for text_tag in self.text_tags_names:
            paragraph_tags.extend(base_elem.find_all(text_tag))

        for paragraph_tag in paragraph_tags:
            if not paragraph_tag.find_all(self.new_line_tag):
                paragraphs.append(HtmlParagraph(list(), paragraph_tag))
                continue

            # processing sub-paragraphs with <br/> tag
            sub_paragraph_items: list[HtmlSubParagraph] = []

            contents = paragraph_tag.contents
            iter_contents = contents.copy()

            if not contents:
                continue

            current_group = []
            new_contents = []

            for element in iter_contents:
                if isinstance(element, Tag) and element.name == 'br':
                    # found <br>, save current_group
                    if current_group:
                        span = soup.new_tag('span')
                        for item in current_group:
                            span.append(item)
                        new_contents.append(span)
                        sub_paragraph_items.append(HtmlSubParagraph(span, span.text))
                        current_group = []
                    new_contents.append(element)  # append <br>
                else:
                    current_group.append(element)  # append element in current group

            # processing last group (after last <br>)
            if current_group:
                span = soup.new_tag('span')
                for item in current_group:
                    span.append(item)
                new_contents.append(span)
                sub_paragraph_items.append(HtmlSubParagraph(span, span.text))

            # replace content of <p> on the new_contents
            paragraph_tag.clear()
            for item in new_contents:
                paragraph_tag.append(item)

            paragraphs.append(HtmlParagraph(sub_paragraph_items, paragraph_tag))

        return HtmlParseResult(paragraphs=paragraphs, header_tags=header_tags)
