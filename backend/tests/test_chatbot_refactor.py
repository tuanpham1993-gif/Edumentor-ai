"""
Comprehensive tests for EduMentor AI Chatbot Refactor & Fixes:
1. Query Router (Exact/Semantic Course & Skill, Strategy Sync, Custom API Key)
2. Search Handler (PostgreSQL, Qdrant Course & Skill, Canonical lookup, Fallbacks, Connection failure)
3. Specialized Handlers (Knowledge, Code, Reinforcement)
4. Orchestrator (Single query, Multi-query multi-handler, Partial failure recovery, Auth vs Public, Custom API Key)
5. Response Service (Contract preservation, Empty answer/suggestion sanitization, combine_responses)
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ai.handlers.code_handler import CodeHandler
from app.ai.handlers.knowledge_handler import KnowledgeHandler
from app.ai.handlers.reinforcement_handler import ReinforcementHandler
from app.ai.handlers.search_handler import SearchHandler
from app.ai.orchestrator import ChatOrchestrator
from app.ai.query_router import route_query
from app.ai.response_service import ResponseService


class TestChatbotRefactorAndFixes(unittest.TestCase):
    """Test suite covering the complete modular architecture and all 6 fixes."""

    # ==========================================
    # 1. QUERY ROUTER & RETRIEVAL STRATEGY SYNC (FIX 2 & FIX 4)
    # ==========================================

    def test_01_query_router_exact_course_search(self):
        """Exact course search: strategy is sql_qdrant, modes are [sql, qdrant]."""
        query = "Python có những khóa học nào?"
        result = route_query(query)
        self.assertEqual(result["intent"], "course_search")
        self.assertEqual(result["task_type"], "course_name_search")
        self.assertEqual(result["entity_name"], "Python")
        self.assertEqual(result["retrieval_strategy"], "sql_qdrant")
        self.assertEqual(result["retrieval_modes"], ["sql", "qdrant"])

    def test_02_query_router_semantic_course_search(self):
        """Semantic course search: strategy is qdrant, modes are [qdrant], no conflict with sql."""
        query = "Các khóa học nào tốt nhất"
        result = route_query(query)
        self.assertEqual(result["intent"], "course_search")
        self.assertEqual(result["task_type"], "course_semantic_search")
        self.assertEqual(result["retrieval_strategy"], "qdrant")
        self.assertEqual(result["retrieval_modes"], ["qdrant"])

    def test_03_query_router_exact_skill_search(self):
        """Exact skill search: strategy is sql_qdrant, modes are [sql, qdrant]."""
        query = "Tìm các skill về Machine Learning"
        result = route_query(query)
        self.assertEqual(result["intent"], "skill_search")
        self.assertEqual(result["task_type"], "skill_name_search")
        self.assertEqual(result["entity_name"], "Machine Learning")
        self.assertEqual(result["retrieval_strategy"], "sql_qdrant")
        self.assertEqual(result["retrieval_modes"], ["sql", "qdrant"])

    def test_04_query_router_semantic_skill_search(self):
        """Semantic skill search: strategy is qdrant, modes are [qdrant]."""
        query = "Có kỹ năng nào phổ biến nhất"
        result = route_query(query)
        self.assertEqual(result["intent"], "skill_search")
        self.assertEqual(result["task_type"], "skill_semantic_search")
        self.assertEqual(result["retrieval_strategy"], "qdrant")
        self.assertEqual(result["retrieval_modes"], ["qdrant"])

    def test_05_query_router_organization_search(self):
        """Organization search: strategy is sql, modes are [sql]."""
        query = "Khóa học của University of Alberta"
        result = route_query(query)
        self.assertEqual(result["intent"], "course_search")
        self.assertEqual(result["task_type"], "organization_search")
        self.assertEqual(result["entity_type"], "organization")
        self.assertEqual(result["entity_name"], "University of Alberta")
        self.assertEqual(result["retrieval_strategy"], "sql")
        self.assertEqual(result["retrieval_modes"], ["sql"])

    def test_06_query_router_rating_search(self):
        """Rating search: strategy is sql, modes are [sql]."""
        query = "Cho tôi các khóa học 5 sao"
        result = route_query(query)
        self.assertEqual(result["intent"], "course_search")
        self.assertEqual(result["task_type"], "rating_search")
        self.assertEqual(result["entity_type"], "rating")
        self.assertEqual(result["entity_name"], "5")
        self.assertEqual(result["retrieval_strategy"], "sql")
        self.assertEqual(result["retrieval_modes"], ["sql"])

    def test_07_query_router_code_tasks(self):
        """Code analysis and fix: strategy is gemini, modes are [gemini]."""
        q_analysis = "Giải thích đoạn code sau: def foo(x): return x * 2"
        r_analysis = route_query(q_analysis)
        self.assertEqual(r_analysis["task_type"], "code_analysis")
        self.assertEqual(r_analysis["retrieval_strategy"], "gemini")
        self.assertEqual(r_analysis["retrieval_modes"], ["gemini"])

        q_fix = "Sửa lỗi giúp tôi đoạn code này: def divide(): return 1 / 0"
        r_fix = route_query(q_fix)
        self.assertEqual(r_fix["task_type"], "code_fix")
        self.assertEqual(r_fix["retrieval_strategy"], "gemini")
        self.assertEqual(r_fix["retrieval_modes"], ["gemini"])

    def test_08_query_router_reinforcement_request(self):
        """Reinforcement request: strategy is sql_gemini when entity present."""
        query = "Tạo câu hỏi trắc nghiệm ôn tập về Deep Learning"
        result = route_query(query)
        self.assertEqual(result["task_type"], "reinforcement_request")
        self.assertEqual(result["entity_name"], "Deep Learning")
        self.assertEqual(result["retrieval_strategy"], "sql_gemini")
        self.assertEqual(result["retrieval_modes"], ["sql", "gemini"])

    @patch("app.ai.query_router.query_decomposer.generate_text")
    def test_09_query_router_custom_api_key_propagation(self, mock_llm):
        """Verify custom_api_key is propagated to decomposer and LLM routing."""
        mock_llm.return_value = '{"queries": ["Python là gì?", "Tìm các khóa học về Python"]}'
        custom_key = "test-custom-api-key-123"
        route_query("Python là gì? Ngoài ra tìm các khóa học về Python", custom_api_key=custom_key)
        self.assertTrue(mock_llm.called)
        # Check api_key keyword arg passed to generate_text
        _, kwargs = mock_llm.call_args
        self.assertEqual(kwargs.get("api_key"), custom_key)

    # ==========================================
    # 2. SEARCH HANDLER & QDRANT RETRIEVAL (FIX 1)
    # ==========================================

    @patch("app.ai.handlers.search_handler.get_course_by_id")
    @patch("app.ai.handlers.search_handler.qdrant_course_service.search_courses")
    @patch("app.ai.handlers.search_handler.embedding_service.encode_text")
    def test_10_search_handler_qdrant_course_canonical_lookup(self, mock_encode, mock_search, mock_get_course):
        """Qdrant returns hits -> SearchHandler retrieves canonical course from PostgreSQL."""
        mock_encode.return_value = [0.1] * 384
        hit = MagicMock()
        hit.score = 0.92
        hit.payload = {"course_id": 42, "title": "Payload Title", "organization": "Payload Org"}
        mock_search.return_value = [hit]

        mock_db_course = MagicMock()
        mock_db_course.course_id = 42
        mock_db_course.title = "Canonical PostgreSQL Title"
        mock_db_course.description = "Canonical Description"
        mock_db_course.instructor = "Dr. Smith"
        mock_db_course.organization = "Canonical Org"
        mock_db_course.level = "Beginner"
        mock_db_course.rating = 4.8
        mock_db_course.num_reviews = 150
        mock_db_course.num_enrolled = 2000
        mock_db_course.url = "http://example.com/canonical"
        mock_db_course.image = "img.png"
        mock_get_course.return_value = mock_db_course

        handler = SearchHandler()
        mock_db = MagicMock()
        results = handler.search_courses_semantic("machine learning", db=mock_db, allow_sql=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Canonical PostgreSQL Title")
        self.assertEqual(results[0]["qdrant_score"], 0.92)
        mock_get_course.assert_called_with(mock_db, 42)

    @patch("app.ai.handlers.search_handler.get_course_by_id")
    @patch("app.ai.handlers.search_handler.qdrant_course_service.search_courses")
    @patch("app.ai.handlers.search_handler.embedding_service.encode_text")
    def test_11_search_handler_qdrant_course_fallback_when_db_missing(self, mock_encode, mock_search, mock_get_course):
        """When PostgreSQL does not have the course_id, fallback safely to Qdrant payload metadata."""
        mock_encode.return_value = [0.1] * 384
        hit = MagicMock()
        hit.score = 0.85
        hit.payload = {"course_id": 999, "title": "Qdrant Only Title", "organization": "Qdrant Org", "level": "All"}
        mock_search.return_value = [hit]
        mock_get_course.return_value = None  # Not in DB

        handler = SearchHandler()
        mock_db = MagicMock()
        results = handler.search_courses_semantic("robotics", db=mock_db, allow_sql=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Qdrant Only Title")
        self.assertEqual(results[0]["qdrant_score"], 0.85)

    @patch("app.ai.handlers.search_handler.qdrant_course_service.search_courses")
    @patch("app.ai.handlers.search_handler.embedding_service.encode_text")
    def test_12_search_handler_qdrant_connection_failure(self, mock_encode, mock_search):
        """When Qdrant fails to connect, SearchHandler catches exception and returns [] without crashing."""
        mock_encode.return_value = [0.1] * 384
        mock_search.side_effect = ConnectionError("Could not connect to Qdrant:6335")

        handler = SearchHandler()
        results = handler.search_courses_semantic("test query", db=None, allow_sql=False)
        self.assertEqual(results, [])

    @patch("app.ai.handlers.search_handler.get_skill_by_id")
    @patch("app.ai.handlers.search_handler.qdrant_skill_service.search_skill")
    @patch("app.ai.handlers.search_handler.embedding_service.encode_text")
    def test_13_search_handler_qdrant_skill_semantic(self, mock_encode, mock_search, mock_get_skill):
        """Qdrant skill semantic search properly retrieves skill and maps to canonical record."""
        mock_encode.return_value = [0.1] * 384
        hit = MagicMock()
        hit.score = 0.90
        hit.payload = {"skill_id": 105, "skill": "Reinforcement Learning", "num_courses": 4}
        mock_search.return_value = [hit]

        mock_db_skill = MagicMock()
        mock_db_skill.skill_id = 105
        mock_db_skill.skill = "Reinforcement Learning"
        mock_db_skill.is_active = True
        mock_get_skill.return_value = mock_db_skill

        handler = SearchHandler()
        mock_db = MagicMock()
        results = handler.search_skills_semantic("RL techniques", db=mock_db, allow_sql=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["skill"], "Reinforcement Learning")
        self.assertEqual(results[0]["qdrant_score"], 0.90)

    # ==========================================
    # 3. SPECIALIZED HANDLERS (KNOWLEDGE, CODE, REINFORCEMENT)
    # ==========================================

    @patch("app.ai.handlers.knowledge_handler.generate_text")
    def test_14_knowledge_handler_custom_key(self, mock_llm):
        """KnowledgeHandler passes custom_api_key to generate_text."""
        mock_llm.return_value = '{"answer": "Python explanation", "suggestions": []}'
        handler = KnowledgeHandler()
        custom_key = "my-secret-key"
        handler.handle(
            route_result={"intent": "skill_question", "task_type": "knowledge_question"},
            retrieval_context={},
            conversation_history="User: Hi",
            custom_api_key=custom_key,
        )
        _, kwargs = mock_llm.call_args
        self.assertEqual(kwargs.get("api_key"), custom_key)

    @patch("app.ai.handlers.code_handler.generate_text")
    def test_15_code_handler_custom_key(self, mock_llm):
        """CodeHandler passes custom_api_key to generate_text."""
        mock_llm.return_value = '{"answer": "Code fix explanation", "suggestions": []}'
        handler = CodeHandler()
        custom_key = "my-secret-key"
        handler.handle(
            route_result={"intent": "code_fix", "task_type": "code_fix"},
            user_content="x = 1/0",
            conversation_history="",
            custom_api_key=custom_key,
        )
        _, kwargs = mock_llm.call_args
        self.assertEqual(kwargs.get("api_key"), custom_key)

    @patch("app.ai.handlers.reinforcement_handler.generate_text")
    def test_16_reinforcement_handler_custom_key(self, mock_llm):
        """ReinforcementHandler passes custom_api_key to generate_text."""
        mock_llm.return_value = '{"answer": "Quiz question", "suggestions": []}'
        handler = ReinforcementHandler()
        custom_key = "my-secret-key"
        handler.handle(
            route_result={"intent": "reinforcement_request", "entity_name": "SQL"},
            user_content="Quiz me",
            retrieval_context={},
            conversation_history="",
            custom_api_key=custom_key,
        )
        _, kwargs = mock_llm.call_args
        self.assertEqual(kwargs.get("api_key"), custom_key)

    # ==========================================
    # 4. ORCHESTRATOR & MULTI-QUERY (FIX 3, FIX 4, FIX 5)
    # ==========================================

    @patch("app.ai.handlers.knowledge_handler.generate_text")
    @patch("app.ai.query_router.query_decomposer.generate_text")
    @patch("app.ai.handlers.search_handler.retrieve_for_query")
    def test_17_orchestrator_multi_query_multiple_handlers(self, mock_retrieve_sql, mock_decomposer, mock_llm):
        """Multi-query: Sub-query 1 (Knowledge) and Sub-query 2 (Search) are both executed and combined."""
        mock_decomposer.return_value = '{"queries": ["Python là gì?", "Tìm các khóa học về Python"]}'
        mock_retrieve_sql.return_value = {
            "intent": "course_search",
            "found": True,
            "courses": [{"course_id": 1, "title": "Python for Everybody"}],
        }

        # Knowledge handler called twice (once for question, once for search result presentation)
        mock_llm.side_effect = [
            '{"answer": "Python là ngôn ngữ thông dịch phổ biến.", "suggestions": [{"label": "Cơ bản", "prompt": "Cơ bản"}]}',
            '{"answer": "Các khóa học Python gồm: Python for Everybody.", "suggestions": [{"label": "Đăng ký", "prompt": "Đăng ký"}]}',
        ]

        mock_db = MagicMock()
        mock_db.query().filter().order_by().all.return_value = []
        orchestrator = ChatOrchestrator()

        res = orchestrator.process(
            db=mock_db,
            session_id=uuid4(),
            user_content="Python là gì? Ngoài ra tìm giúp tôi các khóa học về Python.",
            allow_sql_retrieval=True,
        )

        self.assertIn("Python là ngôn ngữ", res["answer"])
        self.assertIn("Python for Everybody", res["answer"])
        # Both sub-answers are present in the unified answer separated by delimiter
        self.assertIn("---", res["answer"])
        self.assertGreaterEqual(len(res["suggestions"]), 2)

    @patch("app.ai.handlers.knowledge_handler.generate_text")
    @patch("app.ai.query_router.query_decomposer.generate_text")
    def test_18_orchestrator_multi_query_partial_failure_recovery(self, mock_decomposer, mock_llm):
        """If one sub-query fails, Orchestrator catches it and still preserves the successful sub-query."""
        mock_decomposer.return_value = '{"queries": ["Python là gì?", "Sub-query gây lỗi"]}'
        mock_llm.side_effect = [
            '{"answer": "Python là ngôn ngữ lập trình tuyệt vời.", "suggestions": []}',
            Exception("Simulated API failure on sub-query 2"),
        ]

        mock_db = MagicMock()
        mock_db.query().filter().order_by().all.return_value = []
        orchestrator = ChatOrchestrator()

        res = orchestrator.process(
            db=mock_db,
            session_id=None,
            user_content="Python là gì? Và câu hỏi lỗi",
            allow_sql_retrieval=False,
        )

        # Successful answer is preserved
        self.assertIn("Python là ngôn ngữ lập trình tuyệt vời", res["answer"])

    @patch("app.ai.handlers.search_handler.embedding_service.encode_text")
    @patch("app.ai.handlers.search_handler.qdrant_course_service.search_courses")
    @patch("app.ai.handlers.knowledge_handler.generate_text")
    def test_19_orchestrator_public_chat_allows_qdrant_semantic_search(self, mock_llm, mock_qdrant, mock_encode):
        """Public chat (allow_sql_retrieval=False): skips SQL, executes Qdrant semantic search, does not save to DB."""
        mock_encode.return_value = [0.1] * 384
        hit = MagicMock()
        hit.score = 0.89
        hit.payload = {"course_id": 1, "title": "Public Course in Qdrant", "organization": "Public Org"}
        mock_qdrant.return_value = [hit]
        mock_llm.return_value = '{"answer": "Khóa học tìm thấy từ Qdrant.", "suggestions": []}'

        mock_db = MagicMock()
        orchestrator = ChatOrchestrator()

        res = orchestrator.process(
            db=mock_db,
            session_id=None,  # Public chat
            user_content="Tìm khóa học AI",
            allow_sql_retrieval=False,
        )

        self.assertIn("answer", res)
        # Database add must NOT be called for public chat
        mock_db.add.assert_not_called()
        # Qdrant search was executed
        self.assertTrue(mock_qdrant.called)

    # ==========================================
    # 5. RESPONSE SERVICE (FIX 6)
    # ==========================================

    def test_20_response_service_combine_responses(self):
        """ResponseService.combine_responses synthesizes answers and deduplicates suggestions."""
        sub1 = {
            "answer": "Giải thích Python 3.",
            "suggestions": [{"label": "Học thêm", "prompt": "Học thêm Python"}],
        }
        sub2 = {
            "answer": "Danh sách khóa học Python.",
            "suggestions": [
                {"label": "Học thêm", "prompt": "Học thêm Python"},  # Duplicate prompt
                {"label": "Đăng ký", "prompt": "Đăng ký khóa học"},
            ],
        }
        combined = ResponseService.combine_responses([sub1, sub2])
        self.assertIn("Giải thích Python 3.", combined["answer"])
        self.assertIn("Danh sách khóa học Python.", combined["answer"])
        self.assertIn("---", combined["answer"])
        # Duplicate suggestion prompt removed, length is 2
        self.assertEqual(len(combined["suggestions"]), 2)

    def test_21_response_service_empty_and_fallback(self):
        """ResponseService gracefully handles empty / invalid inputs without crashing."""
        res_empty = ResponseService.format_response({})
        self.assertIn("answer", res_empty)
        self.assertIsInstance(res_empty["suggestions"], list)

        res_none = ResponseService.combine_responses([])
        self.assertIn("answer", res_none)
        self.assertEqual(res_none["suggestions"], [])


if __name__ == "__main__":
    unittest.main()
