"""Khóa 494 — Introduction to Internet of Things. Đợt 1 (26/11/2026): IoT, Model and Components, Messaging Protocols.
Đợt 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (module 2 "Sensors & Interfaces" của khóa).
Soạn: Claude · duyệt: Tuấn. Dựng: python -m scripts.bank.build 494"""

from scripts.bank.courses.course_494.chunks import CHUNKS as CHUNKS_B1
from scripts.bank.courses.course_494.chunks_b2 import CHUNKS_B2
from scripts.bank.courses.course_494.essays import ESSAY as ESSAY_B1
from scripts.bank.courses.course_494.essays import GEMINI_PROBES as GEMINI_PROBES_B1
from scripts.bank.courses.course_494.essays import PROBES as PROBES_B1
from scripts.bank.courses.course_494.essays_b2 import ESSAY_B2, GEMINI_PROBES_B2, PROBES_B2
from scripts.bank.courses.course_494.mcq import MCQ as MCQ_B1
from scripts.bank.courses.course_494.mcq_b2 import MCQ_B2
from scripts.bank.courses.course_494.vn_notes import VN_CHUNK as VN_CHUNK_B1
from scripts.bank.courses.course_494.vn_notes import VN_ESSAY as VN_ESSAY_B1
from scripts.bank.courses.course_494.vn_notes import VN_MCQ as VN_MCQ_B1
from scripts.bank.courses.course_494.vn_notes_b2 import VN_CHUNK_B2, VN_ESSAY_B2, VN_MCQ_B2

# Kỹ năng mới xếp SAU đợt 1 → vị trí đáp án đúng của đợt 1 không đổi khi dựng lại
CHUNKS = CHUNKS_B1 + CHUNKS_B2
MCQ = {**MCQ_B1, **MCQ_B2}
ESSAY = {**ESSAY_B1, **ESSAY_B2}
PROBES = {**PROBES_B1, **PROBES_B2}
GEMINI_PROBES = {**GEMINI_PROBES_B1, **GEMINI_PROBES_B2}
VN_CHUNK = {**VN_CHUNK_B1, **VN_CHUNK_B2}
VN_MCQ = {**VN_MCQ_B1, **VN_MCQ_B2}
VN_ESSAY = {**VN_ESSAY_B1, **VN_ESSAY_B2}

COURSE_ID = 494
COURSE_TITLE = "Introduction to Internet of Things"
SKILLS = {"IOT": 1109, "IOTM": 1112, "MSG": 1108, "SENS": 1106, "RO": 1110, "NI": 1113}
SKILL_NAMES = {
    "IOT": "Internet of Things (IoT)",
    "IOTM": "Model and Components of IoT",
    "MSG": "Messaging Protocols",
    "SENS": "Sensors",
    "RO": "Sensor Readout",
    "NI": "Readout Non-Idealities",
}
NOTE = (
    "English bank (drafted by Claude, reviewed by Tuấn). Batch 1 (26/11/2026): IoT, Model and Components of IoT, "
    "Messaging Protocols. Batch 2 (27/11/2026): Sensors, Sensor Readout, Readout Non-Idealities (course module 2 "
    "'Sensors & Interfaces'). Each skill: 20 questions (14 MCQ = 7 recognize + 7 understand, 6 essays = 4 easy + 2 "
    "advanced) + 3 knowledge chunks. Batch 3: Data analysis for IoT, Data Analysis Techniques. Content: well-established "
    "IoT basics, MQTT (OASIS standard), CoAP (RFC 7252), introductory sensors and readout electronics. Load "
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
