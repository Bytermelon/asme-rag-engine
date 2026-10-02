import requests

def test_health():
    """测试健康检查端点"""
    response = requests.get("http://localhost:5000/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("✅ /health 测试通过")

def test_query():
    """测试查询端点"""
    response = requests.post(
        "http://localhost:5000/query",
        json={"query": "什么是压力容器设计规范？"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    print("✅ /query 测试通过")
    print(f"回答: {data['answer'][:100]}...")

def test_empty_query():
    """测试空查询"""
    response = requests.post(
        "http://localhost:5000/query",
        json={"query": ""}
    )
    assert response.status_code == 400
    print("✅ 空查询测试通过")

if __name__ == "__main__":
    test_health()
    test_query()
    test_empty_query()
    print("\n🎉 所有测试通过！")