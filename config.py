import os
from typing import Optional

# 环境变量配置
HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
HF_HUB_OFFLINE = os.environ.get("HF_HUB_OFFLINE", "0") == "1"

# 模型配置
RERANKER_MODEL = "BAAI/bge-reranker-base"
EMBEDDING_MODEL = "BAAI/bge-m3"

# 路径配置
DB_PATH = "./chroma_db"
PARENT_JSON = "parent_chunks.json"
CHILD_JSON = "child_chunks.json"

# 检索配置
RETRIEVAL_TOP_K = 20
RERANK_TOP_N = 5
FINAL_TOP_K = 3

# LLM 配置
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com/v1"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2048

def get_api_key() -> Optional[str]:
    """从环境变量获取 DeepSeek API Key"""
    return os.environ.get("DEEPSEEK_API_KEY")