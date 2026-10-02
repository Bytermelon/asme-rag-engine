import os
from flask import Flask, request, jsonify
from vector_storage import VectorStorage
from rag_pipeline import RAGPipeline
from config import HF_ENDPOINT

# 设置环境变量
os.environ["HF_ENDPOINT"] = HF_ENDPOINT

app = Flask(__name__)

# 初始化 Pipeline（应用启动时只执行一次）
print("⏳ 正在初始化 RAG Pipeline...")
storage = VectorStorage()
pipeline = RAGPipeline(storage)
print("✅ Pipeline 初始化完成！")


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "message": "RAG 服务运行中"})


@app.route('/query', methods=['POST'])
def query():
    """查询端点"""
    # 获取 JSON 数据
    data = request.get_json()
    user_query = data.get('query', '')
    
    # 参数校验
    if not user_query:
        return jsonify({"error": "query 参数不能为空"}), 400
    
    # 调用 Pipeline
    try:
        result = pipeline.query(user_query, stream=False)
        return jsonify({
            "query": user_query,
            "answer": result.get('answer'),
            "citations": result.get('citations', [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)