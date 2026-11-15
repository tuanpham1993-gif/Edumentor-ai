
from app.ai.query_router import route_query

test_cases = [
    "Tôi muốn ôn tập Skill Python",
    "Tôi muốn ôn tập khóa học Python",
    "Tìm khóa học Python",
    "Cách lưu tiến độ học trong EduMentor?",
    "Giải thích đoạn code Python này",
    "Tôi muốn tạo lộ trình học Python",
    "Tôi muốn  tới Khóa học Python",
    "Tôi muốn  tới ôn tập Skill Python",
]

for question in test_cases:
    result = route_query(question)

    print("\nCâu hỏi:", question)
    print("Intent:", result["intent"])
    print("Retrieval:", result["retrieval_modes"])
    print("Entity Type:", result["entity_type"])
    print("Entity Name:", result["entity_name"])
    print("Source:", result["source"])
