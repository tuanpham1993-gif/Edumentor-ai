import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import unittest
from unittest.mock import MagicMock
from uuid import uuid4
from fastapi import HTTPException

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.chat_session import ChatSession
from app.models.user import Users
from app.schemas.chat import ChatSessionUpdate
from app.routers.v1.chat_tutor import update_session, get_owned_session


class TestChatTutorSessionRename(unittest.TestCase):
    def setUp(self):
        self.user = Users(user_id=1, full_name="Student Test", email="student@test.com")
        self.other_user = Users(user_id=2, full_name="Other User", email="other@test.com")
        self.session_id = uuid4()
        self.session = ChatSession(
            session_id=self.session_id,
            user_id=1,
            topic="Phiên học tập mới",
            session_type="tutor",
            status="active",
        )

    def test_get_owned_session_success(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.session

        result = get_owned_session(mock_db, self.session_id, self.user.user_id)
        self.assertEqual(result.session_id, self.session_id)
        self.assertEqual(result.user_id, 1)

    def test_get_owned_session_not_found_raises_404(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            get_owned_session(mock_db, self.session_id, self.other_user.user_id)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Không tìm thấy phiên chat", ctx.exception.detail)

    def test_update_session_rename_success(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.session

        data = ChatSessionUpdate(topic="Lộ trình học Python & AI")
        result = update_session(
            session_id=self.session_id,
            data=data,
            db=mock_db,
            current_user=self.user,
        )

        self.assertEqual(result["session_id"], self.session_id)
        self.assertEqual(result["topic"], "Lộ trình học Python & AI")
        self.assertEqual(self.session.topic, "Lộ trình học Python & AI")
        self.assertTrue(mock_db.commit.called)
        self.assertTrue(mock_db.refresh.called)

    def test_update_session_empty_topic_raises_422(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.session

        data = ChatSessionUpdate(topic="   ")
        with self.assertRaises(HTTPException) as ctx:
            update_session(
                session_id=self.session_id,
                data=data,
                db=mock_db,
                current_user=self.user,
            )
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("không được để trống", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
