
from llama_index.core import VectorStoreIndex

from app.core.embedding_model_tutor import embedding_model_tutor
from app.core.qdrant_tutor import get_qdrant_vector_store


# ==========================================
# 1. CONFIGURATION
# ==========================================

DEFAULT_TOP_K = 5


# ==========================================
# 2. INITIALIZE VECTOR INDEX
# ==========================================

vector_store = get_qdrant_vector_store()

vector_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embedding_model_tutor,
)


# ==========================================
# 3. RETRIEVE KNOWLEDGE
# ==========================================

def retrieve_knowledge(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict]:

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    retriever = vector_index.as_retriever(
        similarity_top_k=top_k
    )

    retrieved_nodes = retriever.retrieve(query.strip())

    results = []

    for item in retrieved_nodes:
        node = item.node
        metadata = node.metadata or {}

        results.append({
            "content": node.get_content(),
            "score": item.score,
            "metadata": {
                "source": metadata.get("source"),
                "section": metadata.get("section"),
                "section_number": metadata.get("section_number"),
                "category": metadata.get("category"),
                "tags": metadata.get("tags", []),

                # Feature metadata
                "feature_number": metadata.get("feature_number"),
                "feature_title": metadata.get("feature_title"),
                "route": metadata.get("route"),

                # FAQ metadata
                "faq_category": metadata.get("faq_category"),
                "faq_question_number": metadata.get("faq_question_number"),
                "faq_chunk_index": metadata.get("faq_chunk_index"),

                "chunk_index": metadata.get("chunk_index"),
            },
        })

    return results
