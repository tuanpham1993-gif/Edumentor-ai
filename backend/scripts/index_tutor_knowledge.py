
import re
from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from app.core.embedding_model_tutor import embedding_model_tutor
from app.core.qdrant_tutor import (
    qdrant_client,
    COLLECTION_NAME,
    create_collection,
    get_qdrant_vector_store,
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

DOCUMENT_PATH = (
    BASE_DIR / "data" / "knowledge" / "SYSTEM_EN.md"
)

# Embedding model: MiniLM, maximum 128 tokens.
MAX_EMBED_TOKENS = embedding_model_tutor._model.max_seq_length

EMBEDDING_TOKENIZER = (
    embedding_model_tutor._model._first_module().tokenizer
)

CHUNK_SIZE = 100
CHUNK_OVERLAP = 15
TOKEN_RESERVE = 8

EXPECTED_FAQ_QUESTIONS = 10

EXCLUDED_SECTIONS = {11}


# ==========================================
# 2. SECTION METADATA
# ==========================================

SECTION_CONFIG = {
    1: {
        "category": "system_overview",
        "description": (
            "General information about the EduMentor platform, "
            "system environment, application structure, "
            "and development conventions."
        ),
        "tags": ["overview", "environment", "system"],
    },
    2: {
        "category": "account_management",
        "description": (
            "User account and profile management, including "
            "registration, login, authentication, and profile settings."
        ),
        "tags": ["account", "profile", "authentication"],
    },
    3: {
        "category": "course_catalog",
        "description": (
            "Course catalog operations: browse, search, filter, "
            "view course details, and bookmark courses from catalog cards."
        ),
        "tags": ["course", "catalog", "search", "bookmark"],
    },
    4: {
        "category": "my_courses",
        "description": (
            "Personal My Courses workspace: view and manage the learner's "
            "saved or bookmarked courses, ongoing courses, "
            "completed courses, and abandoned courses."
        ),
        "tags": ["my_courses", "progress", "bookmark", "saved_courses"],
    },
    5: {
        "category": "learning_path",
        "description": (
            "AI Learning Path Advisor and roadmap management, "
            "including skill-based learning recommendations "
            "and personalized learning roadmaps."
        ),
        "tags": ["learning_path", "roadmap", "skills"],
    },
    6: {
        "category": "quiz",
        "description": (
            "AI Quiz Practice and assessment: practice skill-based quizzes, "
            "answer questions, evaluate quiz results, "
            "and review assessment scores."
        ),
        "tags": ["quiz", "assessment", "score", "practice"],
    },
    7: {
        "category": "ai_tutor",
        "description": (
            "AI Tutor subsystem for practical programming assistance, "
            "code explanations, programming questions, "
            "and interactive coding guidance."
        ),
        "tags": ["ai_tutor", "chatbot", "programming"],
    },
    8: {
        "category": "security",
        "description": (
            "Official learner security policies and governance rules, "
            "including data privacy, user data isolation, "
            "and course completion requirements."
        ),
        "tags": ["security", "privacy", "governance", "policy"],
    },
    9: {
        "category": "troubleshooting",
        "description": (
            "Error code reference and troubleshooting guide, "
            "including common system errors, their causes, "
            "and recommended solutions."
        ),
        "tags": ["error", "troubleshooting", "solution"],
    },
    10: {
        "category": "faq",
        "description": (
            "Frequently asked questions and answers about "
            "using the EduMentor learning platform."
        ),
        "tags": ["faq", "questions", "answers"],
    },
}


# ==========================================
# 3. TOKEN UTILITIES
# ==========================================

def count_embedding_tokens(text: str) -> int:
    """
    Count tokens using the actual MiniLM tokenizer.
    Includes special tokens.
    """

    tokens = EMBEDDING_TOKENIZER.encode(
        text,
        add_special_tokens=True,
    )

    return len(tokens)


def split_text_by_token_limit(
    text: str,
    prefix: str,
):
    """
    Split text while preserving the prefix.

    Every final embedding text must stay within
    the embedding model's maximum token limit.
    """

    prefix_tokens = count_embedding_tokens(prefix)

    available_tokens = (
        MAX_EMBED_TOKENS
        - prefix_tokens
        - TOKEN_RESERVE
    )

    if available_tokens < 20:
        raise ValueError(
            f"Prefix is too long:\n{prefix}\n"
            f"Available tokens: {available_tokens}"
        )

    chunk_size = min(
        CHUNK_SIZE,
        available_tokens,
    )

    chunk_overlap = min(
        CHUNK_OVERLAP,
        chunk_size // 4,
    )

    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        tokenizer=lambda value: EMBEDDING_TOKENIZER.encode(
            value,
            add_special_tokens=False,
        ),
    )

    return splitter.split_text(text), chunk_size


