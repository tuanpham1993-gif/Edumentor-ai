
from app.core.qdrant_tutor import (
    qdrant_client,
    create_collection,
    get_qdrant_vector_store,
    COLLECTION_NAME,
)

from app.core.embedding_model_tutor import EMBEDDING_DIMENSION


def test_qdrant_connection():

    # 1. Kiểm tra kết nối
    health = qdrant_client.get_collections()

    print("\nQdrant connection: SUCCESS")

    # 2. Tạo collection nếu chưa có
    create_collection()

    # 3. Kiểm tra collection
    collection = qdrant_client.get_collection(
        collection_name=COLLECTION_NAME
    )

    assert collection.config.params.vectors.size == EMBEDDING_DIMENSION

    # 4. Kiểm tra LlamaIndex Vector Store
    vector_store = get_qdrant_vector_store()

    assert vector_store is not None

    print("Collection:", COLLECTION_NAME)
    print("Vector dimension:", collection.config.params.vectors.size)
    print("Vector store:", type(vector_store).__name__)

    print("\nQDRANT CONNECTION TEST PASSED!")


if __name__ == "__main__":
    test_qdrant_connection()
