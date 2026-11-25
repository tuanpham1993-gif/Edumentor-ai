import json
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_llm_client
from app.routers.v1.endpoints.recommendation_service import router as recommendation_router

BATCH_01_PATH = Path(__file__).resolve().parents[2] / "datajson" / "LLM_dataset" / "g1" / "raw" / "batch_01.json"

_test_app = FastAPI()
_test_app.include_router(recommendation_router, prefix="/api/learning-paths-generation")


def _make_mock_llm_client(status_code: int, payload: dict) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        body = json.loads(request.content.decode("utf-8"))
        assert body["response_format"] == {"type": "json_object"}
        # same template switch as training (enable_thinking=False); no "/no_think" text appended
        assert body["chat_template_kwargs"] == {"enable_thinking": False}
        assert not body["messages"][-1]["content"].endswith("/no_think")
        return httpx.Response(status_code=status_code, json=payload)

    return httpx.AsyncClient(
        base_url="http://mock-llm",
        transport=httpx.MockTransport(handler),
    )


def test_generate_ai_2_matches_batch_01_schema():
    sample = json.loads(BATCH_01_PATH.read_text(encoding="utf-8"))[0]
    expected_output = sample["expected_output"]

    mock_client = _make_mock_llm_client(
        200,
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(expected_output, ensure_ascii=False)},
                }
            ]
        },
    )
    _test_app.dependency_overrides[get_llm_client] = lambda: mock_client
    try:
        with TestClient(_test_app) as test_client:
            response = test_client.post("/api/learning-paths-generation/generate_ai_2/raw", json=sample["input"])
    finally:
        _test_app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == expected_output


def test_generate_ai_2_invalid_llm_output_returns_502():
    sample = json.loads(BATCH_01_PATH.read_text(encoding="utf-8"))[0]

    mock_client = _make_mock_llm_client(
        200,
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps({"unexpected": "shape"})},
                }
            ]
        },
    )
    _test_app.dependency_overrides[get_llm_client] = lambda: mock_client
    try:
        with TestClient(_test_app) as test_client:
            response = test_client.post("/api/learning-paths-generation/generate_ai_2/raw", json=sample["input"])
    finally:
        _test_app.dependency_overrides.clear()

    assert response.status_code == 502
