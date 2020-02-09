"Unit test for process"
from typing import cast

from dolphin_doc_lib.base.text import TextParagraph, TextSegment
from dolphin_doc_lib.process import process, Content, ContentSource
from dolphin_doc_lib.base.doc import Doc


def test_plain_text():
    text = "paragraph 1\nparagraph 2\n\n  \n  \nparagraph 3\n"
    doc = process(Content(data=text))

    par1 = TextParagraph().append_text_segment(TextSegment("paragraph 1"))
    par2 = TextParagraph().append_text_segment(TextSegment("paragraph 2"))
    par3 = TextParagraph().append_text_segment(TextSegment("paragraph 3"))
    expect_doc = Doc().append_blocks([par1, par2, par3])

    assert doc == expect_doc


def test_plain_text_from_file():
    doc = process(
        Content(source=ContentSource.FILE,
                path="dolphin_doc_lib/testdata/plain_text.txt"))

    par1 = TextParagraph().append_text_segment(TextSegment("paragraph 1"))
    par2 = TextParagraph().append_text_segment(TextSegment("paragraph 2"))
    par3 = TextParagraph().append_text_segment(TextSegment("paragraph 3"))
    par4 = TextParagraph().append_text_segment(TextSegment("paragraph 4"))
    expect_doc = Doc().append_blocks([par1, par2, par3, par4])

    assert doc == expect_doc
