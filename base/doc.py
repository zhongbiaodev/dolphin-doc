"Base Doc implementation"
from typing import Dict, List, Optional, Union
import copy
from enum import Enum
import json
from base.rect import Rect


class TextSegment():
    "Class that stores a text segment, a hyperlink could be attached."
    parent: Optional['TextParagraph'] = None
    _text: str
    _link: Optional[str] = None

    def __init__(self, text: str, link: Optional[str] = None):
        if not text:
            raise ValueError("|text| must not be empty")
        self._text = text
        self._link = link

    def text(self) -> str:
        "Return text content"
        return self._text

    def append_text(self, new_text: str) -> None:
        "Append text to the current text"
        if not new_text:
            raise ValueError("|new_text| must not be empty")
        self._text += new_text

    def link(self) -> Optional[str]:
        "Return link content, None if there is no link attached."
        return self._link

    def to_dict(self) -> Dict[str, str]:
        "dict version for json encoding"
        d = {"text": self._text}
        if self._link is not None:
            d["link"] = self._link
        return d


class TextParagraph():
    '''Class that stores a list of TextSegments.

    All the TextSegments are assumed to be concatenated horizontally.
    '''
    parent: Optional['VerticalBlocks'] = None
    _segments: List[TextSegment] = []

    def __init__(self):
        self.parent = None
        self._segments = []

    def append_text_segment(self, segment: TextSegment) -> 'TextParagraph':
        '''Append a text segment to the paragraph.

        The new segment would be merged with the last segment
        if neither of them has link attached.
        '''
        if segment.parent:
            raise ValueError(
                "Should not append a text segment that already has a parent")
        if self._segments and not self._segments[-1].link() and not segment.link():
            self._segments[-1].append_text(segment.text())
            return self
        new_segment = copy.copy(segment)
        new_segment.parent = self
        self._segments.append(new_segment)
        return self

    def segments(self):
        "Return all segments"
        return self._segments

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {"type": "paragraph",
                "segments": list(map(lambda seg: seg.to_dict(), self._segments))}


class VerticalBlocks():
    '''Class that stores a list of Blocks.

    The blocks are in vertical direction. A block could be a TextParagraph or a Table.
    '''
    parent: Optional['Table'] = None
    _blocks: List['_BlockType'] = []

    def __init__(self):
        self.parent = None
        self._blocks = []

    def append_block(self, block: '_BlockType'):
        "Append a block"
        if block.parent:
            raise ValueError(
                "Should not append a block that already has a parent")
        block.parent = self
        self._blocks.append(block)
        return self

    def blocks(self) -> List['_BlockType']:
        "Return all the stored blocks"
        return self._blocks

    def reset(self) -> None:
        "Reset the VerticalBlocks object."
        self.parent = None
        self._blocks = []

    def merge(self, other: 'VerticalBlocks'):
        '''Merge another VerticalBlocks into the current one.

        The passed in VerticalBlocks got reset to avoid leaking corrupted object.
        '''
        if other.parent:
            raise ValueError(
                "Should not merge a VerticalBlocks that already has a parent")
        for block in other.blocks():
            block.parent = None
            self.append_block(block)
        other.reset()

    def _to_dict(self, label: str) -> Dict:
        return {"type": label,
                "blocks": list(map(lambda block: block.to_dict(), self._blocks))}


class Doc(VerticalBlocks):
    "General Doc"

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return super()._to_dict("table")

    def append_block(self, block: '_BlockType'):
        super().append_block(block)
        return self


class Direction(Enum):
    "Direction for movement"
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Cell(VerticalBlocks, Rect[int]):
    "Class that represents a table cell."

    def __init__(self, rect: Rect[int]):
        VerticalBlocks.__init__(self)
        Rect.__init__(self, rect.left(), rect.top(),
                      rect.width(), rect.height())

    def append_block(self, block: '_BlockType'):
        super().append_block(block)
        return self

    def move(self, direction: Direction) -> Optional['Cell']:
        "Return the next Cell follow the direction. None if already reach the boundary."
        assert self.parent
        return self.parent.move(self, direction)

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return super()._to_dict("cell")


_UNOCCUPIED_CELL = -1


