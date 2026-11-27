"""Khóa 494 — Introduction to Internet of Things. Đợt 1 (26/11/2026): IoT, Model and Components, Messaging Protocols.
Đợt 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (module 2 "Sensors & Interfaces" của khóa).
Đợt 3 (27/11/2026): Data analysis for IoT, Data Analysis Techniques (module 4 "Data Analysis for IoT").
Soạn: Claude · duyệt: Tuấn. Dựng: python -m scripts.bank.build 494"""

from scripts.bank.courses.course_494.chunks import CHUNKS
from scripts.bank.courses.course_494.essays import ESSAY, GEMINI_PROBES, PROBES
from scripts.bank.courses.course_494.mcq import MCQ
from scripts.bank.courses.course_494.vn_notes import VN_CHUNK, VN_ESSAY, VN_MCQ

COURSE_ID = 494
COURSE_TITLE = "Introduction to Internet of Things"
SKILLS = {"IOT": 1109, "IOTM": 1112, "MSG": 1108, "SENS": 1106, "RO": 1110, "NI": 1113, "DA": 1111, "DAT": 1107}
SKILL_NAMES = {
    "IOT": "Internet of Things (IoT)",
    "IOTM": "Model and Components of IoT",
    "MSG": "Messaging Protocols",
    "SENS": "Sensors",
    "RO": "Sensor Readout",
    "NI": "Readout Non-Idealities",
    "DA": "Data analysis for IoT",
    "DAT": "Data Analysis Techniques",
}
# 7.5b (27/11): câu cùng nhóm không vào cùng một đề. Trắc nghiệm minh họa cùng cách làm với câu tự luận tính toán.
# Rà lộ đáp án đợt 1–2: chờ Tuấn duyệt danh sách cặp rồi bổ sung vào đây.
EXCLUSION = {
    "DAT-TN-08": "dat-linreg-substitute",
    "DAT-TL-05": "dat-linreg-substitute",
}
NOTE = (
    "English bank (drafted by Claude, reviewed by Tuấn). Batch 1 (26/11/2026): IoT, Model and Components of IoT, "
    "Messaging Protocols. Batch 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (course module 2 "
    "'Sensors & Interfaces'). Each skill: 20 questions (14 MCQ = 7 recognize + 7 understand, 6 essays = 4 easy + 2 "
    "advanced) + 3 knowledge chunks. Batch 3 (27/11/2026): Data analysis for IoT, Data Analysis Techniques (course module "
    "4). Content: well-established "
    "IoT basics, MQTT (OASIS standard), CoAP (RFC 7252), introductory sensors and readout electronics. Load "
    "with: python -m app.core.seed_data.seed_review --file data/review/course_494_en.json"
)

__all__ = [
    "CHUNKS",
    "COURSE_ID",
    "COURSE_TITLE",
    "ESSAY",
    "EXCLUSION",
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
