
try:
    from sentence_transformers import SentenceTransformer
except Exception as import_err:  # pragma: no cover
    # SentenceTransformers not available in this environment.
    SentenceTransformer = None
    _SENTENCE_TRANSFORMERS_IMPORT_ERROR = import_err

# Duplicate block removed – kept only one configuration and initialization


# ==========================================
# 1. EMBEDDING MODEL CONFIGURATION
# ==========================================

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_DIMENSION = 384


# ==========================================
# 2. INITIALIZE EMBEDDING MODEL
# ==========================================

if SentenceTransformer is not None:
    embedding_model_tutor = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )
    embedding_model_tutor.max_seq_length = 128
else:
    class _MissingEmbeddingModel:
        def __getattr__(self, name):
            raise RuntimeError(
                "SentenceTransformers library is not installed. Embedding model cannot be used."
            )
    embedding_model_tutor = _MissingEmbeddingModel()
