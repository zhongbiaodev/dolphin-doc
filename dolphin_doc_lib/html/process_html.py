from typing import List, NamedTuple, Optional, List, Union, cast
from bs4 import BeautifulSoup, NavigableString

from dolphin_doc_lib.base.doc import Doc, BlockType
from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Table, Cell
from dolphin_doc_lib.base.text import TextParagraph, TextSegment

from dolphin_doc_lib.html.block_info import BlocksInfo, merge_blocks_info_list

FORCE_SPLIT_TAGS = [
    'p',
]

CELL_TAGS = ['td', 'th']
TABLE_ROW_TAG = 'tr'
TABLE_SECTION_TAGS = ['tbody', 'thead', 'tfoot']
TABLE_TAG = 'table'

# BlocksInfo for general case
# Cell for node with tag td, th
# List[Cell] for node with tag tr
# List[List[Cell]] for node with tag tbody, thead and tfoot
ProcessOutput = Union[BlocksInfo, Cell, List[Cell], List[List[Cell]]]


def _process_string_node(node) -> BlocksInfo:
    # strip string to mimic browser behavior, not 100% accurate
    content: str = node.strip()
    if not content:
        return BlocksInfo()

    par = TextParagraph().append_text_segment(TextSegment(content))
    return BlocksInfo(blocks=[par],
                      first_block_mergeable=True,
                      last_block_mergeable=True)


def _process_cell_node(node, outputs: List[ProcessOutput]) -> Cell:
    blocks_info = merge_blocks_info_list(
        [cast(BlocksInfo, o) for o in outputs])

    colspan = int(node.attrs['colspan']) if node.has_attr('colspan') else 1
    rowspan = int(node.attrs['rowspan']) if node.has_attr('rowspan') else 1
    cell = Cell(Rect[int](0, 0, colspan, rowspan))
    for block in blocks_info.blocks:
        cell.append_paragraph(cast(TextParagraph, block))
    return cell


def _process_table_row_node(outputs: List[ProcessOutput]) -> List[Cell]:
    return [cast(Cell, o) for o in outputs]


def _process_table_section_node(
        outputs: List[ProcessOutput]) -> List[List[Cell]]:
    return [cast(List[Cell], o) for o in outputs]


def _process_table_node(outputs: List[ProcessOutput]) -> BlocksInfo:
    return BlocksInfo()


# traverse the tree using dfs
def _process(node) -> ProcessOutput:
    # process leaf nodes
    if type(node) is NavigableString:
        return _process_string_node(node)

    # process non-leaf nodes
    children_outputs: List[ProcessOutput] = [_process(child) for child in node]

    if node.name in CELL_TAGS:
        return _process_cell_node(node, children_outputs)

    if node.name == TABLE_ROW_TAG:
        return _process_table_row_node(children_outputs)

    if node.name in TABLE_SECTION_TAGS:
        return _process_table_section_node(children_outputs)

    if node.name == TABLE_TAG:
        return _process_table_node(children_outputs)

    blocks_info = merge_blocks_info_list(
        [cast(BlocksInfo, o) for o in children_outputs])

    if node.has_attr('href'):
        blocks_info.attach_link(node['href'])

    if node.name in FORCE_SPLIT_TAGS:
        blocks_info.make_non_mergeable()

    return blocks_info


def process_html(html: str) -> Doc:
    "Create Dolphin Doc from html"
    root = BeautifulSoup(html, 'html5lib').body
    blocks_info = cast(BlocksInfo, _process(root))
    doc = Doc()
    for block in blocks_info.blocks:
        doc.append_block(block)
    return doc


from pathlib import Path
if __name__ == '__main__':
    html = Path("dolphin_doc_lib/testdata/test.html").read_text()
    doc = process_html(html)
    doc.print()