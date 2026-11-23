
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings
from app.services.qdrant_service import (
    COURSE_COLLECTION_NAME,
    SKILL_COLLECTION_NAME,
    EMBEDDING_DIMENSION,
)


# ==========================================
# 1. QDRANT CLIENT
# ==========================================

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL
)


# ==========================================
# 2. CREATE COLLECTION
# ==========================================

def create_collection(collection_name: str) -> bool:
    """
    Create collection if it does not exist.
    """

    if qdrant_client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' already exists.")
        return False

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE,
        ),
    )

    print(f"Collection '{collection_name}' created successfully.")

    return True


# ==========================================
# 3. INITIALIZE COLLECTIONS
# ==========================================

def initialize_collections():
    """
    Initialize Course and Skill collections.
    """

    create_collection(COURSE_COLLECTION_NAME)
    create_collection(SKILL_COLLECTION_NAME)
