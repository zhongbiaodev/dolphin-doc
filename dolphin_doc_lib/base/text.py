import copy
from typing import Dict, List, Optional, Any


class TextSegment():
    "Class that stores a text segment, a hyperlink could be attached."

    def __init__(self, text: str, link: Optional[str] = None):
        if not text:
            raise ValueError("|text| must not be empty")

        self.parent: Optional["TextParagraph"] = None
        self._text: str = text
        self._link: Optional[str] = link

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
        d = {"type": "text_segment", "text": self._text}
        if self._link is not None:
            d["link"] = self._link
        return d


class TextParagraph():
    """Class that stores a list of TextSegments.

    All the TextSegments are assumed to be concatenated horizontally.
    """
    def __init__(self):
        self.parent: Optional[Any] = None
        self._segments: List[TextSegment] = []

    def append_text_segment(self, segment: TextSegment) -> "TextParagraph":
        """Append a text segment to the paragraph.

        The new segment would be merged with the last segment
        if neither of them has link attached.
        """
        if segment.parent:
            raise ValueError(
                "Should not append a text segment that already has a parent")
        if self._segments and not self._segments[-1].link(
        ) and not segment.link():
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
        return {
            "type": "text_paragraph",
            "segments": [seg.to_dict() for seg in self._segments]
        }