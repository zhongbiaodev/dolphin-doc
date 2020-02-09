from pathlib import Path
from dolphin_doc_lib.html.process_html import process_html
from dolphin_doc_lib.base.text import TextParagraph, TextSegment
from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Table, Cell
from dolphin_doc_lib.base.doc import Doc


def test_line_break_tags():
    html = "<p>abc</p> <p>This text contains<br>a line break.</p>"
    doc = process_html(html)

    par1 = TextParagraph().append_text_segment(TextSegment("abc"))
    par2 = TextParagraph().append_text_segment(
        TextSegment("This text contains"))
    par3 = TextParagraph().append_text_segment(TextSegment("a line break."))
    expect_doc = Doc().append_blocks([par1, par2, par3])

    assert doc.to_dict() == expect_doc.to_dict()


def test_standard_table():
    html = """
<table>
  <thead>
    <tr>
      <th>Month</th>
      <th>Savings</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>January</td>
      <td>$100</td>
    </tr>
    <tr>
      <td>February</td>
      <td>$80</td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td>Sum</td>
      <td>$180</td>
    </tr>
  </tfoot>
</table>"""
    doc = process_html(html)

    cell1 = Cell(Rect[int](0, 0, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("Month")))
    cell2 = Cell(Rect[int](1, 0, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("Savings")))
    cell3 = Cell(Rect[int](0, 1, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("January")))
    cell4 = Cell(Rect[int](1, 1, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("$100")))
    cell5 = Cell(Rect[int](0, 2, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("February")))
    cell6 = Cell(Rect[int](1, 2, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("$80")))
    cell7 = Cell(Rect[int](0, 3, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("Sum")))
    cell8 = Cell(Rect[int](1, 3, 1, 1)).append_paragraph(
        TextParagraph().append_text_segment(TextSegment("$180")))
    expect_doc = Doc().append_block(
        Table(4, 2, [cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8]))
    assert doc.to_dict() == expect_doc.to_dict()