from enum import Enum
from typing import Dict, List, Optional, Any, NamedTuple

from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.text import TextParagraph

_UNOCCUPIED_CELL = -1


class Direction(Enum):
    "Direction for movement"
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Cell(Rect[int]):
    "Class that represents a table cell."

    def __init__(self, rect: Rect[int]):
        self.parent: Optional["Table"] = None
        self._paragraphs: List[TextParagraph] = []
        Rect.__init__(self, rect.left(), rect.top(), rect.width(),
                      rect.height())

    def append_paragraph(self, paragraph: TextParagraph) -> "Cell":
        "Append a paragraph"
        if paragraph.parent:
            raise ValueError(
                "Should not append a paragraph that already has a parent")
        paragraph.parent = self
        self._paragraphs.append(paragraph)
        return self

    def append_paragraphs(self, paragraphs: List[TextParagraph]) -> "Cell":
        for par in paragraphs:
            self.append_paragraph(par)
        return self

    def move(self, direction: Direction) -> Optional["Cell"]:
        "Return the next Cell follow the direction. None if already reach the boundary."
        assert self.parent
        return self.parent.move(self, direction)

    def is_empty(self) -> bool:
        return len(self._paragraphs) == 0

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {
            "type": "cell",
            "rect": super().to_dict(),
            "paragraphs": list(map(lambda p: p.to_dict(), self._paragraphs))
        }


class TableSection(NamedTuple):
    "Layout result of List[List[Cell]], table section size and cell position is calculated"
    row_num: int = 0
    col_num: int = 0
    cells: List[Cell] = []


def layout_cells(cell_mat: List[List[Cell]]) -> TableSection:
    cell_mat = [cell_row for cell_row in cell_mat if cell_row]
    if not cell_mat:
        return TableSection()

    row_num: int = 0
    col_num: int = sum([cell.width() for cell in cell_mat[0]])
    height_per_col = [0] * col_num
    cells: List[Cell] = []
    for cell_row in cell_mat:
        cur_height = min(height_per_col)
        empty_slots = [
            i for i, h in enumerate(height_per_col) if h == cur_height
        ]
        for cell in cell_row:
            width = cell.width()
            assert width <= len(empty_slots)
            assert empty_slots[width - 1] - empty_slots[0] == width - 1
            cell.set_position(empty_slots[0], cur_height)
            cells.append(cell)
            height_per_col[empty_slots[0]:empty_slots[0] +
                           width] = [cur_height + cell.height()] * width
            empty_slots = empty_slots[width:]
        assert len(empty_slots) == 0

    assert max(height_per_col) == min(height_per_col)

    return TableSection(height_per_col[0], col_num, cells)


class Table(Rect[int]):
    "Class that stores list of cells"
    parent: Optional[Any] = None
    _cells: List[Cell] = []

    _board: List[List[int]]
    _occupied_area: int
    _ready_to_move: bool

    def __init__(self, row_num: int, col_num: int, cells: List[Cell] = []):
        super().__init__(0, 0, col_num, row_num)
        self.parent = None
        self._cells = []
        self._occupied_area = 0
        self._board = [[_UNOCCUPIED_CELL for x in range(col_num)]
                       for y in range(row_num)]
        self._ready_to_move = False
        if cells:
            self.add_cells(cells)

    def cells(self) -> List[Cell]:
        return self._cells

    def _fill_board(self, cell: Cell, idx: int):
        for row in range(cell.top(), cell.bottom() + 1):
            for col in range(cell.left(), cell.right() + 1):
                self._board[row][col] = idx

        self._occupied_area += cell.area()

    def add_cell(self, cell: Cell) -> "Table":
        "Add a new cell to the table."
        if not self.contains(cell):
            raise ValueError("Cell is not inside the table")

        for row in range(cell.top(), cell.bottom() + 1):
            for col in range(cell.left(), cell.right() + 1):
                if self._board[row][col] != _UNOCCUPIED_CELL:
                    raise ValueError(
                        "Point (row = {}, col = {}) already occupied".format(
                            row, col))

        cell.parent = self
        self._cells.append(cell)
        self._fill_board(cell, len(self._cells) - 1)
        if self._occupied_area == self.area():
            self._sort_cells()
            self._ready_to_move = True
        return self

    def add_cells(self, cells: List[Cell]) -> "Table":
        for cell in cells:
            self.add_cell(cell)
        return self

    def ready_to_move(self) -> bool:
        "Return whether all the cells are added"
        return self._ready_to_move

    def _sort_cells(self) -> None:
        self._cells.sort(key=lambda cell: (cell.top(), cell.left()))
        self._occupied_area = 0
        for i, _cell in enumerate(self._cells):
            self._fill_board(_cell, i)

    def move(self, cell: Cell, direction: Direction) -> Optional[Cell]:
        "Find the cell follow the direction. None if reach the boundary."
        assert self.ready_to_move()
        if cell.parent is not self:
            raise ValueError("The cell parent is not this table")
        x: int = 0
        y: int = 0
        if direction == Direction.UP:
            x, y = cell.left(), cell.top() - 1
        elif direction == Direction.DOWN:
            x, y = cell.left(), cell.bottom() + 1
        elif direction == Direction.LEFT:
            x, y = cell.left() - 1, cell.top()
        else:
            x, y = cell.right() + 1, cell.top()
        if self.contains_point(x, y):
            return self._cells[self._board[y][x]]
        return None

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {
            "type": "table",
            "cells": list(map(lambda cell: cell.to_dict(), self._cells))
        }