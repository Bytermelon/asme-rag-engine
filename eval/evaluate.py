"""检索评测：在QA 集上对比「有无重排」的 Hit@k

用法（在项目根目录运行）:
    python eval/evaluate.py eval/qa.json
"""
import argparse
import json
import sys
from pathlib import Path

# 保证能从项目根目录导入 vector_storage / reranker / config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vector_storage import VectorStorage
from reranker import Reranker
from config import RERANK_TOP_N


def hit(golden_pages, top_pages):
    """golden 页是否出现在 top 页列表里"""
    return any(g in top_pages for g in golden_pages)


def main() -> None:
    parser = argparse.ArgumentParser(description="黄金 QA 集检索评测")
    parser.add_argument(
        "golden",
        nargs="?",
        default="eval/qa.json",
        help="黄金 QA json 路径（默认 eval/qa.json）",
    )
    args = parser.parse_args()

    with open(args.golden, encoding="utf-8") as f:
        qa = json.load(f)

    storage = VectorStorage()
    reranker = Reranker()

    ks = [1, 3, 5]
    summary = {k: {"no_rerank": 0, "rerank": 0} for k in ks}

    for item in qa:
        q = item["question"]
        golden = [str(p) for p in item["relevant_pages"]]

        retrieved = storage.search(q)                 # 按相似度排序的 top-K
        no_rerank_pages = [str(c.page_num) for c in retrieved]

        ranked = reranker.rerank(q, retrieved, RERANK_TOP_N)
        rerank_pages = [str(c.chunk.page_num) for c in ranked]

        recalled = hit(golden, no_rerank_pages)       # 正确答案是否在 top-20 里

        print(f"\nQ: {q}")
        print(f"  无重排 top-5: {no_rerank_pages[:5]}")
        print(f"  有重排 top-5: {rerank_pages}")
        print(f"  黄金页: {golden}  {'✅ 召回命中' if recalled else '❌ 召回未命中(top-20 都没有)'}")

        for k in ks:
            if hit(golden, no_rerank_pages[:k]):
                summary[k]["no_rerank"] += 1
            if hit(golden, rerank_pages[:k]):
                summary[k]["rerank"] += 1

    n = len(qa)
    print("\n" + "=" * 56)
    print(f"共 {n} 题")
    print(f"{'k':>4} | {'无重排 Hit@k':>14} | {'有重排 Hit@k':>14} | {'提升':>8}")
    print("-" * 56)
    for k in ks:
        no_ = summary[k]["no_rerank"] / n
        re_ = summary[k]["rerank"] / n
        print(f"{k:>4} | {no_:>13.2%} | {re_:>13.2%} | {re_-no_:>+8.2%}")


if __name__ == "__main__":
    main()