from typing import List

class PromptBuilder:
    """Prompt 构建器，将检索结果拼接成 LLM 输入"""
    
    SYSTEM_PROMPT = """你是一位专业的文档问答助手。

核心规则：
1. 只基于提供的参考文档回答问题
2. 不确定时明确说"无法找到相关信息"
3. 每个事实必须标注来源 [Source:第X页]
4. 禁止编造文档中没有的信息

回答结构：
- 直接答案（1-2句话）
- 详细解释（基于文档展开）
- 引用来源列表

约束：
- 简洁准确
- 优先给出直接答案"""
    
    def build(self, query: str, chunks: List[dict]) -> str:
        """构建 Prompt
        
        Args:
            query: 用户查询字符串
            chunks: 父块内容字典列表
        
        Returns:
            拼接好的 Prompt 字符串
        """
        # 构建文档部分
        docs_section = ""
        for r in chunks:
            chunk = r.get('content')
            page = r.get('page')
            docs_section += f"第{page}页\n{chunk}\n\n"
        
        # 拼接完整 Prompt
        prompt = f"""[用户问题]
{query}

[参考文档]
{docs_section}[要求]
请基于上述参考文档回答问题。如果文档中没有相关信息，请明确说明。
每个事实必须标注来源 [Source: 第X页]。"""
        
        return prompt


if __name__ == "__main__":
    # 端到端测试：完整的 RAG 流程
    
    from vector_storage import VectorStorage
    from reranker import Reranker
    from prompt_builder import PromptBuilder
    from rag_generator import RAGGenerator
    
    print("=== 步骤1: 向量检索 ===")
    storage = VectorStorage()
    # 如果数据库为空，先存入
    storage.store_child_chunks()
    
    query = "法兰螺栓受力熔断"
    candidates = storage.search_parent_chunks(query, use_reranker=False, retrieve_k=10)
    print(f"检索到 {len(candidates)} 个候选父块")
    
    print("\n=== 步骤2: Reranker 精排 ===")
    reranker = Reranker()
    
    # 把父块转成 Reranker 需要的格式
    from reranker import RetrievedChunk
    rerank_candidates = []
    for i, parent in enumerate(candidates):
        content = parent.get("full_content") or parent.get("text", "")
        rerank_candidates.append(
            RetrievedChunk(
                chunk_id=f"parent_{i}",
                content=content[:500],  # 取前500字
                score=0.0,
                page_num=parent.get("page") or parent.get("page_num")
            )
        )
    
    ranked = reranker.rerank(query, rerank_candidates, top_n=3)
    print(f"精排后取 top-3")
    
    print("\n=== 步骤3: 构建 Prompt ===")
    builder = PromptBuilder()
    prompt = builder.build(query, ranked)
    print(f"Prompt 长度: {len(prompt)} 字符")
    
    print("\n=== 步骤4: LLM 生成 ===")
    generator = RAGGenerator()
    answer = generator.generate(
    prompt, 
    system_prompt=builder.SYSTEM_PROMPT,  # ← 传入完整的 System Prompt
    stream=False
    )
    print(f"\n最终回答:\n{answer}")