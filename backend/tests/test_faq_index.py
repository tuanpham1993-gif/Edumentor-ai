
from app.core.qdrant_tutor import (
    qdrant_client,
    COLLECTION_NAME,
)

from app.core.embedding_model_tutor import (
    embedding_model_tutor,
)


def main():

    print("========== FAQ INDEX INSPECTION ==========")

    result = qdrant_client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=None,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    points, next_offset = result

    found = False

    for point in points:

        payload = point.payload or {}

        metadata = payload.get("_node_content")

        if not metadata:
            continue

        import json

        node = json.loads(metadata)

        node_metadata = node.get("metadata", {})
        content = node.get("text", "")

        if (
            node_metadata.get("faq_question_number") == 3
            or "Does clicking" in content
        ):

            found = True

            print("\nFAQ Q3 FOUND")

            print("Metadata:")
            print(node_metadata)

            print("\nContent:")
            print(content)

            print("\nContent characters:")
            print(len(content))

            print("\nEmbedding max sequence length:")
            print(
                embedding_model_tutor._model.max_seq_length
            )

    if not found:
        print("\nFAQ Q3 NOT FOUND in first 100 points.")

    print("\n========== INSPECTION FINISHED ==========")


if __name__ == "__main__":
    main()
