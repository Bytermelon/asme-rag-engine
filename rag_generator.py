import logging
from typing import Generator
from openai import OpenAI
from config import LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, get_api_key


class RAGGenerator:
    """RAG 系统的 LLM 生成器，调用 DeepSeek API"""
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        api_key = get_api_key()
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY 未设置")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=LLM_BASE_URL
        )
        logging.info("RAGGenerator 初始化完成")
    
    def generate(self, prompt: str, stream: bool = False, system_prompt: str = "你是一位专业的文档问答助手") -> str:
        """非流式生成回答
        
        Args:
            prompt: 完整的 Prompt 字符串
            stream: 是否流式输出（默认否）
        
        Returns:
            LLM 生成的回答字符串
        """
        if stream:
            # 流式模式：通过 generate_stream 累积完整回答
            full_answer = ""
            for chunk in self.generate_stream(prompt):
                full_answer += chunk
            return full_answer
        
        # 非流式模式
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"LLM 调用失败: {e}")
            raise RuntimeError(f"LLM 调用失败: {e}")
    
    def generate_stream(self, prompt: str, system_prompt: str = "你是一位专业的文档问答助手") -> Generator[str, None, None]:
        """流式生成回答
        
        Args:
            prompt: 完整的 Prompt 字符串
        
        Yields:
            逐块生成的文本片段
        """
        try:
            stream = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                stream=True
            )
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        
        except Exception as e:
            logging.error(f"LLM 流式调用失败: {e}")
            raise RuntimeError(f"LLM 流式调用失败: {e}")