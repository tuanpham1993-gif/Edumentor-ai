
from app.core.embedding_model_tutor import (
    embedding_model_tutor,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
)

def test_embedding_model():
    texts = [
        "How can students save their learning progress?",
        "Làm sao để lưu tiến độ học tập?",
    ]

    vectors = embedding_model_tutor.encode(texts)

    assert vectors.shape == (2, EMBEDDING_DIMENSION)

    print("Model:", EMBEDDING_MODEL_NAME)
    print("Vector shape:", vectors.shape)
    print("English vector:", vectors[0][:5])
    print("Vietnamese vector:", vectors[1][:5])

    print("EMBEDDING TEST PASSED!")


if __name__ == "__main__":
    test_embedding_model()
