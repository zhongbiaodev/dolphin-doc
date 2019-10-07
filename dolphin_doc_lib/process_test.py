"Unit test for process"
from typing import cast

from dolphin_doc_lib.process import process, Content, ContentSource
from dolphin_doc_lib.base.doc import TextParagraph, TextSegment


def _assert_block(block, text: str):
    assert isinstance(block, TextParagraph)
    assert cast(TextParagraph, block).segments() == [TextSegment(text)]


def test_plain_text():
    text = "paragraph 1\nparagraph 2\n\n  \n  \nparagraph 3\n"
    doc = process(Content(data=text))
    blocks = doc.blocks()
    assert len(blocks) == 3
    _assert_block(blocks[0], "paragraph 1")
    _assert_block(blocks[1], "paragraph 2")
    _assert_block(blocks[2], "paragraph 3")


def test_plain_text_from_file():
    doc = process(Content(source=ContentSource.FILE,
                          path="dolphin_doc_lib/testdata/plain_text.txt"))
    blocks = doc.blocks()
    assert len(blocks) == 4
    _assert_block(blocks[0], "paragraph 1")
    _assert_block(blocks[1], "paragraph 2")
    _assert_block(blocks[2], "paragraph 3")
    _assert_block(blocks[3], "paragraph 4")
