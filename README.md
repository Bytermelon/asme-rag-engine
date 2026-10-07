# Advanced RAG Engine —— ASME B16.5 法兰标准问答

基于 **MinerU 文档解析 + ChromaDB 向量检索 + 重排序 + 父块召回** 的 RAG 问答系统，
针对 ASME B16.5-2025《管道法兰与法兰管件》标准做中文问答。

## 流程

PDF（ASME B16.5）
 → [mineru parse] 提取 Markdown + 页码标记
 → [mineru_parser.py] 解析为 block（文本 / 表格 / 标题…）
 → [blocks_to_chunks.py] 切子块 + 父块（父块保留整页上下文）
 → [vector_storage.py] 子块向量化入库 ChromaDB
 → [rag_pipeline.py] 检索 → 重排序 → 父块召回 → 生成
 → [app.py] Flask API

解析步骤需先 pip install "mineru[all]"

## 技术栈

- 文档解析：MinerU 4.x（`mineru parse`）
- 向量库：ChromaDB
- 嵌入模型：`BAAI/bge-m3`
- 重排序模型：`BAAI/bge-reranker-base`
- 生成：DeepSeek Chat API
- 服务框架：Flask

## 安装

```bash pip install -r requirements.txt```

数据准备

▎ ⚠️ 本项目不包含 PDF 原文、解析全文及向量索引（版权原因），需自行准备。

1. MinerU 解析（务必加 --pages all，否则只解析前 10 页）：

mineru parse <pdf路径> --pages all --output <输出目录>
2. 跑分块 + 建库脚本，生成本地 JSON 和 ChromaDB 索引：

python blocks_to_chunks.py
3. 启动服务：

python app.py

API

| 方法 | 路径      | 说明                        |
| ---- | --------- | --------------------------- |
| GET  | `/health` | 健康检查                    |
| POST | `/query`  | 问答，body：`{"query": "..."}` |

/query 返回：

{
  "query": "Class 150 法兰在多少温度以上可能泄漏？",
  "answer": "……",
  "citations": ["31", "49"]
}

配置

在 .env 中配置 API key（不要硬编码、不要提交）：

DEEPSEEK_API_KEY=sk-xxx
HF_ENDPOINT=https://hf-mirror.com

版权声明

ASME B16.5 为 ASME 版权标准。本仓库仅包含代码，不包含 PDF 原文、解析全文及向量索引；
数据需使用者自行准备，仅用于个人学习研究。

---

## 架构演进 / Roadmap

当前版本是**单标准（B16.5）文本问答 RAG**。设计上已把「处理哪本标准」与「怎么处理」解耦，
可平滑扩展到多标准与结构化查询。

### 现状（v1）
- [x] MinerU 解析 Markdown → block 结构化（文本 / 表格 / 标题）
- [x] 子块切分 + 父块召回（保留整页上下文）
- [x] ChromaDB 向量检索 + bge-reranker 重排序
- [x] Flask API：`/health`、`/query`（返回 answer + citations）

### 规划（v2 · 多标准扩展）
- [ ] 数据按 `data/{standard}/` 命名空间隔离
- [ ] 通用 ingest 脚本：`python ingest.py --standard xxx --pdf xxx.pdf`
- [ ] `config.py` 增加 `STANDARD_NAME` 参数，代码中去掉 B16.5 字面量

### 规划（v3 · 结构化查询 + Agent）
- [ ] 表格数据确定性查询（NPS / Class / 材料 → 精确尺寸与额定值）
- [ ] 每本标准一个 schema 注册表
- [ ] 查询路由层（Router）：概念问答走 RAG，查表走结构化 lookup
- [ ] 将 RAG 与查表封装为 Agent 可调用的工具