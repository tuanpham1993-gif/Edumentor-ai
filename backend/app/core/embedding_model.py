from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding_skills_name(texts_list: list[str])->list[list[float]]:
    embeddings = model.encode(texts_list, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()