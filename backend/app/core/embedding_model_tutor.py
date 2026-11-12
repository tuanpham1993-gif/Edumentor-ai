
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# Embedding Model Configuration
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_DIMENSION = 384


# Initialize HuggingFace Embedding for LlamaIndex
embedding_model_tutor = HuggingFaceEmbedding(
    model_name=EMBEDDING_MODEL_NAME,
    normalize=True,
)
