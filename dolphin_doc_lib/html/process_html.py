from typing import List, NamedTuple, cast
from bs4 import BeautifulSoup, NavigableString

from dolphin_doc_lib.base.doc import Doc, BlockType
from dolphin_doc_lib.base.table import Table
from dolphin_doc_lib.base.text import TextParagraph, TextSegment


class _BlocksInfo(NamedTuple):
    "HTML element in dolphin Block form, it is intermediate result during converting"
    blocks: List[BlockType] = []
    first_block_mergeable: bool = False
    last_block_mergeable: bool = False


def _merge_block(block1: BlockType, block2: BlockType) -> BlockType:
    if type(block1) is TextParagraph and type(block2) is TextParagraph:
        block = cast(TextParagraph, block1)
        for segment in cast(TextParagraph, block2).segments():
            block = block.append_text_segment(segment)
        return block
    raise ValueError(
        "Not able to merge block that is not TextParagraph: {}, {}".format(
            type(block1), type(block2)))


def _merge_blocks_info(info1: _BlocksInfo, info2: _BlocksInfo) -> _BlocksInfo:
    if not info1.blocks:
        return info2
    if not info2.blocks:
        return info1

    blocks: List[BlockType] = []
    if info1.last_block_mergeable and info2.last_block_mergeable:
        merged_block = _merge_block(info1.blocks[-1], info2.blocks[0])
        blocks = info1.blocks[:-1] + [merged_block] + info2.blocks[1:]
    else:
        blocks = info1.blocks + info2.blocks
    return _BlocksInfo(blocks=blocks,
                       first_block_mergeable=info1.first_block_mergeable,
                       last_block_mergeable=info2.last_block_mergeable)


FORCE_SPLIT_TAGS = [
    'p',
]


def _convert_to_blocks_info(soup) -> _BlocksInfo:
    if type(soup) is NavigableString:
        if len(soup.strip()) == 0:
            return _BlocksInfo()
        par = TextParagraph().append_text_segment(TextSegment(soup.strip()))
        return _BlocksInfo(blocks=[par],
                           first_block_mergeable=True,
                           last_block_mergeable=True)

    blocks_info = _BlocksInfo()
    for child in soup:
        blocks_info = _merge_blocks_info(blocks_info,
                                         _convert_to_blocks_info(child))

    if soup.name in FORCE_SPLIT_TAGS:
        blocks_info = _BlocksInfo(blocks=blocks_info.blocks)

    return blocks_info


def process_html(html: str) -> Doc:
    "Create Dolphin Doc from html"
    soup = BeautifulSoup(html, 'html5lib').body
    blocks_info = _convert_to_blocks_info(soup)
    doc = Doc()
    for block in blocks_info.blocks:
        doc.append_block(block)
    return doc


from pathlib import Path
if __name__ == '__main__':
    html = Path("dolphin_doc_lib/testdata/test.html").read_text()
    doc = process_html(html)
    doc.print()