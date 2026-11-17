from google import genai

from app.core.config import settings


client = genai.Client(api_key=settings.LLM_API_KEY)


def generate_text(prompt: str, api_key: str | None = None) -> str:
    if api_key and api_key.strip():
        call_client = genai.Client(api_key=api_key.strip())
    else:
        call_client = client

    response = call_client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini không trả về nội dung.")

    return response.text