import pytest
from blocks_to_chunks import block_to_child_text, blocks_to_chunks, blocks_to_parents


def test_table_merges_caption():
    """表格块：标题 + 内容拼接成可嵌入文本"""
    block = {
        "type": "table",
        "caption": "表1 法兰尺寸",
        "text": ["行1", "行2"],
    }
    assert block_to_child_text(block) == "表1 法兰尺寸:行1\n行2"


def test_table_without_caption():
    """表格无标题时，只拼内容"""
    block = {"type": "table", "caption": "", "text": ["a", "b"]}
    assert block_to_child_text(block) == "a\nb"


def test_text_block_keeps_text():
    """普通文本块原样返回"""
    block = {"type": "text", "text": "普通文本"}
    assert block_to_child_text(block) == "普通文本"


def test_parent_is_one_per_page():
    """每个 page 只对应一个父块，按页合并"""
    blocks = [
        {"page": 1, "type": "text", "text": "a"},
        {"page": 1, "type": "text", "text": "b"},
        {"page": 2, "type": "text", "text": "c"},
    ]
    parents = blocks_to_parents(blocks)
    pages = [p["page"] for p in parents]
    assert pages == [1, 2]
    assert len(parents) == 2


def test_children_match_blocks():
    """子块数量 = block 数量，字段正确"""
    blocks = [
        {"page": 1, "type": "text", "text": "x"},
        {"page": 2, "type": "text", "text": "y"},
    ]
    children = blocks_to_chunks(blocks)
    assert len(children) == 2
    assert children[0]["page"] == 1
    assert children[1]["text"] == "y"
    