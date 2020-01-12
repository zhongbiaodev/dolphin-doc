from typing import List, NamedTuple, Optional, List, Union, cast
from bs4 import BeautifulSoup, NavigableString

from dolphin_doc_lib.base.doc import Doc, BlockType
from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Table, Cell, layout_cells
from dolphin_doc_lib.base.text import TextParagraph, TextSegment

from dolphin_doc_lib.html.block_info import BlocksInfo, merge_blocks_info_list

FORCE_SPLIT_TAGS = ['p', 'br']

CELL_TAGS = ['td', 'th']
TABLE_ROW_TAG = 'tr'
TABLE_SECTION_TAGS = ['tbody', 'thead', 'tfoot']
TABLE_TAG = 'table'

# BlocksInfo for general case
# Cell for node with tag td, th
# List[Cell] for node with tag tr
# List[List[Cell]] for node with tag tbody, thead and tfoot
ProcessOutput = Union[BlocksInfo, Cell, List[Cell], List[List[Cell]]]


# empty BlockInfo introduced by "\n"
def _empty_blocks_info(output: ProcessOutput) -> bool:
    return type(output) is BlocksInfo and not cast(BlocksInfo, output).blocks


def _process_string_node(node) -> BlocksInfo:
    # strip string to mimic browser behavior, not 100% accurate
    content: str = node.strip()
    if not content:
        return BlocksInfo()

    par = TextParagraph().append_text_segment(TextSegment(content))
    return BlocksInfo(blocks=[par])


def _process_cell_node(node, outputs: List[ProcessOutput]) -> Cell:
    colspan = int(node.attrs['colspan']) if node.has_attr('colspan') else 1
    rowspan = int(node.attrs['rowspan']) if node.has_attr('rowspan') else 1
    # rowspan = "0" or colspan = "0" is not supported.
    cell = Cell(Rect[int](0, 0, colspan, rowspan))

    blocks_info = merge_blocks_info_list(
        [cast(BlocksInfo, o) for o in outputs])
    cell.append_paragraphs(
        [cast(TextParagraph, block) for block in blocks_info.blocks])
    return cell


def _process_table_row_node(outputs: List[ProcessOutput]) -> List[Cell]:
    casted_outputs = [cast(Cell, o) for o in outputs]
    if all(cell.is_empty() for cell in casted_outputs):
        return []
    return casted_outputs


def _process_table_section_node(
        outputs: List[ProcessOutput]) -> List[List[Cell]]:
    return [cast(List[Cell], o) for o in outputs]


def _process_table_node(outputs: List[ProcessOutput]) -> BlocksInfo:
    cells: List[List[Cell]] = []
    for o in outputs:
        cells.extend(cast(List[List[Cell]], o))

    result = layout_cells(cells)
    if not result.cells:
        return BlocksInfo().make_non_mergeable()

    table = Table(result.row_num, result.col_num, result.cells)
    return BlocksInfo(blocks=[table]).make_non_mergeable()


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
        children_outputs = [
            o for o in children_outputs if not _empty_blocks_info(o)
        ]
        return _process_table_row_node(children_outputs)

    if node.name in TABLE_SECTION_TAGS:
        children_outputs = [
            o for o in children_outputs if not _empty_blocks_info(o)
        ]
        return _process_table_section_node(children_outputs)

    if node.name == TABLE_TAG:
        children_outputs = [
            o for o in children_outputs if not _empty_blocks_info(o)
        ]
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
    doc = Doc().append_blocks(blocks_info.blocks)
    return doc


from pathlib import Path
if __name__ == '__main__':
    html = Path(
        "/Users/jzfeng/MyProjects/dolphin-doc/dolphin_doc_lib/testdata/test.html"
    ).read_text()
    doc = process_html(html)
    doc.print()