"Create Dolphin Doc for various content type and source"
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from dolphin_doc_lib.base.doc import Doc
from dolphin_doc_lib.base.text import TextParagraph, TextSegment


class ContentType(Enum):
    "Supported content type"
    TEXT = 1
    IMG = 2
    HTML = 3


class ContentSource(Enum):
    "Supported content source"
    STRING = 1
    FILE = 2


class Content(NamedTuple):
    "Content to process"
    type: ContentType = ContentType.TEXT
    source: ContentSource = ContentSource.STRING
    "set data when source is STRING"
    data: str = ""
    "set path when source is FILE"
    path: str = ""


def process(content: Content) -> Doc:
    "Create Dolphin Doc from content"
    data: str
    if content.source == ContentSource.STRING:
        data = content.data
    elif content.source == ContentSource.FILE:
        data = Path(content.path).read_text()
    else:
        raise ValueError("Not a valid content source")

    if content.type == ContentType.TEXT:
        return _process_text(data)
    if content.type == ContentType.IMG:
        return _process_image(data)
    if content.type == ContentType.HTML:
        return _process_html(data)
    raise ValueError("Not a valid content type")


def _process_text(text: str) -> Doc:
    "Create Dolphin Doc from plain text"
    doc = Doc()
    for line in text.splitlines():
        line = line.strip()
        if line:
            par = TextParagraph().append_text_segment(TextSegment(line))
            doc.append_block(par)
    return doc


def _process_image(image_content: str) -> Doc:
    "Create Dolphin Doc from image"
    raise NotImplementedError


def _process_html(html: str) -> Doc:
    "Create Dolphin Doc from html"
    raise NotImplementedError
