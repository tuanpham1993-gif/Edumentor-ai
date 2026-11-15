
from app.services.rag_service import retrieve_knowledge


test_queries = [
    "What score is required to pass a review quiz?",
    "How many questions must I answer correctly to complete a course?",
    "What is the minimum passing score for the course review quiz?",
    "Tôi cần đạt bao nhiêu điểm để hoàn thành bài kiểm tra khóa học?",
    "Cần trả lời đúng bao nhiêu câu để vượt qua bài kiểm tra?",
]


for query in test_queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = retrieve_knowledge(query, top_k=10)

    for rank, item in enumerate(results, start=1):
        metadata = item.get("metadata", {})

        print(f"\nRank: {rank}")
        print("Score:", item.get("score"))
        print("Section:", metadata.get("section_title"))
        print("FAQ Question:", metadata.get("faq_question_number"))
        print("Content:", item.get("content"))
