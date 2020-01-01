"Base Doc implementation"
import json
from typing import Dict, List, Union

from dolphin_doc_lib.base.table import Table
from dolphin_doc_lib.base.text import TextParagraph

BlockType = Union[TextParagraph, Table]


class Doc():
    "General Doc"

    def __init__(self):
        self._blocks: List[BlockType] = []

    def append_block(self, block: BlockType) -> "Doc":
        "Append a block"
        if block.parent:
            raise ValueError(
                "Should not append a block that already has a parent")
        block.parent = self
        self._blocks.append(block)
        return self

    def append_blocks(self, blocks: List[BlockType]) -> "Doc":
        for block in blocks:
            self.append_block(block)
        return self

    def blocks(self) -> List[BlockType]:
        "Return all the stored blocks"
        return self._blocks

    def to_dict(self) -> Dict:
        "dict version for json encoding"
        return {
            "type": "doc",
            "blocks": [block.to_dict() for block in self._blocks]
        }

    def print(self):
        "print this doc"
        print(
            json.dumps(self.to_dict(), indent=4,
                       ensure_ascii=False).encode('utf8').decode())
