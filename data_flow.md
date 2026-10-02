# RAG 数据流地图

## 输入
user_query: str

## 数据流

1. app.py `/query`
   - 输入: HTTP POST JSON
   - 输出: HTTP JSON

2. rag_pipeline.query(user_query, stream=False)
   - 输入: str
   - 输出: Dict[str, Any]

3. vector_storage.search_parent_chunks(query, ...)
   - 输入: str
   - 输出: List[RetrievedChunk]

4. reranker.rerank(query, candidates, top_n=5)
   - 输入: str + List[RetrievedChunk]
   - 输出: List[RerankerResult]

5. prompt_builder.build(query, chunks)
   - 输入: str + List[RerankerResult]
   - 输出: str

6. rag_generator.generate(prompt, stream=False)
   - 输入: str
   - 输出: str

## 输出
{answer: str, citations: List[str], metadata: Dict}


## 架构反思

### 当前问题
- VectorStorage 职责过重（模型加载 + 向量化 + 存储 + 检索）
- Pipeline 直接依赖具体类，不是接口

### 理想架构
- 分层：应用层 → 服务层 → 领域层 → 基础设施层
- 单一职责：每个类只做一件事
- 依赖注入：从外部传入依赖，便于测试和替换

## 架构改进计划

### 阶段1: 拆分 VectorStorage
- `EmbeddingModel` — 加载 text2vec-base-chinese，提供 encode() 接口
- `VectorDB` — 封装 ChromaDB，提供 add/query 接口  
- `DocumentStore` — 加载 parent_chunks.json，提供 lookup 接口
- `VectorSearch` — 组合上面三个，提供 search() 接口

### 阶段2: 接口抽象
- 定义 `SearchEngine` 接口（抽象基类）
- `VectorSearch` 实现 `SearchEngine`
- `RAGPipeline` 依赖 `SearchEngine`，不是具体类

### 阶段3: 依赖注入
- 模型在外部加载，通过构造函数传入
- 支持 mock 替换，便于单元测试