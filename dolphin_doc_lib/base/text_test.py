"Unit test for text"
from dolphin_doc_lib.base.text import TextSegment, TextParagraph


def test_merge_segments():
    par = TextParagraph() \
        .append_text_segment(TextSegment("Hello ")) \
        .append_text_segment(TextSegment("World!"))
    assert len(par.segments()) == 1
    assert par.segments()[0].text() == "Hello World!"


def test_merge_segments_with_link():
    # This is a link: <a href="http://www.example.com"> link </a>.
    par = TextParagraph() \
        .append_text_segment(TextSegment("This is a link: ")) \
        .append_text_segment(TextSegment("example", "http://www.example.com")) \
        .append_text_segment(TextSegment("."))
    assert len(par.segments()) == 3
    assert par.segments()[0].text() == "This is a link: "
    assert par.segments()[1].text() == "example"
    assert par.segments()[1].link() == "http://www.example.com"
    assert par.segments()[2].text() == "."