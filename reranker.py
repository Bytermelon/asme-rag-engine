from config import RERANKER_MODEL

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class RetrievedChunk(BaseModel):
    """从向量数据库检索到的文档块，作为 Reranker 的输入"""
    
    chunk_id: str = Field(..., description="块的唯一标识")
    content: str = Field(..., description="块的文本内容")
    score: float = Field(0.0, description="Bi-Encoder 检索分数")
    page_num: Optional[int] = Field(None, description="所在页码")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")

class RerankerResult(BaseModel):
    """Reranker 的输出结果"""
    
    chunk: RetrievedChunk = Field(..., description="原始文档块")
    rerank_score: float = Field(..., description="Cross-Encoder 重排序分数")
    rank: int = Field(..., description="重排序后的排名（1 开始）")

class Reranker:
    def __init__(
        self,
        model_name: str = RERANKER_MODEL,
        use_fp16: bool = True,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        logging.info(f"Reranker 初始化，模型: {model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()
            self.model.to(self.device)
            logging.info("模型加载成功")
        except Exception as e:
            logging.error(f"模型加载失败: {e}")
            raise RuntimeError(f"模型加载失败: {e}")

    def rerank(self, query, candidates, top_n):

        if self.model is None or self.tokenizer is None:
            raise RuntimeError("模型未加载，请检查模型路径")

        # Step 1: 输入校验（已有）
        if not candidates:
            logging.warning("候选列表为空，返回空结果")
            return []
        
        logging.info(f"收到 {len(candidates)} 个候选文档，返回 Top-{top_n}")
        
        # Step 2: 构建 pairs（已有）
        pairs = [[query, c.content] for c in candidates]
        
        # Step 3: 调用模型计算分数（新增）
        import torch
        
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # print(f"logits 形状: {outputs.logits.shape}")  # 调试用
        
        # 单输出模型，直接用 logits
        scores = outputs.logits.squeeze()
        if scores.dim() == 0:  # 如果是标量（0维）
            scores = [scores.item()]  # 包装成列表
        else:
            scores = scores.cpu().numpy().tolist()
        
        # print(f"分数: {scores}")  # 调试用，确认分数正确
        
        # Step 4: 排序
        scored_candidates = sorted(
            zip(candidates, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Step 5: 构建结果
        results = []
        for rank, (chunk, score) in enumerate(scored_candidates[:top_n], start=1):
            results.append(RerankerResult(
                chunk=chunk,
                rerank_score=score,
                rank=rank
            ))
        return results

if __name__ == "__main__":
    # 测试1: 正常重排序
    reranker = Reranker()
    candidates = [
        RetrievedChunk(chunk_id="1", content="RAG系统通过检索增强生成。", score=0.8),
        RetrievedChunk(chunk_id="2", content="深度学习是机器学习分支。", score=0.7),
        RetrievedChunk(chunk_id="3", content="RAG中的重排序提升精度。", score=0.6),
    ]
    results = reranker.rerank("RAG系统怎么提升效果？", candidates, top_n=3)
    print(f"返回 {len(results)} 个结果")
    for r in results:
        print(f"Rank {r.rank}: score={r.rerank_score:.3f} | {r.chunk.content[:30]}...")

    # 验证: 最高分应该在第一个
    assert results[0].rank == 1, "第一个结果应该是Rank 1"

    # 测试2: 空候选列表
    empty_results = reranker.rerank("测试", [], top_n=3)
    assert len(empty_results) == 0, "空列表应该返回空结果"
    print("所有测试通过!")