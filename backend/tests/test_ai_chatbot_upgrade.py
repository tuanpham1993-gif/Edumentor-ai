"""
Unit & Integration Tests for Upgraded EduMentor AI Chatbot.
Verifies:
1. Intent Classification for 6 distinct flows (Recommendation, Web Search, Course Search, Skill Search, Code Help, Reinforcement, QA).
2. Course Recommendation logic & candidate course retrieval.
3. Course Web Search strict DB verification & Tavily isolation.
4. Response formatting contract (answer, suggestions).
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import pytest

# Ensure backend path is on sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.ai.query_router import route_query
from app.ai.query_router.config import ALLOWED_INTENTS
from app.ai.handlers.curriculum_handler import CourseCurriculumAdvisor
from app.ai.handlers.recommendation_handler import RecommendationHandler
from app.services.tavily_service import TavilyService


class TestIntentClassification:
    """Kiểm tra phân loại Query Router cho các nghiệp vụ."""

    def test_course_recommendation_beginner(self):
        query = "Tôi mới học lập trình, nên bắt đầu với khóa học nào?"
        result = route_query(query)
        assert result["intent"] == "course_recommendation"
        assert result["task_type"] == "course_recommendation"
        assert "gemini" in result["retrieval_modes"]

    def test_course_recommendation_career_goal(self):
        query = "Tôi muốn trở thành Backend Developer, nên học những khóa học nào?"
        result = route_query(query)
        assert result["intent"] == "course_recommendation"
        assert result["task_type"] == "course_recommendation"

    def test_course_recommendation_next_step(self):
        query = "Tôi đã biết Python, nên học khóa nào tiếp theo?"
        result = route_query(query)
        assert result["intent"] == "course_recommendation"
        assert result["task_type"] == "course_recommendation"

    def test_course_web_search_syllabus(self):
        query = "Giáo trình khóa học Machine Learning của Stanford gồm những gì?"
        result = route_query(query)
        assert result["intent"] == "course_web_search"
        assert result["task_type"] == "course_web_search"
        assert "web" in result["retrieval_modes"]

    def test_course_web_search_modules(self):
        query = "Khóa học Python for Everybody có những module nào?"
        result = route_query(query)
        assert result["intent"] == "course_web_search"
        assert result["task_type"] == "course_web_search"

    def test_course_web_search_lessons(self):
        query = "Lộ trình bài học của khóa học Deep Learning Specialization gồm những tuần nào?"
        result = route_query(query)
        assert result["intent"] == "course_web_search"

    def test_internal_course_search(self):
        query = "Tìm các khóa học về Machine Learning trên EduMentor"
        result = route_query(query)
        assert result["intent"] == "course_search"

    def test_reinforcement_quiz(self):
        query = "Cho mình 3 câu hỏi trắc nghiệm ôn tập về SQL"
        result = route_query(query)
        assert result["intent"] in ("reinforcement_request", "skill_review")

    def test_code_assistance(self):
        query = "Đoạn code sau bị lỗi IndexError, sửa giúp tôi: arr[10]"
        result = route_query(query)
        assert result["intent"] in ("code_fix", "code_help", "code_analysis")

    def test_knowledge_qa(self):
        query = "Giải thích khái niệm Dependency Injection trong FastAPI"
        result = route_query(query)
        assert result["intent"] in ("skill_question", "general_question")


class TestCourseWebSearchStrictConstraint:
    """Kiểm tra điều kiện ngặt nghèo của Web Search."""

    def test_reject_course_not_in_edumentor_db(self):
        """Nếu khóa học không có trong EduMentor DB, tuyệt đối không gọi Tavily."""
        advisor = CourseCurriculumAdvisor()
        mock_db = MagicMock()

        # Giả lập không tìm thấy khóa học trong DB
        with patch("app.ai.handlers.curriculum_handler.sql_retrieval.find_course", return_value=None), \
             patch("app.ai.handlers.curriculum_handler.sql_retrieval.search_courses", return_value=[]), \
             patch("app.ai.handlers.curriculum_handler.tavily_service.search_course_curriculum") as mock_tavily:

            res = advisor.handle(
                db=mock_db,
                course_name="Khoa Hoc Hoan Toan La Khong Co Trong DB 999",
                user_query="Giáo trình khóa Khoa Hoc Hoan Toan La Khong Co Trong DB 999 gồm những gì?",
            )

            # Khẳng định Tavily KHÔNG BAO GIỜ ĐƯỢC GỌI
            mock_tavily.assert_not_called()

            # Khẳng định câu trả lời nêu rõ không có trong hệ thống và hướng dẫn AI Lộ trình
            assert "không tìm thấy khóa học" in res["answer"]
            assert "AI Lộ trình" in res["answer"]
            assert len(res["suggestions"]) >= 1

    def test_leverage_db_modules_when_course_in_db(self):
        """Khi khóa học có trong DB, tận dụng trường modules và chỉ gọi Tavily bổ sung."""
        advisor = CourseCurriculumAdvisor()
        mock_db = MagicMock()

        sample_course = {
            "course_id": 101,
            "title": "Machine Learning Specialization",
            "organization": "Stanford University",
            "instructor": "Andrew Ng",
            "modules": "3 course series",
            "level": "Beginner",
            "rating": 4.9,
            "description": "Foundational course on machine learning algorithms.",
            "url": "https://coursera.org/learn/machine-learning",
        }

        with patch("app.ai.handlers.curriculum_handler.sql_retrieval.find_course", return_value=sample_course), \
             patch("app.ai.handlers.curriculum_handler.tavily_service._api_key", "tvly-test-key"), \
             patch("app.ai.handlers.curriculum_handler.tavily_service.search_course_curriculum") as mock_tavily, \
             patch("app.ai.handlers.curriculum_handler.generate_text", return_value='{"answer": "Giáo trình gồm 3 khóa học...", "suggestions": []}') as mock_llm:

            mock_tavily.return_value = {
                "success": True,
                "results": [{"title": "Course 1: Supervised Learning", "url": "https://stanford.edu", "content": "Week 1: Linear Regression"}],
            }

            res = advisor.handle(
                db=mock_db,
                course_name="Machine Learning Specialization",
                user_query="Giáo trình khóa Machine Learning Specialization gồm những gì?",
                organization="Stanford University",
            )

            # Tavily được gọi chính xác theo tên khóa học và tổ chức trong DB
            mock_tavily.assert_called_once_with(
                course_title="Machine Learning Specialization",
                organization="Stanford University",
                max_results=3,
            )

            # LLM nhận được prompt chứa cả dữ liệu DB (modules_summary) và dữ liệu Tavily
            call_prompt = mock_llm.call_args[0][0]
            assert "Machine Learning Specialization" in call_prompt
            assert "3 course series" in call_prompt
            assert "Week 1: Linear Regression" in call_prompt


class TestCourseRecommender:
    """Kiểm tra luồng Gợi ý khóa học."""

    def test_recommender_uses_candidate_courses_from_db(self):
        recommender = RecommendationHandler()
        mock_db = MagicMock()

        sample_candidates = [
            {"course_id": 1, "title": "Python for Beginners", "level": "Beginner", "organization": "Univ A", "rating": 4.8, "description": "Intro to python"},
            {"course_id": 2, "title": "Advanced Python & FastAPI", "level": "Intermediate", "organization": "Univ B", "rating": 4.9, "description": "Backend dev with FastAPI"},
        ]

        with patch("app.ai.handlers.recommendation_handler.sql_retrieval.search_courses", return_value=sample_candidates), \
             patch("app.ai.handlers.recommendation_handler.qdrant_course_service.search_courses", return_value=[]), \
             patch("app.ai.handlers.recommendation_handler.generate_text", return_value='{"answer": "Đề xuất lộ trình...", "suggestions": []}') as mock_llm:

            recommender.handle(
                db=mock_db,
                user_query="Tôi muốn trở thành Backend Developer, nên học những khóa nào?",
                route_result={"intent": "course_recommendation", "target_role": "Backend Developer", "level": "Beginner"},
            )

            call_prompt = mock_llm.call_args[0][0]
            assert "Python for Beginners" in call_prompt
            assert "Advanced Python & FastAPI" in call_prompt
            assert "Backend Developer" in call_prompt


class TestTavilyService:
    """Kiểm tra Tavily Service."""

    def test_tavily_config_and_url(self):
        service = TavilyService(api_key="tvly-mock-key")
        assert service.is_configured is True

    def test_tavily_unconfigured_graceful_return(self):
        service = TavilyService(api_key="")
        res = service.search_course_curriculum("Python")
        assert res["success"] is False
        assert "not configured" in res["error"]


class TestOrchestratorIntegration:
    """Kiểm tra ChatOrchestrator điều phối và format response chuẩn cho các luồng mới."""

    def test_orchestrator_recommendation_flow(self):
        from app.ai.orchestrator import ChatOrchestrator

        orchestrator = ChatOrchestrator()
        mock_db = MagicMock()

        sample_candidates = [
            {"course_id": 1, "title": "Python Basics", "level": "Beginner", "organization": "Univ A", "rating": 4.8, "description": "Intro"},
        ]

        with patch.object(orchestrator.search_handler, "handle", return_value={"retrieval_context": {}}), \
             patch("app.ai.handlers.recommendation_handler.sql_retrieval.search_courses", return_value=sample_candidates), \
             patch("app.ai.handlers.recommendation_handler.generate_text", return_value='{"answer": "Lộ trình đề xuất: Khóa 1...", "suggestions": [{"label": "Học thử", "prompt": "Chi tiết"}]}') as mock_llm:

            res = orchestrator.process(
                db=mock_db,
                session_id=None,
                user_content="Tôi mới học lập trình, nên bắt đầu với khóa học nào?",
            )

            assert "answer" in res
            assert "suggestions" in res
            assert "Lộ trình đề xuất" in res["answer"]
            assert len(res["suggestions"]) >= 1

    def test_orchestrator_web_search_flow(self):
        from app.ai.orchestrator import ChatOrchestrator

        orchestrator = ChatOrchestrator()
        mock_db = MagicMock()

        sample_course = {
            "course_id": 5,
            "title": "Python for Everybody",
            "organization": "University of Michigan",
            "instructor": "Charles Severance",
            "modules": "5 modules",
            "level": "Beginner",
            "rating": 4.8,
            "description": "Learn to Program and Analyze Data with Python.",
            "url": "https://coursera.org/specializations/python",
        }

        with patch.object(orchestrator.search_handler, "handle", return_value={"retrieval_context": {}}), \
             patch("app.ai.handlers.curriculum_handler.sql_retrieval.find_course", return_value=sample_course), \
             patch("app.ai.handlers.curriculum_handler.tavily_service._api_key", "tvly-test-key"), \
             patch("app.ai.handlers.curriculum_handler.tavily_service.search_course_curriculum", return_value={"success": True, "results": [{"title": "Mod 1", "content": "Variables"}]}), \
             patch("app.ai.handlers.curriculum_handler.generate_text", return_value='{"answer": "Giáo trình gồm 5 modules...", "suggestions": [{"label": "Đăng ký", "prompt": "Link"}]}'):

            res = orchestrator.process(
                db=mock_db,
                session_id=None,
                user_content="Khóa học Python for Everybody có những module nào?",
            )

            assert "answer" in res
            assert "suggestions" in res
            assert "5 modules" in res["answer"]


if __name__ == "__main__":
    print("--- 1. Testing Intent Classification (6 Flows) ---")
    t_intent = TestIntentClassification()
    t_intent.test_course_recommendation_beginner()
    print("  [PASS] test_course_recommendation_beginner")
    t_intent.test_course_recommendation_career_goal()
    print("  [PASS] test_course_recommendation_career_goal")
    t_intent.test_course_recommendation_next_step()
    print("  [PASS] test_course_recommendation_next_step")
    t_intent.test_course_web_search_syllabus()
    print("  [PASS] test_course_web_search_syllabus")
    t_intent.test_course_web_search_modules()
    print("  [PASS] test_course_web_search_modules")
    t_intent.test_course_web_search_lessons()
    print("  [PASS] test_course_web_search_lessons")
    t_intent.test_internal_course_search()
    print("  [PASS] test_internal_course_search")
    t_intent.test_reinforcement_quiz()
    print("  [PASS] test_reinforcement_quiz")
    t_intent.test_code_assistance()
    print("  [PASS] test_code_assistance")
    t_intent.test_knowledge_qa()
    print("  [PASS] test_knowledge_qa")

    print("\n--- 2. Testing Web Search Strict Constraints ---")
    t_web = TestCourseWebSearchStrictConstraint()
    t_web.test_reject_course_not_in_edumentor_db()
    print("  [PASS] test_reject_course_not_in_edumentor_db (Zero Tavily calls when course not in DB)")
    t_web.test_leverage_db_modules_when_course_in_db()
    print("  [PASS] test_leverage_db_modules_when_course_in_db (Tavily called only when course verified in DB)")

    print("\n--- 3. Testing Course Recommender ---")
    t_rec = TestCourseRecommender()
    t_rec.test_recommender_uses_candidate_courses_from_db()
    print("  [PASS] test_recommender_uses_candidate_courses_from_db (Ranks EduMentor DB courses)")

    print("\n--- 4. Testing Tavily Service ---")
    t_tavily = TestTavilyService()
    t_tavily.test_tavily_config_and_url()
    print("  [PASS] test_tavily_config_and_url")
    t_tavily.test_tavily_unconfigured_graceful_return()
    print("  [PASS] test_tavily_unconfigured_graceful_return")

    print("\n--- 5. Testing Orchestrator Integration (Schema & Flow) ---")
    t_orch = TestOrchestratorIntegration()
    t_orch.test_orchestrator_recommendation_flow()
    print("  [PASS] test_orchestrator_recommendation_flow (Response has 'answer' and 'suggestions')")
    t_orch.test_orchestrator_web_search_flow()
    print("  [PASS] test_orchestrator_web_search_flow (Response has 'answer' and 'suggestions')")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<\n")
