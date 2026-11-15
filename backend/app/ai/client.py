from google import genai

from app.core.config import settings


client = genai.Client(api_key=settings.LLM_API_KEY)


def generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini không trả về nội dung.")

    return response.text