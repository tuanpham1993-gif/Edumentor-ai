
from typing import Sequence

from app.core.embedding_model_tutor import (
    embedding_model_tutor,
    EMBEDDING_DIMENSION,
)


# ==========================================
# 1. EMBEDDING SERVICE
# ==========================================

class EmbeddingService:

    def __init__(self):
        self.model = embedding_model_tutor
        self.embedding_dimension = EMBEDDING_DIMENSION

    # ======================================
    # 2. ENCODE SINGLE TEXT
    # ======================================

    def encode_text(self, text: str) -> list[float]:
        """
        Convert a single text into an embedding vector.
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must not be empty.")

        embedding = self.model.encode(
            text.strip(),
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        if len(embedding) != self.embedding_dimension:
            raise ValueError(
                f"Invalid embedding dimension: {len(embedding)}. "
                f"Expected: {self.embedding_dimension}"
            )

        return embedding.tolist()

    # ======================================
    # 3. ENCODE MULTIPLE TEXTS
    # ======================================

    def encode_texts(
        self,
        texts: Sequence[str],
        batch_size: int = 32,
    ) -> list[list[float]]:
        """
        Convert multiple texts into embedding vectors.
        """

        if not texts:
            return []

        if any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            raise ValueError("All input texts must be non-empty strings.")

        embeddings = self.model.encode(
            [text.strip() for text in texts],
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Invalid embedding dimension: {embeddings.shape[1]}. "
                f"Expected: {self.embedding_dimension}"
            )

        return embeddings.tolist()


# ==========================================
# 4. SHARED SERVICE INSTANCE
# ==========================================

embedding_service = EmbeddingService()
