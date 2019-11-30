from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Cell, Direction, Table
from dolphin_doc_lib.base.text import TextSegment, TextParagraph


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
    table.add_cell(cell1).add_cell(cell2).add_cell(cell3).add_cell(
        cell4).add_cell(cell5)

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