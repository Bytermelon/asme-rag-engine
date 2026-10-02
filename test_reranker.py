import pytest
from reranker import Reranker, RetrievedChunk, RerankerResult


@pytest.fixture
def sample_candidates():
    """共享测试数据：3个候选文档"""
    return [
        RetrievedChunk(chunk_id="1", content="RAG系统通过检索增强生成。", score=0.8),
        RetrievedChunk(chunk_id="2", content="深度学习是机器学习分支。", score=0.7),
        RetrievedChunk(chunk_id="3", content="RAG中的重排序提升精度。", score=0.6),
    ]


@pytest.fixture
def reranker():
    """共享 Reranker 实例"""
    return Reranker()


def test_rerank_normal(reranker, sample_candidates):
    """测试正常重排序"""
    results = reranker.rerank("RAG系统怎么提升效果？", sample_candidates, top_n=3)
    
    assert len(results) == 3
    assert results[0].rank == 1
    assert results[0].rerank_score >= results[1].rerank_score  # 降序


def test_rerank_empty(reranker):
    """测试空候选列表"""
    results = reranker.rerank("测试", [], top_n=3)
    assert len(results) == 0


def test_rerank_top_n_larger(reranker, sample_candidates):
    """测试 top_n 大于候选数量"""
    results = reranker.rerank("测试", sample_candidates, top_n=10)
    assert len(results) == 3  # 只有3个候选，返回3个


def test_rerank_result_fields(reranker, sample_candidates):
    """测试返回结果的字段类型"""
    results = reranker.rerank("测试", sample_candidates, top_n=1)
    
    assert results[0].rank == 1
    assert isinstance(results[0].rerank_score, float)
    assert isinstance(results[0].chunk, RetrievedChunk)

def test_rerank_model_not_loaded():
    """测试模型未加载时抛出异常"""
    r = Reranker()
    # r.model = None  # 模拟加载失败
    
    with pytest.raises(RuntimeError):
        r.rerank(
            "测试",
            [RetrievedChunk(chunk_id="1", content="test", score=0.5)],
            top_n=1
        )