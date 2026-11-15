
from app.core.embedding_model_tutor import (
    embedding_model_tutor,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
)


def test_llamaindex_embedding():

    texts = [
        "How can students save their learning progress?",
        "Làm sao để lưu tiến độ học tập của sinh viên?",
    ]

    vectors = [
        embedding_model_tutor.get_text_embedding(text)
        for text in texts
    ]

    # Kiểm tra số lượng vector
    assert len(vectors) == 2

    # Kiểm tra dimension
    assert len(vectors[0]) == EMBEDDING_DIMENSION
    assert len(vectors[1]) == EMBEDDING_DIMENSION

    # Kiểm tra vector không rỗng
    assert any(value != 0 for value in vectors[0])
    assert any(value != 0 for value in vectors[1])

    print("\nModel:", EMBEDDING_MODEL_NAME)
    print("English dimension:", len(vectors[0]))
    print("Vietnamese dimension:", len(vectors[1]))

    print("\nLLAMAINDEX EMBEDDING TEST PASSED!")


if __name__ == "__main__":
    test_llamaindex_embedding()
