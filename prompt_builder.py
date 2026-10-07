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
