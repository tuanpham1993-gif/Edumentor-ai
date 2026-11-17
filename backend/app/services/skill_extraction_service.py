import json
import httpx
from app.core.config import settings
import logging
logger = logging.getLogger(__name__)

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