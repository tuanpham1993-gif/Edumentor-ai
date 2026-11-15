from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PointIdsList
from uuid import uuid5, NAMESPACE_URL
from app.core.config import settings

def generate_point_id(skill_id: int) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            f"edumentor-skill:{skill_id}"
        )
    )

class QdrantSkillService:
    def __init__(self, qdrant_url, collection_name, vector_size):
        self.client = QdrantClient(url=qdrant_url)
        self.COLLECTION_NAME = collection_name
        self.VECTOR_SIZE = vector_size

    def create_collection(self):
        collections = self.client.get_collections()
        existing_name = [each.name for each in collections.collections]
        if self.COLLECTION_NAME in existing_name: return False
        self.client.create_collection(collection_name = self.COLLECTION_NAME, 
                                      vectors_config=VectorParams(size=self.VECTOR_SIZE, 
                                                                  distance=Distance.COSINE))
        print(f"Created collection: {self.COLLECTION_NAME}")
        return True

    def index_skill(self, skills, embeddings, batch_size=100):

        if len(skills) != len(embeddings):
            raise ValueError(
                "Number of skills and embeddings must match."
            )

        points = []

        for each_skill, embedding in zip(skills, embeddings):
            skill_id = each_skill["skill_id"]

            points.append(
                PointStruct(
                    id=generate_point_id(skill_id),
                    vector=embedding,
                    payload={
                        "skill_id": skill_id,
                        "skill": each_skill["skill_name"]
                    }
                )
            )

        # Upload points in smaller batches
        total_points = len(points)

        for start in range(0, total_points, batch_size):
            batch = points[start:start + batch_size]

            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch,
                wait=True
            )

            print(
                f"Uploaded {min(start + len(batch), total_points)}"
                f"/{total_points} skills."
            )

        print(f"Successfully indexed {total_points} skills.")

    def search_skill(self, embedding, limit = 5):
        results = self.client.query_points(
            collection_name= self.COLLECTION_NAME,
            query=embedding,
            limit=limit,
            with_payload=True
        )
        return results.points

    def update_skill(self, skill_id: int, skill_name: str, embedding):
        point_id = generate_point_id(skill_id)
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "skill_id": str(skill_id),
                "skill": skill_name
            }
        )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
            wait=True
        )

        print(f"Updated Qdrant skill: {skill_id} - {skill_name}")

    def delete_skill(self, skill_id: int):
        point_id = generate_point_id(skill_id)
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=PointIdsList(points=[point_id]),
            wait=True
        )
        print(f"Deleted Qdrant skill: {skill_id}")
    
qdrant_skill_service = QdrantSkillService(qdrant_url=settings.QDRANT_URL, 
                                          collection_name="edumentor_skills",
                                          vector_size=384)