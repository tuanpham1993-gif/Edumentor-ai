
import logging
import re

import httpx
from app.core.config import settings
logger = logging.getLogger(__name__)
class LLMInferenceError(Exception):
    """Raised when the LLM response cannot be retrieved."""


_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(content: str) -> str:
    """Remove a Qwen3 <think>...</think> block if the server left it in the content."""
    return _THINK.sub("", content).strip()


async def generate_g1_response(
    messages: list[dict[str, str]],
    client: httpx.AsyncClient,
) -> str:
    # The adapter was trained with apply_chat_template(..., enable_thinking=False)
    # (06_HUAN_LUYEN.md). llama.cpp (--jinja) applies the same template switch
    # through chat_template_kwargs, so the prompt matches training. Appending
    # "/no_think" to the user message would add text the adapter never saw.
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": [message.copy() for message in messages],
        "temperature": 0,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "stream": False,
        "response_format": {
            "type": "json_object"
        },
        "chat_template_kwargs": {"enable_thinking": False},
    }

    try:
        response = await client.post(
            "/v1/chat/completions",
            json=payload,
        )

        response.raise_for_status()

    except httpx.TimeoutException as exc:
        logger.error("G1 LLM request timed out.")
        raise LLMInferenceError(
            "The LLM request timed out."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.error(
            "G1 LLM server returned HTTP %s.",
            exc.response.status_code,
        )
        raise LLMInferenceError(
            "The LLM server returned an HTTP error."
        ) from exc

    except httpx.RequestError as exc:
        logger.error("Unable to connect to G1 LLM server: %s", exc)
        raise LLMInferenceError(
            "Unable to communicate with the LLM server."
        ) from exc

    try:
        result = response.json()

        choices = result["choices"]
        if not choices:
            raise ValueError("LLM returned no choices.")

        choice = choices[0]
        finish_reason = choice.get("finish_reason")

        if finish_reason == "length":
            raise LLMInferenceError(
                "LLM response was truncated because the token limit was reached."
            )

        content = choice["message"]["content"]
        if isinstance(content, str):
            content = strip_think(content)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM returned empty content.")

        logger.info(
            "G1 inference completed. Finish reason: %s, response length: %d",
            finish_reason,
            len(content),
        )

        return content

    except LLMInferenceError:
        raise

    except (ValueError, KeyError, TypeError, IndexError) as exc:
        logger.exception("Invalid response structure from LLM server.")
        raise LLMInferenceError(
            "The LLM server returned an invalid response."
        ) from exc