class Table(Rect[int]):
    "Class that stores list of cells"
    parent: Optional['VerticalBlocks'] = None
    _cells: List[Cell] = []

    _board: List[List[int]]
    _occupied_area: int

    def __init__(self, row_num: int, col_num: int):
        super().__init__(0, 0, col_num, row_num)
        self.parent = None
        self._cells = []
        self._occupied_area = 0
        self._board = [[_UNOCCUPIED_CELL for x in range(
            col_num)] for y in range(row_num)]

    def _fill_board(self, cell: Cell, idx: int):
        for row in range(cell.top(), cell.bottom()+1):
            for col in range(cell.left(), cell.right()+1):
                self._board[row][col] = idx

        self._occupied_area += cell.area()

    def add_cell(self, cell: Cell) -> 'Table':
        "Add a new cell to the table."
        if not self.contains(cell):
            raise ValueError("Cell is not inside the table")

        for row in range(cell.top(), cell.bottom()+1):
            for col in range(cell.left(), cell.right()+1):
                if self._board[row][col] != _UNOCCUPIED_CELL:
                    raise ValueError(
                        "Point (row = {}, col = {}) already occupied".format(row, col))

        cell.parent = self
        self._cells.append(cell)
        self._cells.sort(key=lambda cell: (cell.top(), cell.left()))
        self._occupied_area = 0
        for i, _cell in enumerate(self._cells):
            self._fill_board(_cell, i)
        return self

    def ready_to_move(self) -> bool:
        "Return whether all the cells are added"
        return self._occupied_area == self.area()

    def move(self, cell: Cell, direction: Direction) -> Optional[Cell]:
        "Find the Cell above the given cell. None if the cell is at the top."
        assert self.ready_to_move()
        if cell.parent is not self:
            raise ValueError("The cell parent is not this table")
        x: int = 0
        y: int = 0
        if direction == Direction.UP:
            x, y = cell.left(), cell.top()-1
        elif direction == Direction.DOWN:
            x, y = cell.left(), cell.bottom()+1
        elif direction == Direction.LEFT:
            x, y = cell.left()-1, cell.top()
        else:
            x, y = cell.right()+1, cell.top()
        if self.contains_point(x, y):
            return self._cells[self._board[y][x]]
        return None

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {"type": "Table", "cells": list(map(lambda block: block.to_dict(), self._cells))}


_BlockType = Union[TextParagraph, Table]


def _main():
    # Hello World!
    par1 = TextParagraph() \
        .append_text_segment(TextSegment("Hello ")) \
        .append_text_segment(TextSegment("World!"))
    assert len(par1.segments()) == 1
    assert par1.segments()[0].text() == "Hello World!"

    # This is a link: <a href="http://www.example.com"> link </a>.
    par2 = TextParagraph() \
        .append_text_segment(TextSegment("This is a link: ")) \
        .append_text_segment(TextSegment("example", "http://www.example.com")) \
        .append_text_segment(TextSegment("."))
    assert len(par2.segments()) == 3

    # Table with 2 rows, 3 cols.
    # C1, C3, C5
    # C2, C4, C5
    table = Table(2, 3)  # 2 rows, 3 cols
    cell1 = Cell(Rect[int](0, 0, 1, 1)).append_block(
        TextParagraph().append_text_segment(TextSegment("C1")))
    cell2 = Cell(Rect[int](0, 1, 1, 1)).append_block(
        TextParagraph().append_text_segment(TextSegment("C2")))
    cell3 = Cell(Rect[int](1, 0, 1, 1)).append_block(
        TextParagraph().append_text_segment(TextSegment("C3")))
    cell4 = Cell(Rect[int](1, 1, 1, 1)).append_block(
        TextParagraph().append_text_segment(TextSegment("C4")))
    cell5 = Cell(Rect[int](2, 0, 1, 2)).append_block(
        TextParagraph().append_text_segment(TextSegment("C5")))
    table.add_cell(cell1).add_cell(cell2).add_cell(
        cell3).add_cell(cell4).add_cell(cell5)

    assert table.ready_to_move()
    assert cell1.move(Direction.LEFT) is None
    assert cell1.move(Direction.UP) is None
    assert cell1.move(Direction.RIGHT) is cell3
    assert cell1.move(Direction.DOWN) is cell2

    assert cell2.move(Direction.LEFT) is None
    assert cell2.move(Direction.UP) is cell1
    assert cell2.move(Direction.RIGHT) is cell4
    assert cell2.move(Direction.DOWN) is None

    assert cell3.move(Direction.LEFT) is cell1
    assert cell3.move(Direction.UP) is None
    assert cell3.move(Direction.RIGHT) is cell5
    assert cell3.move(Direction.DOWN) is cell4

    assert cell4.move(Direction.LEFT) is cell2
    assert cell4.move(Direction.UP) is cell3
    assert cell4.move(Direction.RIGHT) is cell5
    assert cell4.move(Direction.DOWN) is None

    assert cell5.move(Direction.LEFT) is cell3
    assert cell5.move(Direction.UP) is None
    assert cell5.move(Direction.RIGHT) is None
    assert cell5.move(Direction.DOWN) is None

    doc = Doc().append_block(par1).append_block(par2).append_block(table)
    print(json.dumps(doc.to_dict(), indent=4))


if __name__ == '__main__':
    _main()
