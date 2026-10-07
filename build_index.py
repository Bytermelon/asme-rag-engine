"""一键建库：MinerU 输出 → 分块 → 写 JSON → 入库 ChromaDB

用法（在项目根目录运行）:
    python build_index.py <MinerU 输出文件>
    # 自动识别 .md（带页码标记的 markdown）或 .json（middle_json）
"""
import argparse
import json

from mineru_parser import parse_markdown_to_blocks, parse_json_to_blocks
from blocks_to_chunks import blocks_to_chunks, blocks_to_parents, write_chunks_for_rag1
from vector_storage import VectorStorage
from config import CHILD_JSON


def load_blocks(path: str) -> list[dict]:
    """按文件后缀选解析器，把 MinerU 输出读成 block 列表"""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if path.lower().endswith(".json"):
        return parse_json_to_blocks(json.loads(raw))
    return parse_markdown_to_blocks(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="一键建库")
    parser.add_argument("input", help="MinerU 输出文件：.md 或 .json")
    args = parser.parse_args()

    # 1. 解析 → 2. 切块 → 3. 写 JSON
    blocks = load_blocks(args.input)
    children = blocks_to_chunks(blocks)
    parents = blocks_to_parents(blocks)
    write_chunks_for_rag1(children, parents)
    print(f"✅ 分块完成：{len(blocks)} block → {len(children)} 子块 / {len(parents)} 父块")

    # 4. 入库 ChromaDB
    storage = VectorStorage()
    storage.store(storage.load(CHILD_JSON))
    print("✅ 已写入 ChromaDB 索引")


if __name__ == "__main__":
    main()