from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


# ==========================================
# 1. CONFIGURATION
# ==========================================

EMBEDDING_DIMENSION = 384

COURSE_COLLECTION_NAME = "edumentor_courses"
SKILL_COLLECTION_NAME = "edumentor_skills"
TUTOR_SKILL_COLLECTION_NAME = "tutor_skills"


# ==========================================
# 2. POINT ID GENERATORS
# ==========================================

def generate_skill_point_id(skill_id: int) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            f"edumentor-skill:{skill_id}"
        )
    )


def generate_course_point_id(course_id: int) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            f"edumentor-course:{course_id}"
        )
    )


# ==========================================
# 3. SHARED QDRANT CLIENT
# ==========================================

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL
)


# ==========================================
# 4. BASE QDRANT SERVICE
# ==========================================

class BaseQdrantService:

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.COLLECTION_NAME = collection_name
        self.VECTOR_SIZE = EMBEDDING_DIMENSION
        self.client = qdrant_client

    def create_collection(self) -> bool:

        if self.client.collection_exists(self.collection_name):
            info = self.client.get_collection(self.collection_name)

            vector_config = info.config.params.vectors

            if (
                vector_config.size != EMBEDDING_DIMENSION
                or vector_config.distance != Distance.COSINE
            ):
                raise ValueError(
                    f"Invalid configuration for {self.collection_name}"
                )

            return False

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )

        return True

    def search(self, embedding: list[float], limit: int = 5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            with_payload=True,
        )

        return results.points

    def delete_point(self, point_id: str):

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=[point_id]
            ),
            wait=True,
        )


# ==========================================
# 5. SKILL SERVICE
# ==========================================

class QdrantSkillService(BaseQdrantService):

    COLLECTION_NAME = SKILL_COLLECTION_NAME
    VECTOR_SIZE = EMBEDDING_DIMENSION

    def __init__(self):
        super().__init__(SKILL_COLLECTION_NAME)
        self.client = qdrant_client
        self.COLLECTION_NAME = SKILL_COLLECTION_NAME
        self.VECTOR_SIZE = EMBEDDING_DIMENSION

    def search_skill(self, embedding: list[float], limit: int = 5):
        return self.search(embedding, limit)

    def index_skill(
        self,
        skills: list[dict],
        embeddings: list[list[float]] | None = None,
        batch_size: int = 100,
        embedding: list[list[float]] | None = None,
    ):
        """Đánh chỉ mục danh sách kỹ năng vào Qdrant (dành cho database.py lúc startup)."""
        vectors = embeddings if embeddings is not None else embedding
        if vectors is None or len(skills) != len(vectors):
            raise ValueError("Number of skills and embeddings must match.")

        points = []
        for each_skill, vec in zip(skills, vectors):
            skill_id = each_skill.get("skill_id")
            skill_name = each_skill.get("skill_name") or each_skill.get("skill") or ""
            points.append(
                PointStruct(
                    id=generate_skill_point_id(skill_id),
                    vector=vec,
                    payload={
                        "skill_id": skill_id,
                        "skill": skill_name,
                    },
                )
            )

        total_points = len(points)
        for start in range(0, total_points, batch_size):
            batch = points[start : start + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True,
            )
        print(f"Successfully indexed {total_points} skills into {self.collection_name}.")

    def update_skill(
        self,
        skill_id: int,
        skill_name: str | None = None,
        embedding: list[float] | None = None,
        skill: str | None = None,
    ):
        """Cập nhật kỹ năng, hỗ trợ cả skill_name và skill để tương thích ngược với code của Hòa."""
        name = skill_name or skill or ""
        point = PointStruct(
            id=generate_skill_point_id(skill_id),
            vector=embedding,
            payload={
                "skill_id": skill_id,
                "skill": name,
            },
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
            wait=True,
        )

    def delete_skill(self, skill_id: int):

        self.delete_point(
            generate_skill_point_id(skill_id)
        )


class QdrantTutorSkillService(BaseQdrantService):
    """
    Dedicated Skill Service for AI Tutor Chatbot using multilingual embedding model (L12-v2).
    Operates on collection 'tutor_skills' to completely isolate from Hoa's 'edumentor_skills'.
    """

    COLLECTION_NAME = TUTOR_SKILL_COLLECTION_NAME
    VECTOR_SIZE = EMBEDDING_DIMENSION

    def __init__(self):
        super().__init__(TUTOR_SKILL_COLLECTION_NAME)
        self.client = qdrant_client
        self.COLLECTION_NAME = TUTOR_SKILL_COLLECTION_NAME
        self.VECTOR_SIZE = EMBEDDING_DIMENSION

    def search_skill(self, embedding: list[float], limit: int = 5):
        return self.search(embedding, limit)

    def update_skill(
        self,
        skill_id: int,
        skill_name: str | None = None,
        embedding: list[float] | None = None,
        skill: str | None = None,
    ):
        name = skill_name or skill or ""
        point = PointStruct(
            id=generate_skill_point_id(skill_id),
            vector=embedding,
            payload={
                "skill_id": skill_id,
                "skill": name,
            },
        )
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
            wait=True,
        )

    def delete_skill(self, skill_id: int):
        self.delete_point(
            generate_skill_point_id(skill_id)
        )


# ==========================================
# 6. COURSE SERVICE
# ==========================================

class QdrantCourseService(BaseQdrantService):

    COLLECTION_NAME = COURSE_COLLECTION_NAME
    VECTOR_SIZE = EMBEDDING_DIMENSION

    def __init__(self):
        super().__init__(COURSE_COLLECTION_NAME)
        self.client = qdrant_client
        self.COLLECTION_NAME = COURSE_COLLECTION_NAME
        self.VECTOR_SIZE = EMBEDDING_DIMENSION

    def search_courses(self, embedding: list[float], limit: int = 5):
        return self.search(embedding, limit)

    def update_course(
        self,
        course_id: int,
        title: str,
        embedding: list[float],
        payload: dict | None = None,
    ):

        point_payload = {
            "course_id": course_id,
            "title": title,
        }

        if payload:
            point_payload.update(payload)

        point = PointStruct(
            id=generate_course_point_id(course_id),
            vector=embedding,
            payload=point_payload,
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
            wait=True,
        )

    def delete_course(self, course_id: int):

        self.delete_point(
            generate_course_point_id(course_id)
        )


# ==========================================
# 7. SERVICE INSTANCES
# ==========================================

qdrant_skill_service = QdrantSkillService()

qdrant_tutor_skill_service = QdrantTutorSkillService()

qdrant_course_service = QdrantCourseService()
