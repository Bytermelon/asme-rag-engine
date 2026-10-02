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
        self.reranker = reranker
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.generator = generator or RAGGenerator()
        logging.info("RAGPipeline 初始化完成")

    def query(self, query:str) -> str:
        # step1:检索
        retrievalchunk = self.vector_storage.search(query)
        
        # step2:重排序
        candidates = self.reranker.rerank(query,retrievalchunk,RERANK_TOP_N)

        # step3:召回父块
        parent_ref_id = []
        for candidate in candidates:
            pid = candidate.chunk.metadata['parent_ref_id']
            parent_ref_id.append(pid)
        chunks = self.vector_storage.get_parent(parent_ref_id)

        # step4:生成回答
        prompt = self.prompt_builder.build(query,chunks)
        answer = self.generator.generate(prompt)

        return answer


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
    answer = [
        ragpipeline.query("Class 150 法兰在多少温度以上可能泄漏？"),
        ragpipeline.query("法兰的压力等级有哪些？"),
        ragpipeline.query("低温下碳钢法兰有什么风险？"),
    ]
    print(answer)