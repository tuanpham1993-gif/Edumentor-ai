"""
Handlers package for EduMentor AI Chatbot.
Provides specialized handlers for search, knowledge, code, and reinforcement.
"""

from app.ai.handlers.code_handler import CodeHandler, code_handler
from app.ai.handlers.knowledge_handler import (
    KnowledgeHandler,
    build_learning_path_instructions,
    build_system_operation_instructions,
    build_system_operation_response,
    knowledge_handler,
)
from app.ai.handlers.reinforcement_handler import (
    ReinforcementHandler,
    reinforcement_handler,
)
from app.ai.handlers.search_handler import SearchHandler, search_handler

__all__ = [
    "CodeHandler",
    "KnowledgeHandler",
    "ReinforcementHandler",
    "SearchHandler",
    "build_learning_path_instructions",
    "build_system_operation_instructions",
    "build_system_operation_response",
    "code_handler",
    "knowledge_handler",
    "reinforcement_handler",
    "search_handler",
]
