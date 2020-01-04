from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Cell, Direction, Table, layout_cells
from dolphin_doc_lib.base.text import TextSegment, TextParagraph


def create_cell(x: int, y: int) -> Cell:
    return Cell(Rect[int](0, 0, x, y))


def assert_cell(cell: Cell, x: int, y: int, w: int, h: int) -> None:
    assert cell.left() == x
    assert cell.top() == y
    assert cell.width() == w
    assert cell.height() == h


def test_layout_cells():
    table_section = layout_cells([[create_cell(1, 1),
                                   create_cell(1, 1)],
                                  [create_cell(1, 1),
                                   create_cell(1, 1)]])

    assert table_section.row_num == 2
    assert table_section.col_num == 2
    assert_cell(table_section.cells[0], 0, 0, 1, 1)
    assert_cell(table_section.cells[1], 1, 0, 1, 1)
    assert_cell(table_section.cells[2], 0, 1, 1, 1)
    assert_cell(table_section.cells[3], 1, 1, 1, 1)

    # C1, C2, C3, C3
    # C4, C2, C5, C6
    # C4, C7, C7, C6
    # C8, C8, C9, C6
    table_section = layout_cells(
        [[create_cell(1, 1),
          create_cell(1, 2),
          create_cell(2, 1)],
         [create_cell(1, 2),
          create_cell(1, 1),
          create_cell(1, 3)], [create_cell(2, 1)],
         [create_cell(2, 1), create_cell(1, 1)]])

    assert table_section.row_num == 4
    assert table_section.col_num == 4
    assert_cell(table_section.cells[0], 0, 0, 1, 1)
    assert_cell(table_section.cells[1], 1, 0, 1, 2)
    assert_cell(table_section.cells[2], 2, 0, 2, 1)
    assert_cell(table_section.cells[3], 0, 1, 1, 2)
    assert_cell(table_section.cells[4], 2, 1, 1, 1)
    assert_cell(table_section.cells[5], 3, 1, 1, 3)
    assert_cell(table_section.cells[6], 1, 2, 2, 1)
    assert_cell(table_section.cells[7], 0, 3, 2, 1)
    assert_cell(table_section.cells[8], 2, 3, 1, 1)


def test_move_cell():
    # Table with 2 rows, 3 cols.
    # C1, C3, C5
    # C2, C4, C5
    table = Table(2, 3)  # 2 rows, 3 cols
    cell1 = Cell(Rect[int](0, 0, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("C1")))
    cell2 = Cell(Rect[int](0, 1, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("C2")))
    cell3 = Cell(Rect[int](1, 0, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("C3")))
    cell4 = Cell(Rect[int](1, 1, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("C4")))
    cell5 = Cell(Rect[int](2, 0, 1, 2)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("C5")))

    table.add_cell(cell1).add_cell(cell5).add_cell(cell4).add_cell(cell3)
    assert table.cells()[0] == cell1
    assert table.cells()[1] == cell5
    assert table.cells()[2] == cell4
    assert table.cells()[3] == cell3

    table.add_cell(cell2)
    assert table.cells()[0] == cell1
    assert table.cells()[1] == cell3
    assert table.cells()[2] == cell5
    assert table.cells()[3] == cell2
    assert table.cells()[4] == cell4

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