# ==========================================
# 4. CREATE DOCUMENT
# ==========================================

def create_document(
    text: str,
    metadata: dict,
) -> Document:
    """
    Create a LlamaIndex document.

    Metadata is stored in Qdrant but excluded
    from embedding text and LLM metadata.
    """

    token_count = count_embedding_tokens(text)

    if token_count > MAX_EMBED_TOKENS:
        raise ValueError(
            f"Document exceeds embedding limit: "
            f"{token_count}/{MAX_EMBED_TOKENS} tokens.\n"
            f"Content preview: {text[:300]}"
        )

    return Document(
        text=text,
        metadata=metadata,
        excluded_embed_metadata_keys=list(metadata.keys()),
        excluded_llm_metadata_keys=list(metadata.keys()),
    )


# ==========================================
# 5. READ MARKDOWN DOCUMENT
# ==========================================

def read_markdown():

    if not DOCUMENT_PATH.exists():
        raise FileNotFoundError(
            f"Document not found: {DOCUMENT_PATH}"
        )

    content = DOCUMENT_PATH.read_text(
        encoding="utf-8"
    )

    if not content.strip():
        raise ValueError("SYSTEM_EN.md is empty.")

    print("Document loaded successfully.")
    print("Path:", DOCUMENT_PATH)

    return content


# ==========================================
# 6. SPLIT DOCUMENT INTO SECTIONS
# ==========================================

