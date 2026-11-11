import httpx
from fastapi import Request

def get_llm_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.llm_client

def get_llm_client_base(request: Request) -> httpx.AsyncClient:
    return request.app.state.llm_client_base