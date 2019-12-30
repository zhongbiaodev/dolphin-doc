from pathlib import Path
from dolphin_doc_lib.html.process_html import process_html


def test_process_html():
    html = Path("dolphin_doc_lib/testdata/test.html").read_text()
    doc = process_html(html)
