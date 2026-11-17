from app.services.rag_service import retrieve_knowledge

query = "Cho tôi link vào trang đăng nhập?"

results = retrieve_knowledge(query, top_k=5)

for i, item in enumerate(results, start=1):

    metadata = item["metadata"]

    print(f"\n========== RESULT {i} ==========")
    print("Score:", item["score"])
    print("Section:", metadata.get("section"))
    print("Feature:", metadata.get("feature_title"))
    print("Route:", metadata.get("route"))
    print("Content:")
    print(item["content"])