"""Khóa 494 — Introduction to Internet of Things. Đợt 1 (26/11/2026): IoT, Model and Components, Messaging Protocols.
Soạn: Claude · duyệt: Tuấn. Dựng: python -m scripts.bank.build 494"""

from scripts.bank.courses.course_494.chunks import CHUNKS
from scripts.bank.courses.course_494.essays import ESSAY, GEMINI_PROBES, PROBES
from scripts.bank.courses.course_494.mcq import MCQ
from scripts.bank.courses.course_494.vn_notes import VN_CHUNK, VN_ESSAY, VN_MCQ

COURSE_ID = 494
COURSE_TITLE = "Introduction to Internet of Things"
SKILLS = {"IOT": 1109, "IOTM": 1112, "MSG": 1108}
SKILL_NAMES = {"IOT": "Internet of Things (IoT)", "IOTM": "Model and Components of IoT", "MSG": "Messaging Protocols"}
NOTE = (
    "English bank (26/11/2026, drafted by Claude, reviewed by Tuấn) — batch 1 of 3: IoT, Model and Components of IoT, "
    "Messaging Protocols; 3 skills x 20 questions (14 MCQ = 7 recognize + 7 understand, 6 essays = 4 easy + 2 advanced) "
    "+ 9 knowledge chunks. Batch 2: Sensors, Sensor Readout, Readout Non-Idealities; batch 3: Data analysis for IoT, "
    "Data Analysis Techniques. Content: well-established IoT basics, MQTT (OASIS standard) and CoAP (RFC 7252). Load "
    "with: python -m app.core.seed_data.seed_review --file data/review/course_494_en.json"
)

__all__ = [
    "CHUNKS",
    "COURSE_ID",
    "COURSE_TITLE",
    "ESSAY",
    "GEMINI_PROBES",
    "MCQ",
    "NOTE",
    "PROBES",
    "SKILLS",
    "SKILL_NAMES",
    "VN_CHUNK",
    "VN_ESSAY",
    "VN_MCQ",
]
