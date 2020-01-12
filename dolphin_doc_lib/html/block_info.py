from typing import List, cast

from dolphin_doc_lib.base.doc import BlockType
from dolphin_doc_lib.base.text import TextParagraph


def _merge_block(block1: BlockType, block2: BlockType) -> BlockType:
    if type(block1) is TextParagraph and type(block2) is TextParagraph:
        block = cast(TextParagraph, block1)
        for segment in cast(TextParagraph, block2).segments():
            block = block.append_text_segment(segment)
        return block
    raise ValueError(
        "Not able to merge block that is not TextParagraph: {}, {}".format(
            type(block1), type(block2)))


class BlocksInfo():
    "HTML element in dolphin Block form, it is intermediate result during converting"

    def __init__(self, blocks: List[BlockType] = []):
        self.blocks: List[BlockType] = blocks
        self.first_block_mergeable: bool = True
        self.last_block_mergeable: bool = True

    def attach_link(self, link: str) -> "BlocksInfo":
        if len(self.blocks) != 1:
            raise ValueError("can not attach link: block number is not 1")
        if type(self.blocks[0]) is not TextParagraph:
            raise ValueError("can not attach link to non TextParagraph block")
        par = cast(TextParagraph, self.blocks[0])
        segments = par.segments()
        if len(segments) != 1:
            raise ValueError("can not attach link: segment number is not 1")
        segments[0].attach_link(link)
        return self

    def make_non_mergeable(self) -> "BlocksInfo":
        self.first_block_mergeable = False
        self.last_block_mergeable = False
        return self

    def merge_blocks_info(self, other: "BlocksInfo") -> "BlocksInfo":
        if not other.blocks:
            if not other.first_block_mergeable:
                self.last_block_mergeable = False
            return self

        if not self.blocks:
            self.blocks = other.blocks
            self.first_block_mergeable = self.first_block_mergeable and other.first_block_mergeable
            self.last_block_mergeable = other.last_block_mergeable
            return self

        blocks: List[BlockType] = []
        if self.last_block_mergeable and other.first_block_mergeable:
            merged_block = _merge_block(self.blocks[-1], other.blocks[0])
            blocks = self.blocks[:-1] + [merged_block] + other.blocks[1:]
        else:
            blocks = self.blocks + other.blocks

        self.blocks = blocks
        self.last_block_mergeable = other.last_block_mergeable
        return self


def merge_blocks_info_list(infos: List[BlocksInfo]) -> BlocksInfo:
    blocks_info = BlocksInfo()
    for info in infos:
        blocks_info.merge_blocks_info(info)
    return blocks_info
