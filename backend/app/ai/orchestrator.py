"""
Orchestrator module for EduMentor AI Chatbot.
Coordinates Query Routing, Search, Knowledge, Code, Reinforcement Handlers,
and Response Service with session state, multi-query aggregation, and history persistence.
"""

import json
import re
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.handlers.code_handler import code_handler
from app.ai.handlers.knowledge_handler import knowledge_handler
from app.ai.handlers.curriculum_handler import course_curriculum_advisor
from app.ai.handlers.recommendation_handler import recommendation_handler
from app.ai.handlers.reinforcement_handler import reinforcement_handler
from app.ai.handlers.search_handler import search_handler
from app.ai.query_router import route_query
from app.ai.query_router.normalizer import is_generic_entity, normalize_text
from app.ai.response_service import response_service
from app.models.chat_message import ChatMessage
from app.services import sql_retrieval


def resolve_numbered_course_reference(user_content: str, history: list, db: Session) -> str | None:
    """
    Nhận diện yêu cầu chọn khóa học theo thứ tự (ví dụ: 'chi tiết khóa học số 4', 'khóa 1', 'thứ 2')
    từ danh sách khóa học được trợ lý đề xuất gần nhất.
    """
    norm = normalize_text(user_content)
    m_num = re.search(r"(?:khoa\s*hoc|khoa|course|mon\s*hoc|mon)?\s*(?:so|thu)\s*([0-9]+)\b", norm)
    if not m_num:
        m_num = re.search(r"\b(?:khoa|course)\s+([0-9]+)\b", norm)
    if not m_num:
        m_num = re.search(r"(?:chi\s*tiet|xem|chon|thong\s*tin)\s+(?:khoa\s*hoc\s+|khoa\s+|course\s+)?(?:so\s*)?([0-9]+)\b", norm)

    word_to_num = {"nhat": 1, "mot": 1, "hai": 2, "nhi": 2, "ba": 3, "bon": 4, "tu": 4, "nam": 5}
    target_idx = None
    if m_num:
        try:
            target_idx = int(m_num.group(1))
        except ValueError:
            pass
    else:
        for w, num_val in word_to_num.items():
            if re.search(rf"(?:khoa\s*hoc|khoa|course)?\s*thu\s*{w}\b", norm):
                target_idx = num_val
                break

    if target_idx is not None and target_idx >= 1 and history:
        for prev_message in reversed(history):
            if prev_message.role == "assistant" and prev_message.content:
                bold_titles = re.findall(r"\*\*([^*]+)\*\*", prev_message.content)
                valid_courses = []
                for cand in bold_titles:
                    cand_clean = cand.strip()
                    if len(cand_clean) > 3 and not any(
                        kw in cand_clean.lower()
                        for kw in ["luu y", "chu y", "tong quan", "goi y", "de xuat", "module", "tuan", "rating", "danh gia", "thong tin"]
                    ):
                        c = sql_retrieval.find_course(db, cand_clean)
                        if c:
                            valid_courses.append(c.title if hasattr(c, "title") else c["title"])
                        else:
                            cands = sql_retrieval.search_courses(db, cand_clean, limit=1)
                            if cands:
                                valid_courses.append(cands[0]["title"])
                if valid_courses and 1 <= target_idx <= len(valid_courses):
                    return valid_courses[target_idx - 1]
    return None


def format_assistant_history(saved_response: dict) -> str:
    """Chuyển phản hồi assistant đã lưu thành văn bản cho history."""
    answer = saved_response.get("answer", "")
    if isinstance(answer, str):
        return answer
    if isinstance(answer, dict):
        history_parts = []
        for field in (
            "concept",
            "real_world_example",
            "code_example",
            "code_explanation",
            "practical_application",
        ):
            value = answer.get(field, "")
            if isinstance(value, str) and value.strip():
                history_parts.append(value.strip())
        return "\n".join(history_parts)
    return str(answer)


