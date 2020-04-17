from pathlib import Path
from dolphin_doc_lib.html.process_html import process_html
from dolphin_doc_lib.base.text import TextParagraph, TextSegment
from dolphin_doc_lib.base.rect import Rect
from dolphin_doc_lib.base.table import Table, Cell
from dolphin_doc_lib.base.doc import Doc


def test_line_break_tags():
    html = """a<p>b<br>c<h1>d<h2>e<h3>f<h4>g<h5>h<h6>i<pre>j<address>k<blockquote>l
    <dl>m<div>n<fieldset>o<form>p<hr>q<ol>r<ul>s<li>t
    """
    doc = process_html(html)

    expect_doc = Doc().append_blocks([
        TextParagraph().append_text_segment(TextSegment("a")),
        TextParagraph().append_text_segment(TextSegment("b")),
        TextParagraph().append_text_segment(TextSegment("c")),
        TextParagraph().append_text_segment(TextSegment("d")),
        TextParagraph().append_text_segment(TextSegment("e")),
        TextParagraph().append_text_segment(TextSegment("f")),
        TextParagraph().append_text_segment(TextSegment("g")),
        TextParagraph().append_text_segment(TextSegment("h")),
        TextParagraph().append_text_segment(TextSegment("i")),
        TextParagraph().append_text_segment(TextSegment("j")),
        TextParagraph().append_text_segment(TextSegment("k")),
        TextParagraph().append_text_segment(TextSegment("l")),
        TextParagraph().append_text_segment(TextSegment("m")),
        TextParagraph().append_text_segment(TextSegment("n")),
        TextParagraph().append_text_segment(TextSegment("o")),
        TextParagraph().append_text_segment(TextSegment("p")),
        TextParagraph().append_text_segment(TextSegment("q")),
        TextParagraph().append_text_segment(TextSegment("r")),
        TextParagraph().append_text_segment(TextSegment("s")),
        TextParagraph().append_text_segment(TextSegment("t")),
    ])

    assert doc.to_dict() == expect_doc.to_dict()


def test_ignore_tags():
    html = """a<style>b</style><script>c</script><noscript>d</noscript>e"""
    doc = process_html(html)

    expect_doc = Doc().append_blocks([
        TextParagraph().append_text_segment(TextSegment("ae")),
    ])

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

    expect_doc = Doc().append_block(
        Table(4, 2, [
            Cell(Rect[int](0, 0, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("Month"))),
            Cell(Rect[int](1, 0, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("Savings"))),
            Cell(Rect[int](0, 1, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("January"))),
            Cell(Rect[int](1, 1, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("$100"))),
            Cell(Rect[int](0, 2, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("February"))),
            Cell(Rect[int](1, 2, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("$80"))),
            Cell(Rect[int](0, 3, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("Sum"))),
            Cell(Rect[int](1, 3, 1, 1)).append_paragraph(
                TextParagraph().append_text_segment(TextSegment("$180"))),
        ]))
    assert doc.to_dict() == expect_doc.to_dict()