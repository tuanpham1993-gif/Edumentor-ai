
import json

from llama_index.core.schema import TextNode, MetadataMode

from app.core.qdrant_tutor import (
    qdrant_client,
    COLLECTION_NAME,
)

from app.core.embedding_model_tutor import embedding_model_tutor


def main():
    print("========== FAQ EMBEDDING INSPECTION ==========")

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

            if metadata.get("faq_question_number") != 3:
                continue

            found = True

            content = node_data.get("text", "")

            # Khôi phục cả metadata exclusion keys
            node = TextNode(
                text=content,
                metadata=metadata,
                excluded_embed_metadata_keys=node_data.get(
                    "excluded_embed_metadata_keys", []
                ),
                excluded_llm_metadata_keys=node_data.get(
                    "excluded_llm_metadata_keys", []
                ),
            )

            embedding_text = node.get_content(
                metadata_mode=MetadataMode.EMBED
            )

            print("\n[1] ORIGINAL CONTENT")
            print(content)

            print("\n[2] METADATA")
            print(metadata)

            print("\n[3] TEXT SENT TO EMBEDDING")
            print(embedding_text)

            print("\n[4] CHARACTER LENGTH")
            print("Original:", len(content))
            print("Embedding:", len(embedding_text))

            # Đếm token đầy đủ, không cắt
            full_tokens = tokenizer.encode(
                embedding_text,
                add_special_tokens=True,
                truncation=False,
            )

            # Mô phỏng giới hạn đầu vào thực tế của model
            truncated_tokens = tokenizer.encode(
                embedding_text,
                add_special_tokens=True,
                truncation=True,
                max_length=max_tokens,
            )

            print("\n[5] TOKEN INFORMATION")
            print("Model max sequence length:", max_tokens)
            print("Full token count:", len(full_tokens))
            print("Tokens sent within model limit:", len(truncated_tokens))

            print("\n[6] ACTUAL TEXT WITHIN MODEL LIMIT")
            print(
                tokenizer.decode(
                    truncated_tokens,
                    skip_special_tokens=False,
                )
            )

            if len(full_tokens) > max_tokens:
                print("\nWARNING: TEXT EXCEEDS MODEL TOKEN LIMIT!")
            else:
                print("\nSUCCESS: FULL TEXT FITS MODEL TOKEN LIMIT.")

            break

        if found or next_offset is None:
            break

        offset = next_offset

    if not found:
        print("FAQ Q3 NOT FOUND.")

    print("\n========== INSPECTION FINISHED ==========")


if __name__ == "__main__":
    main()
