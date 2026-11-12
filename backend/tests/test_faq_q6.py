
import json

from app.core.qdrant_tutor import (
    qdrant_client,
    COLLECTION_NAME,
)

from app.core.embedding_model_tutor import embedding_model_tutor


def main():
    print("========== FAQ Q6 INSPECTION ==========")

    offset = None
    found = False

    tokenizer = embedding_model_tutor._model._first_module().tokenizer
    max_tokens = embedding_model_tutor._model.max_seq_length

    while True:
        points, next_offset = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            payload = point.payload or {}
            raw_node = payload.get("_node_content")

            if not raw_node:
                continue

            node_data = json.loads(raw_node)
            metadata = node_data.get("metadata", {})

            if metadata.get("faq_question_number") != 6:
                continue

            found = True
            content = node_data.get("text", "")

            print("\nFAQ Q6 FOUND")
            print("\nCONTENT:")
            print(content)

            tokens = tokenizer.encode(
                content,
                add_special_tokens=True,
                truncation=False,
            )

            print("\nTOKEN INFORMATION")
            print("Token count:", len(tokens))
            print("Model max tokens:", max_tokens)

            print("\nTOKENIZED TEXT")
            print(
                tokenizer.decode(
                    tokens[:max_tokens],
                    skip_special_tokens=False,
                )
            )

            if len(tokens) > max_tokens:
                print("\nWARNING: FAQ Q6 EXCEEDS TOKEN LIMIT")
            else:
                print("\nSUCCESS: FAQ Q6 FITS TOKEN LIMIT")

            break

        if found or next_offset is None:
            break

        offset = next_offset

    if not found:
        print("FAQ Q6 NOT FOUND IN QDRANT")

    print("\n========== INSPECTION FINISHED ==========")


if __name__ == "__main__":
    main()
