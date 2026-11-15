
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import settings
from app.core.embedding_model_tutor import EMBEDDING_DIMENSION


# Qdrant Configuration — đọc từ settings (.env: QDRANT_URL, mặc định http://localhost:6335).
# Tuấn 13/11: trước ghi cứng localhost:6335 → trong Docker backend không tới được Qdrant (docker-compose
# truyền QDRANT_URL=http://qdrant:6333). Chạy dev trên máy không đổi gì.
QQDRANT_URL = settings.QDRANT_URL

COLLECTION_NAME = "edumentor_tutor_knowledge"

qdrant_client = QdrantClient(
    url=QQDRANT_URL
)


def create_collection():
    """
    Tạo collection nếu chưa tồn tại.
    Vector dimension phải khớp với Embedding Model.
    """

    if qdrant_client.collection_exists(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE,
        ),
    )

    print(f"Collection '{COLLECTION_NAME}' created successfully.")


def get_qdrant_vector_store():
    """
    Khởi tạo Qdrant Vector Store cho LlamaIndex.
    """

    return QdrantVectorStore(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
    )
