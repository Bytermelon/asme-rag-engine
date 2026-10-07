import logging
import time
from typing import Optional, Dict, Any, List
from vector_storage import VectorStorage
from reranker import Reranker, RetrievedChunk, RerankerResult
from prompt_builder import PromptBuilder
from rag_generator import RAGGenerator
from config import RERANK_TOP_N

class RAGPipeline:
    """RAG 流水线，串联检索 -> 重排 -> Prompt -> LLM 生成"""

    def __init__(
        self,
        vector_storage: VectorStorage,
        reranker: Optional[Reranker] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        generator: Optional[RAGGenerator] = None
    ):
        """初始化 Pipeline

        Args:
            vector_storage: 向量存储模块（必须）
            reranker: Reranker 模块（可选）
            prompt_builder: Prompt 构建器（可选，默认创建）
            generator: LLM 生成器（可选，默认创建）
        """
        self.vector_storage = vector_storage
        self.reranker = reranker or Reranker()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.generator = generator or RAGGenerator()
        logging.info("RAGPipeline 初始化完成")

    def query(self, query: str, stream: bool = False) -> dict:
        timings = {}

        # step1: 检索
        t0 = time.perf_counter()
        retrievalchunk = self.vector_storage.search(query)
        timings["检索"] = time.perf_counter() - t0

        # step2: 重排序
        t0 = time.perf_counter()
        candidates = self.reranker.rerank(query, retrievalchunk, RERANK_TOP_N)
        timings["重排"] = time.perf_counter() - t0

        # step3: 召回父块
        t0 = time.perf_counter()
        parent_ref_id = []
        for candidate in candidates:
            pid = candidate.chunk.metadata['parent_ref_id']
            if pid not in parent_ref_id:
                parent_ref_id.append(pid)
        chunks = self.vector_storage.get_parent(parent_ref_id)
        timings["召回父块"] = time.perf_counter() - t0

        # step4: 构建 Prompt
        t0 = time.perf_counter()
        prompt = self.prompt_builder.build(query, chunks)
        timings["拼Prompt"] = time.perf_counter() - t0

        # step5: LLM 生成
        t0 = time.perf_counter()
        answer = self.generator.generate(prompt)
        timings["LLM生成"] = time.perf_counter() - t0

        # step6: 返回 dict；citations 是引用页码列表（page_15 → 15）
        citations = [pid.replace('page_', '') for pid in parent_ref_id]
        timings["总耗时"] = sum(timings.values())

        return {"answer": answer, "citations": citations, "timings": timings}


if __name__ == '__main__':
    vectorstorage = VectorStorage()
    reranker = Reranker()
    promptbuild = PromptBuilder()
    generator = RAGGenerator()
    ragpipeline = RAGPipeline(
        vector_storage=vectorstorage,
        reranker=reranker,
        prompt_builder=promptbuild,
        generator=generator
    )
    questions = [
        "Class 150 法兰在多少温度以上可能泄漏？",
        "法兰的压力等级有哪些？",
        "低温下碳钢法兰有什么风险？",
    ]
    for q in questions:
        r = ragpipeline.query(q)
        print("问题:", q)
        print("答案:", r["answer"])
        print("引用页码:", r["citations"])
        t = r["timings"]
        print("耗时: 检索 %.3fs | 重排 %.3fs | 召回 %.4fs | Prompt %.4fs | LLM %.3fs | 总 %.3fs" % (
            t["检索"], t["重排"], t["召回父块"], t["拼Prompt"], t["LLM生成"], t["总耗时"]))
        print("-" * 40)