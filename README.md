# 工业规范问答 RAG 系统

基于父子块双轨召回 + BGE-Reranker 精排 + DeepSeek LLM 生成的工业规范问答系统。

## 功能特性

- **父子块双轨召回**：子块 256 token 用于向量检索，父块 1024 token 恢复完整上下文
- **BGE-Reranker 精排**：Bi-Encoder 召回 Top-20，Cross-Encoder 精排 Top-5
- **幻觉防护**：System Prompt 约束 + 引用标注 + 不确定性表达
- **模块化设计**：VectorStorage、Reranker、PromptBuilder、RAGGenerator 解耦

## 技术架构
Query → VectorStorage (检索) → Reranker (精排) → PromptBuilder (拼接) → RAGGenerator (生成) → Answer
 
## 安装
```bash
git clone https://github.com/Bytermelon/rag_1.git
cd rag_1
pip install -r requirements.txt
export DEEPSEEK_API_KEY="your-api-key"
export HF_ENDPOINT="https://hf-mirror.com"
python app.py
```

## 使用示例
bash
### 健康检查
curl http://localhost:5000/health

### 问答请求
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是压力容器设计规范？"}'

## API 文档

| 端点        | 方法   | 参数                                       | 响应                                                       |
| :-------- | :--- | :--------------------------------------- | :------------------------------------------------------- |
| `/health` | GET  | 无                                        | `{"status": "ok"}`                                       |
| `/query`  | POST | `query` (str), `stream` (bool, 默认 false) | `{"answer": ..., "citations": [...], "metadata": {...}}` |

## 项目结构
plain
├── app.py              # Flask API 入口
├── rag_pipeline.py     # RAG Pipeline (串联所有模块)
├── vector_storage.py   # 向量存储 (ChromaDB + text2vec)
├── reranker.py         # 重排序 (BGE-Reranker)
├── prompt_builder.py   # Prompt 拼接
├── rag_generator.py    # LLM 生成 (DeepSeek API)
├── config.py           # 配置管理
└── requirements.txt    # 依赖列表

## 性能指标
表格
| 环节          | 耗时      | 占比  |
| :---------- | :------ | :-- |
| 向量检索        | ~200ms  | 7%  |
| Reranker 精排 | ~800ms  | 27% |
| LLM 生成      | ~2000ms | 66% |
| 其他          | ~100ms  | 3%  |

## 后续计划
[ ] 升级 BGE-M3 多语言模型，支持英文工业标准
[ ] 引入 Layout-Aware PDF 解析，保留表格结构
[ ] 接入 LangGraph，实现 Agentic RAG