class ChatOrchestrator:
    """
    Central coordinator of the EduMentor AI Chatbot.
    Orchestrates:
    User Input -> Query Router -> Handlers (Search, Knowledge, Code, Reinforcement)
    -> Response Service -> Persistence -> Client.
    """

    def __init__(self):
        self.search_handler = search_handler
        self.knowledge_handler = knowledge_handler
        self.code_handler = code_handler
        self.reinforcement_handler = reinforcement_handler
        self.recommendation_handler = recommendation_handler
        self.course_curriculum_advisor = course_curriculum_advisor
        self.response_service = response_service

    def _generate_retrieval_fallback(self, retrieval_context: dict[str, Any], error: Exception) -> str:
        """
        Tạo câu trả lời dự phòng khi LLM gặp lỗi nhưng dữ liệu SQL hoặc Qdrant đã được truy xuất thành công.
        """
        sql_data = retrieval_context.get("sql_data") or {}
        qdrant_data = retrieval_context.get("qdrant_data") or []

        # 0. Nếu có dữ liệu một khóa học cụ thể từ SQL (course_question)
        single_course = sql_data.get("course")
        if single_course and isinstance(single_course, dict):
            title = single_course.get("title", "Khóa học")
            org = single_course.get("organization", "N/A")
            inst = single_course.get("instructor", "N/A")
            rating = single_course.get("rating", "N/A")
            desc = single_course.get("description", "")
            if len(desc) > 300:
                desc = desc[:300] + "..."
            skills = sql_data.get("skills") or []
            skill_names = [s.get("skill") for s in skills if s.get("skill")]
            skills_str = ", ".join(skill_names) if skill_names else "Chưa có kỹ năng liên kết cụ thể"
            lines = [
                f"### Thông tin khóa học: **{title}**",
                f"- **Tổ chức / Giảng viên:** {org} ({inst})",
                f"- **Đánh giá:** {rating}★",
                f"- **Kỹ năng đạt được:** {skills_str}",
                f"- **Mô tả sơ lược:** {desc}",
            ]
            return "\n".join(lines)

        # 1. Nếu có dữ liệu danh sách khóa học từ SQL
        courses = sql_data.get("courses") or []
        if courses and isinstance(courses, list):
            lines = ["Dưới đây là các khóa học phù hợp trong hệ thống:"]
            for c in courses[:5]:
                title = c.get("title", "Khóa học")
                org = c.get("organization", "N/A")
                rating = c.get("rating", "N/A")
                lines.append(f"- **{title}** (Tổ chức: {org}, Đánh giá: {rating}★)")
            return "\n".join(lines)

        # 2. Nếu có dữ liệu kỹ năng từ SQL
        skills = sql_data.get("skills") or []
        if skills and isinstance(skills, list):
            lines = ["Dưới đây là các kỹ năng liên quan trong hệ thống:"]
            for s in skills[:5]:
                skill_name = s.get("skill") or s.get("name") or "Kỹ năng"
                lines.append(f"- **{skill_name}**")
            return "\n".join(lines)

        # 3. Nếu có dữ liệu từ Qdrant
        if qdrant_data and isinstance(qdrant_data, list):
            lines = ["Dưới đây là kết quả tìm kiếm ngữ nghĩa từ hệ thống:"]
            for hit in qdrant_data[:5]:
                content = hit.get("content") or hit.get("title") or hit.get("skill")
                if content:
                    lines.append(f"- {content}")
            return "\n".join(lines)

        return f"*(Hiện tại không thể kết nối đến dịch vụ AI để xử lý câu hỏi: {error})*"

    def process(
        self,
        db: Session,
        session_id: UUID | None,
        user_content: str,
        allow_sql_retrieval: bool = True,
        custom_api_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Xử lý toàn bộ luồng hội thoại của Chatbot, hỗ trợ single-query và multi-query.
        """
        if not isinstance(user_content, str) or not user_content.strip():
            raise ValueError("Message cannot be empty.")

        user_content = user_content.strip()

        # ======================================
        # STEP 1. SAVE USER MESSAGE (IF AUTHENTICATED)
        # ======================================
        if session_id is not None:
            user_msg_record = ChatMessage(
                session_id=session_id,
                role="user",
                content=user_content,
            )
            db.add(user_msg_record)
            db.commit()
        else:
            print("\n========== PUBLIC CHAT ==========")
            print("Không lưu user message vào database.")

        # ======================================
        # STEP 2. GET CONVERSATION HISTORY
        # ======================================
        history: list[ChatMessage] = []
        if session_id is not None:
            history = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(
                    ChatMessage.created_at.asc(),
                    ChatMessage.message_id.asc(),
                )
                .all()
            )

            conversation_lines = []
            for message in history:
                content = message.content
                if message.role == "assistant":
                    try:
                        saved_resp = json.loads(content)
                        if isinstance(saved_resp, dict):
                            content = format_assistant_history(saved_resp)
                    except (json.JSONDecodeError, TypeError):
                        pass

                role_name = "Người dùng" if message.role == "user" else "Gia sư AI"
                conversation_lines.append(f"{role_name}: {content}")
            conversation = "\n".join(conversation_lines)
        else:
            conversation = f"Người dùng: {user_content}"

        # ======================================
        # STEP 3. QUERY ROUTER (PROPAGATE CUSTOM API KEY)
        # ======================================
        route_result = route_query(user_content, custom_api_key=custom_api_key)

        # 0. Check numbered course reference first (ví dụ: "chi tiết khóa học số 4", "khóa 1")
        numbered_course = resolve_numbered_course_reference(user_content, history, db)
        if numbered_course:
            route_result["entity_name"] = numbered_course
            route_result["entity_type"] = "course"
            route_result["intent"] = "course_web_search"
            route_result["task_type"] = "course_web_search"
            route_result["source"] = "conversation_context"
            if route_result.get("sub_queries"):
                route_result["sub_queries"][0]["entity_name"] = numbered_course
                route_result["sub_queries"][0]["entity_type"] = "course"
                route_result["sub_queries"][0]["intent"] = "course_web_search"
                route_result["sub_queries"][0]["task_type"] = "course_web_search"
                route_result["sub_queries"][0]["source"] = "conversation_context"

        # Context inheritance (anaphoric references)
        elif (route_result.get("entity_name") is None or is_generic_entity(str(route_result.get("entity_name")))) and history:
            is_course_query = (
                route_result.get("entity_type") == "course"
                or route_result.get("intent") in (
                    "course_web_search",
                    "course_recommendation",
                    "course_question",
                    "course_review",
                    "course_enrollment_link",
                )
                or any(kw in user_content.lower() for kw in ["khoa hoc", "khoa", "course", "module", "giao trinh"])
            )

            # 1. Nếu là câu hỏi về khóa học, ưu tiên tìm khóa học đã được nhắc tới trong tin nhắn của trợ lý
            if is_course_query:
                for prev_message in reversed(history):
                    if prev_message.role == "assistant" and prev_message.content:
                        try:
                            bold_titles = re.findall(r"\*\*([^*]+)\*\*", prev_message.content)
                            for cand in bold_titles:
                                cand_clean = cand.strip()
                                if len(cand_clean) > 3 and not any(
                                    kw in cand_clean.lower()
                                    for kw in ["luu y", "chu y", "tong quan", "goi y", "de xuat", "module", "tuan", "rating", "danh gia", "thong tin"]
                                ):
                                    found = sql_retrieval.find_course(db, cand_clean)
                                    found_dict = sql_retrieval.course_to_dict(found) if hasattr(found, "course_id") else found
                                    if not found_dict:
                                        cands = sql_retrieval.search_courses(db, cand_clean, limit=1)
                                        if cands:
                                            found_dict = cands[0]
                                    if found_dict:
                                        route_result["entity_name"] = found_dict["title"]
                                        route_result["entity_type"] = "course"
                                        route_result["source"] = "conversation_context"
                                        if route_result.get("sub_queries"):
                                            route_result["sub_queries"][0]["entity_name"] = route_result["entity_name"]
                                            route_result["sub_queries"][0]["entity_type"] = route_result["entity_type"]
                                            route_result["sub_queries"][0]["source"] = "conversation_context"
                                        break
                            if route_result.get("entity_name") and not is_generic_entity(str(route_result.get("entity_name"))):
                                break
                        except Exception:  # noqa: BLE001
                            pass

            # 2. Nếu vẫn chưa có entity, kiểm tra tin nhắn trước của người dùng
            if route_result.get("entity_name") is None or is_generic_entity(str(route_result.get("entity_name"))):
                for prev_message in reversed(history):
                    if prev_message.role == "user" and prev_message.content:
                        try:
                            prev_route = route_query(prev_message.content, custom_api_key=custom_api_key)
                            if prev_route.get("entity_name") and not is_generic_entity(str(prev_route["entity_name"])):
                                route_result["entity_name"] = prev_route["entity_name"]
                                if route_result.get("entity_type") in ("none", None):
                                    route_result["entity_type"] = prev_route.get("entity_type", "skill")
                                route_result["source"] = "conversation_context"
                                if route_result.get("sub_queries"):
                                    route_result["sub_queries"][0]["entity_name"] = route_result["entity_name"]
                                    route_result["sub_queries"][0]["entity_type"] = route_result["entity_type"]
                                    route_result["sub_queries"][0]["source"] = "conversation_context"
                                break
                        except Exception:  # noqa: BLE001
                            pass

        # Điều hướng câu hỏi chi tiết/modules sang course_web_search handler
        if any(kw in user_content.lower() for kw in ["chi tiet", "module", "moudule", "moudle", "giao trinh", "de cuong", "thoi gian hoan thanh"]):
            if route_result.get("entity_type") == "course" or route_result.get("intent") in ("course_question", "general_question"):
                route_result["intent"] = "course_web_search"
                route_result["task_type"] = "course_web_search"
                if route_result.get("sub_queries"):
                    route_result["sub_queries"][0]["intent"] = "course_web_search"
                    route_result["sub_queries"][0]["task_type"] = "course_web_search"

        print("\n========== QUERY ROUTER ==========")
        print(json.dumps(route_result, ensure_ascii=False, indent=2))

        # ======================================
        # STEP 4 & 5. EXECUTION: MULTI-QUERY OR SINGLE-QUERY
        # ======================================
        is_compound = bool(route_result.get("is_compound"))
        sub_queries = route_result.get("sub_queries") or []

        if is_compound and len(sub_queries) > 1:
            print("\n========== PROCESSING MULTI-QUERY ==========")
            sub_responses: list[dict[str, Any]] = []
            previous_entity = route_result.get("entity_name")
            previous_entity_type = route_result.get("entity_type")

            for idx, sub_q in enumerate(sub_queries, start=1):
                sub_query_text = sub_q.get("query", user_content)
                sub_intent = sub_q.get("intent", "general_question")
                sub_task_type = sub_q.get("task_type", "knowledge_question")
                sub_entity_name = sub_q.get("entity_name") or previous_entity
                sub_entity_type = sub_q.get("entity_type") or previous_entity_type

                sub_route = dict(sub_q)
                sub_route["entity_name"] = sub_entity_name
                sub_route["entity_type"] = sub_entity_type

                if sub_entity_name:
                    previous_entity = sub_entity_name
                    previous_entity_type = sub_entity_type

                try:
                    # Retrieve context for sub-query
                    sub_search_res = self.search_handler.handle(
                        db=db,
                        route_result=sub_route,
                        user_content=sub_query_text,
                        allow_sql=allow_sql_retrieval,
                    )
                    sub_context = sub_search_res["retrieval_context"]

                    # Dispatch to appropriate handler
                    if sub_intent == "course_recommendation" or sub_task_type == "course_recommendation":
                        raw_sub = self.recommendation_handler.handle(
                            db=db,
                            user_query=sub_query_text,
                            route_result=sub_route,
                            conversation_history=conversation,
                            custom_api_key=custom_api_key,
                        )
                    elif sub_intent == "course_web_search" or sub_task_type == "course_web_search":
                        raw_sub = self.course_curriculum_advisor.handle(
                            db=db,
                            course_name=sub_route.get("entity_name"),
                            user_query=sub_query_text,
                            organization=sub_route.get("organization"),
                            conversation_history=conversation,
                            custom_api_key=custom_api_key,
                        )
                    elif sub_task_type in ("code_analysis", "code_fix") or sub_intent in (
                        "code_help",
                        "code_analysis",
                        "code_fix",
                    ):
                        raw_sub = self.code_handler.handle(
                            route_result=sub_route,
                            user_content=sub_query_text,
                            conversation_history=conversation,
                            custom_api_key=custom_api_key,
                        )
                    elif sub_task_type in ("reinforcement_request", "skill_review") or sub_intent in (
                        "reinforcement_request",
                        "skill_review",
                    ):
                        raw_sub = self.reinforcement_handler.handle(
                            route_result=sub_route,
                            user_content=sub_query_text,
                            retrieval_context=sub_context,
                            conversation_history=conversation,
                            custom_api_key=custom_api_key,
                        )
                    else:
                        raw_sub = self.knowledge_handler.handle(
                            route_result=sub_route,
                            retrieval_context=sub_context,
                            conversation_history=conversation,
                            custom_api_key=custom_api_key,
                        )

                    formatted_sub = self.response_service.format_response(
                        raw_output=raw_sub,
                        metadata={
                            "sub_query": sub_query_text,
                            "intent": sub_intent,
                            "task_type": sub_task_type,
                        },
                    )
                    sub_responses.append(formatted_sub)

                except Exception as sub_err:  # noqa: BLE001
                    print(f"[ORCHESTRATOR] Sub-query {idx} execution failed: {sub_err}")
                    sub_responses.append(
                        {
                            "answer": f"*(Không thể xử lý yêu cầu: \"{sub_query_text}\")*",
                            "suggestions": [],
                        }
                    )

            response_data = self.response_service.combine_responses(
                sub_responses=sub_responses,
                metadata={
                    "is_compound": True,
                    "sub_queries_count": len(sub_responses),
                    "source": route_result.get("source"),
                },
            )

        else:
            # Single query execution
            search_res = self.search_handler.handle(
                db=db,
                route_result=route_result,
                user_content=user_content,
                allow_sql=allow_sql_retrieval,
            )
            retrieval_context = search_res["retrieval_context"]

            print("\n========== RETRIEVAL CONTEXT ==========")
            print(json.dumps(retrieval_context, ensure_ascii=False, indent=2, default=str))

            task_type = route_result.get("task_type", "knowledge_question")
            intent = route_result.get("intent", "general_question")

            try:
                if intent == "course_recommendation" or task_type == "course_recommendation":
                    print("\n========== ROUTED TO RECOMMENDATION HANDLER ==========")
                    raw_response = self.recommendation_handler.handle(
                        db=db,
                        user_query=user_content,
                        route_result=route_result,
                        conversation_history=conversation,
                        custom_api_key=custom_api_key,
                    )
                elif intent == "course_web_search" or task_type == "course_web_search":
                    print("\n========== ROUTED TO COURSE CURRICULUM ADVISOR (WEB SEARCH) ==========")
                    raw_response = self.course_curriculum_advisor.handle(
                        db=db,
                        course_name=route_result.get("entity_name"),
                        user_query=user_content,
                        organization=route_result.get("organization"),
                        conversation_history=conversation,
                        custom_api_key=custom_api_key,
                    )
                elif task_type in ("code_analysis", "code_fix") or intent in (
                    "code_help",
                    "code_analysis",
                    "code_fix",
                ):
                    print("\n========== ROUTED TO CODE HANDLER ==========")
                    raw_response = self.code_handler.handle(
                        route_result=route_result,
                        user_content=user_content,
                        conversation_history=conversation,
                        custom_api_key=custom_api_key,
                    )
                elif task_type in ("reinforcement_request", "skill_review") or intent in (
                    "reinforcement_request",
                    "skill_review",
                ):
                    print("\n========== ROUTED TO REINFORCEMENT HANDLER ==========")
                    raw_response = self.reinforcement_handler.handle(
                        route_result=route_result,
                        user_content=user_content,
                        retrieval_context=retrieval_context,
                        conversation_history=conversation,
                        custom_api_key=custom_api_key,
                    )
                else:
                    print("\n========== ROUTED TO KNOWLEDGE HANDLER ==========")
                    raw_response = self.knowledge_handler.handle(
                        route_result=route_result,
                        retrieval_context=retrieval_context,
                        conversation_history=conversation,
                        custom_api_key=custom_api_key,
                    )
            except Exception as handler_err:
                print(f"[ORCHESTRATOR] Handler execution error: {handler_err}")
                fallback_answer = self._generate_retrieval_fallback(retrieval_context, handler_err)
                raw_response = {
                    "answer": fallback_answer,
                    "suggestions": [
                        {"label": "Thử lại câu hỏi", "prompt": user_content},
                    ],
                }

            response_data = self.response_service.format_response(
                raw_output=raw_response,
                metadata={
                    "intent": intent,
                    "task_type": task_type,
                    "source": route_result.get("source"),
                },
            )

        # ======================================
        # STEP 6. PERSIST ASSISTANT RESPONSE (AUTHENTICATED ONLY)
        # ======================================
        if session_id is not None:
            db_save_data = {
                "answer": response_data["answer"],
                "suggestions": response_data["suggestions"],
            }
            ai_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=json.dumps(db_save_data, ensure_ascii=False),
            )
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)

        return response_data


orchestrator = ChatOrchestrator()
