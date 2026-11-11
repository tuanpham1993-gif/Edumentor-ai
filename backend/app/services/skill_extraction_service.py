import json
import httpx
from app.core.config import settings
import logging
logger = logging.getLogger(__name__)

async def rearrange_learning_path(
    learning_path: dict,
    client: httpx.AsyncClient
) -> dict:

    payload = {
        "model": "qwen3",
        "messages": [
            {
                "role": "system",
                "content": settings.SYSTEM_PROMPT_LEARNING_PATH + "\n/no_think"
            },
            {
                "role": "user",
                "content": json.dumps(
                    learning_path,
                    ensure_ascii=False
                )
            }
        ],
        "temperature": 0,
        "max_tokens": 16384,
        "stream": False,
        "response_format": {
            "type": "json_object"
        }
    }

    response = await client.post(
        "/v1/chat/completions",
        json=payload
    )
    response.raise_for_status()

    result = response.json()

    # Inspect the actual LLM response
    choice = result["choices"][0]
    message = choice["message"]

    content = message.get("content")

    logger.info("Base LLM finish_reason: %s", choice.get("finish_reason"))
    logger.info("Base LLM message keys: %s", list(message.keys()))
    logger.info("Base LLM content: %r", content)
    logger.info(
        "Base LLM reasoning_content: %r",
        message.get("reasoning_content")
    )

    if not content or not content.strip():
        raise ValueError(
            f"Base LLM returned empty content. "
            f"finish_reason={choice.get('finish_reason')}"
        )

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON returned by base LLM: %r", content)
        raise ValueError("Base LLM did not return valid JSON.") from exc

async def generate_skill_result(user_prompt: str, client: httpx.AsyncClient)->dict:
    payload = {
        "model": "edumentor-qwen3",
        "messages": [
            {
                "role": "system",
                "content": settings.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt + " /no_think"
            }
        ],
        "temperature": 0,
        "max_tokens": 512,
        "stream": False,
        "response_format": {
            "type": "json_object"
        }
    }

    response = await client.post(
        f"{settings.LLM_URL_ADAPTER}/v1/chat/completions",
        json = payload
    )
    response.raise_for_status() #if error occurs
    result = response.json()
    print(result)

    content = result["choices"][0]["message"]["content"]
    logger.info("LLM finish reason: %s", result["choices"][0].get("finish_reason"))
    logger.info("LLM raw response: %r", content)
    try:
        parsed_result = json.loads(content)

    except json.JSONDecodeError:
        logger.exception("LLM generated invalid JSON")
        raise

    return parsed_result