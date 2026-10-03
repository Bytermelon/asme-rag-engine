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
    # test_health()
    # test_query()
    # test_empty_query()
    # print("\n🎉 所有测试通过！")

    import json
d = json.load(open(r"output\ASME B16.5-2025.json", encoding="utf-8"))

for want in ("image", "equation", "code", "index", "chart"):
    # found = False
    # for p in d["pages"]:
    #     for b in p["blocks"]:
    #         if b["type"] == want:
    #             print(f"\n=== {want} (page_idx={p['page_idx']}) 顶层键: {list(b.keys())} ===")
    #             print(json.dumps(b, ensure_ascii=False, indent=2)[:600])
    #             found = True
    #             break
    #     if found:
    #         break

    import json
    d = json.load(open(r"output\ASME B16.5-2025.json", encoding="utf-8"))
    count = 0
    for p in d["pages"]:
        for b in p["blocks"]:
            if b["type"] == "image":
                for c in b.get("content", []):
                    v = c.get("content", "")
                    if v:
                        count += 1
                        print(f"\n非空 image #{count}: page_idx={p['page_idx']}, bbox={b['bbox']}")
                        print(f"  内容类型={type(v).__name__}, 长度={len(v)} 字符")
                        print(f"  开头 120 字符: {repr(v[:120])}")
                        if count >= 3:
                            raise SystemExit