def split_sections(content: str):

    pattern = re.compile(
        r"^##\s+(?:Section\s+)?(\d+)[.)]?\s*(.*?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    matches = list(pattern.finditer(content))

    if not matches:
        raise ValueError(
            "No numbered sections found. "
            "Please check SYSTEM_EN.md headings."
        )

    sections = []

    for index, match in enumerate(matches):

        section_number = int(match.group(1))
        section_title = match.group(2).strip()

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(content)

        section_content = content[start:end].strip()

        if section_number in EXCLUDED_SECTIONS:
            print(
                f"Excluded Section {section_number}: "
                f"{section_title}"
            )
            continue

        if section_number not in SECTION_CONFIG:
            print(
                f"Skipped unsupported Section {section_number}"
            )
            continue

        if not section_content:
            print(
                f"Warning: Section {section_number} is empty."
            )
            continue

        sections.append({
            "section_number": section_number,
            "section_title": section_title,
            "content": section_content,
        })

    found_numbers = {
        section["section_number"]
        for section in sections
    }

    missing_sections = (
        set(SECTION_CONFIG.keys()) - found_numbers
    )

    if missing_sections:
        raise ValueError(
            f"Missing or empty sections: "
            f"{sorted(missing_sections)}"
        )

    print(f"Valid sections: {len(sections)}")

    return sections


# ==========================================
# 7. SPLIT SECTION INTO FEATURES
# ==========================================

def split_section_into_features(content: str):
    """
    Split a section by level-3 numbered headings.

    Example:
        ### 2.1. Registration Process
        ### 2.2. Login Process
        ### 2.3. Password Recovery Process

    Each feature keeps its own title and content.
    """

    pattern = re.compile(
        r"^###\s+(\d+\.\d+)\.?\s*(.*?)\s*$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(content))

    # Sections without level-3 headings are kept
    # as general information.
    if not matches:
        return [{
            "feature_number": None,
            "feature_title": "General Information",
            "content": content.strip(),
        }]

    features = []

    # Keep any content before the first feature heading.
    intro_content = content[:matches[0].start()].strip()

    if intro_content:
        features.append({
            "feature_number": None,
            "feature_title": "Section Introduction",
            "content": intro_content,
        })

    for index, match in enumerate(matches):

        feature_number = match.group(1)
        feature_title = match.group(2).strip()

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(content)

        feature_content = content[start:end].strip()

        if not feature_content:
            continue

        features.append({
            "feature_number": feature_number,
            "feature_title": feature_title,
            "content": feature_content,
        })

    return features


# ==========================================
# 8. EXTRACT ROUTE FROM FEATURE
# ==========================================

def extract_route(
    feature_title: str,
    feature_content: str,
):
    """
    Extract frontend route from a feature.

    Priority:
    1. Absolute localhost frontend URL.
    2. Route written inside backticks.
    3. Route written in parentheses.
    """

    text = feature_title + "\n" + feature_content

    # Example:
    # http://localhost:5173/login
    absolute_url_match = re.search(
        r"https?://localhost:5173(?P<route>/[^\s)\]`]+)",
        text,
        re.IGNORECASE,
    )

    if absolute_url_match:
        return absolute_url_match.group("route").rstrip(".,;")

    # Example:
    # (`/login`)
    backtick_match = re.search(
        r"`(?P<route>/[^`\s]+)`",
        text,
    )

    if backtick_match:
        return backtick_match.group("route").rstrip(".,;")

    # Example:
    # (/login)
    parenthesis_match = re.search(
        r"\((?P<route>/[A-Za-z0-9_{}./-]+)\)",
        text,
    )

    if parenthesis_match:
        return parenthesis_match.group("route")

    return None


# ==========================================
# 9. SPLIT FAQ INTO CATEGORY AND Q&A
# ==========================================

def split_faq_questions(content: str):
    """
    Split Section 10 into individual Question + Answer pairs.
    Each FAQ question and its answer stay together.
    """

    category_pattern = re.compile(
        r"^###\s+10\.\d+\.\s*(.*?)\s*$",
        re.MULTILINE,
    )

    category_matches = list(
        category_pattern.finditer(content)
    )

    if not category_matches:
        raise ValueError(
            "No FAQ categories found in Section 10."
        )

    faq_items = []

    for category_index, category_match in enumerate(
        category_matches
    ):

        category_name = category_match.group(1).strip()

        category_start = category_match.end()

        if category_index + 1 < len(category_matches):
            category_end = category_matches[
                category_index + 1
            ].start()
        else:
            category_end = len(content)

        category_content = content[
            category_start:category_end
        ].strip()

        question_pattern = re.compile(
            r"^\s*[-*]\s+\*{1,2}Q(\d+):\s*(.*?)\*{1,2}\s*$",
            re.MULTILINE,
        )

        question_matches = list(
            question_pattern.finditer(category_content)
        )

        if not question_matches:
            raise ValueError(
                f"No questions found in FAQ category: "
                f"{category_name}"
            )

        for question_index, question_match in enumerate(
            question_matches
        ):

            question_number = int(question_match.group(1))

            question_start = question_match.start()

            if question_index + 1 < len(question_matches):
                question_end = question_matches[
                    question_index + 1
                ].start()
            else:
                question_end = len(category_content)

            qa_content = category_content[
                question_start:question_end
            ].strip()

            if not re.search(
                r"Answer\s*:",
                qa_content,
                re.IGNORECASE,
            ):
                raise ValueError(
                    f"Answer not found for FAQ Q{question_number}."
                )

            faq_items.append({
                "faq_category": category_name,
                "question_number": question_number,
                "content": qa_content,
            })

    found_questions = sorted(
        item["question_number"]
        for item in faq_items
    )

    expected_questions = list(
        range(1, EXPECTED_FAQ_QUESTIONS + 1)
    )

    if found_questions != expected_questions:
        raise ValueError(
            "FAQ questions are missing or duplicated. "
            f"Expected: {expected_questions}, "
            f"Found: {found_questions}"
        )

    print(f"FAQ categories: {len(category_matches)}")
    print(f"FAQ questions: {len(faq_items)}")

    return faq_items


# ==========================================
# 10. CREATE DOCUMENT CHUNKS
# ==========================================


def create_chunks(sections):

    documents = []

    # Dùng để đánh số chunk liên tục trong từng section.
    for section in sections:

        section_number = section["section_number"]
        section_title = section["section_title"]

        config = SECTION_CONFIG[section_number]

        # --------------------------------------
        # SECTION 10: FAQ SPECIAL PROCESSING
        # --------------------------------------

        if section_number == 10:

            faq_items = split_faq_questions(
                section["content"]
            )

            section_chunk_count = 0

            for faq in faq_items:

                # Prefix chứa thông tin để AI hiểu ngữ cảnh.
                prefix = (
                    f"Section: {section_title}\n"
                    f"Topic: {config['category']}\n"
                    f"Feature: FAQ - {faq['faq_category']}\n"
                    f"Question: Q{faq['question_number']}\n\n"
                )

                # Quan trọng:
                # Chia nội dung FAQ nếu vượt giới hạn token.
                chunks, actual_chunk_size = split_text_by_token_limit(
                    faq["content"],
                    prefix,
                )

                print(
                    f"FAQ Q{faq['question_number']} "
                    f"({faq['faq_category']}): {len(chunks)} chunks"
                )

                # Một câu hỏi có thể tạo ra nhiều chunks.
                for faq_chunk_index, chunk in enumerate(chunks):

                    embedding_text = prefix + chunk

                    metadata = {
                        "source": "SYSTEM_EN.md",
                        "section": section_title,
                        "section_number": section_number,
                        "category": config["category"],
                        "tags": config["tags"],

                        # Số chunk liên tục trong Section 10.
                        "chunk_index": section_chunk_count,

                        # Giữ thông tin FAQ gốc.
                        "faq_category": faq["faq_category"],
                        "faq_question_number": faq[
                            "question_number"
                        ],

                        # Phân biệt các chunk thuộc cùng một câu hỏi.
                        "faq_chunk_index": faq_chunk_index,
                    }

                    document = create_document(
                        text=embedding_text,
                        metadata=metadata,
                    )

                    documents.append(document)

                    token_count = count_embedding_tokens(
                        embedding_text
                    )

                    print(
                        f"  FAQ Q{faq['question_number']} "
                        f"- Chunk {faq_chunk_index}: "
                        f"{token_count} tokens"
                    )

                    section_chunk_count += 1

            print(
                f"Section 10: {section_title} "
                f"-> {section_chunk_count} chunks "
                f"from {len(faq_items)} FAQ questions"
            )

            continue

        # --------------------------------------
        # SECTION 1-9: FEATURE-BASED CHUNKING
        # --------------------------------------

        features = split_section_into_features(
            section["content"]
        )

        section_chunk_count = 0

        for feature in features:

            feature_number = feature["feature_number"]
            feature_title = feature["feature_title"]
            feature_content = feature["content"]

            # Find route from feature title/content.
            route = extract_route(
                feature_title,
                feature_content,
            )

            # Build context prefix for embedding.
            prefix = (
                f"Section: {section_title}\n"
                f"Topic: {config['category']}\n"
                f"Feature: {feature_title}\n"
            )

            if feature_number:
                prefix += (
                    f"Feature Number: {feature_number}\n"
                )

            if route:
                prefix += f"Route: {route}\n"

            prefix += "\n"

            # Split this feature independently.
            chunks, actual_chunk_size = split_text_by_token_limit(
                feature_content,
                prefix,
            )

            print(
                f"Section {section_number} - "
                f"{feature_number or 'General'} "
                f"{feature_title}: {len(chunks)} chunks"
            )

            for chunk in chunks:

                embedding_text = prefix + chunk

                metadata = {
                    "source": "SYSTEM_EN.md",
                    "section": section_title,
                    "section_number": section_number,
                    "category": config["category"],
                    "tags": config["tags"],
                    "chunk_index": section_chunk_count,
                    "feature_number": feature_number,
                    "feature_title": feature_title,
                }

                if route:
                    metadata["route"] = route

                document = create_document(
                    text=embedding_text,
                    metadata=metadata,
                )

                documents.append(document)

                print(
                    f"  Chunk {section_chunk_count}: "
                    f"{count_embedding_tokens(embedding_text)} tokens"
                    + (f" | Route: {route}" if route else "")
                )

                section_chunk_count += 1

        print(
            f"Section {section_number}: "
            f"{section_title} -> {section_chunk_count} chunks"
        )

    if not documents:
        raise ValueError("No chunks were created.")

    print(f"\nTotal chunks: {len(documents)}")

    return documents



# ==========================================
# 11. RESET QDRANT COLLECTION
# ==========================================

def reset_collection():

    if qdrant_client.collection_exists(COLLECTION_NAME):

        print("\nDeleting old collection...")

        qdrant_client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    create_collection()

    print("Collection reset successfully.")


# ==========================================
# 12. INDEX DOCUMENTS INTO QDRANT
# ==========================================

def index_documents(documents):

    vector_store = get_qdrant_vector_store()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    print("\nStarting embedding and indexing...")

    VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        embed_model=embedding_model_tutor,
        show_progress=True,
    )

    print("Indexing completed.")


# ==========================================
# 13. VERIFY INDEXING
# ==========================================

def verify_indexing(expected_count: int):

    collection_info = qdrant_client.get_collection(
        collection_name=COLLECTION_NAME
    )

    actual_count = collection_info.points_count

    print("\n========== INDEXING RESULT ==========")
    print("Collection:", COLLECTION_NAME)
    print("Expected points:", expected_count)
    print("Actual points:", actual_count)

    print(
        "Vector dimension:",
        collection_info.config.params.vectors.size,
    )

    if actual_count != expected_count:
        raise RuntimeError(
            "Indexing verification failed: "
            f"expected {expected_count}, got {actual_count}"
        )

    print("\nINDEXING VERIFIED SUCCESSFULLY!")


# ==========================================
# 14. MAIN
# ==========================================

def main():

    print("========== EDUMENTOR RAG INDEXING ==========")

    print(
        "Embedding model max tokens:",
        MAX_EMBED_TOKENS,
    )

    content = read_markdown()

    sections = split_sections(content)

    # Create and validate all chunks before
    # deleting the existing Qdrant collection.
    documents = create_chunks(sections)

    print("\nAll documents passed token validation.")

    reset_collection()

    index_documents(documents)

    verify_indexing(len(documents))


if __name__ == "__main__":
    main()
